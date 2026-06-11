from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
    )
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select,func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.exceptions import HTTPException as StarletteHTTPException
import models
from database import engine, get_db
from routers import posts, users, comments, likes
from config import settings
from fastapi import WebSocket, WebSocketDisconnect
from websocket_manager import manager ,notification_manager
from auth import verify_access_token
from sqlalchemy import text

@asynccontextmanager
async def lifespan(_app: FastAPI):
   
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])
app.include_router(comments.router, prefix="/api/posts", tags=["comments"])
app.include_router(likes.router, prefix="/api", tags=["likes"])



@app.get("/health")
async def health_check(db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        print(exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc
    return {"status": "healthy"}


@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
async def home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    count_result = await db.execute(select(func.count()).select_from(models.Post))
    total = count_result.scalar() or 0

    result = await db.execute(
    select(models.Post)
    .options(
        selectinload(models.Post.author),
        selectinload(models.Post.comments),
    )
    .order_by(models.Post.date_posted.desc())
    .limit(settings.posts_per_page),
     )
    posts = result.scalars().all()

    has_more = len(posts) < total

    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "posts": posts,
            "title": "Home",
            "limit": settings.posts_per_page,
            "has_more": has_more,
        },
    )



@app.get("/posts/{post_id}", include_in_schema=False)
async def post_page(
    request: Request,
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id == post_id),
    )
    post = result.scalars().first()
    if post:
        title = post.title[:50]
        return templates.TemplateResponse(
            request,
            "post.html",
            {"post": post, "title": title},
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


## user_posts_page route - paginated
@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
async def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    count_result = await db.execute(
        select(func.count())
        .select_from(models.Post)
        .where(models.Post.user_id == user_id),
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.user_id == user_id)
        .order_by(models.Post.date_posted.desc())
        .limit(settings.posts_per_page),
    )
    posts = result.scalars().all()

    has_more = len(posts) < total

    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {
            "posts": posts,
            "user": user,
            "title": f"{user.username}'s Posts",
            "limit": settings.posts_per_page,
            "has_more": has_more,
        },
    )


## login and register template_routes
@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"title": "Login"},
    )

@app.get("/register", include_in_schema=False)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request,
        "register.html",
        {"title": "Register"},
    )

@app.get("/account", include_in_schema=False)
async def account_page(request: Request):
    return templates.TemplateResponse(
        request,
        "account.html",
        {"title": "Account"},
    )


@app.get("/forgot-password", include_in_schema=False)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse(
        request,
        "forgot_password.html",
        {"title": "Forgot Password"},
    )


@app.get("/reset-password", include_in_schema=False)
async def reset_password_page(request: Request):
    response = templates.TemplateResponse(
        request,
        "reset_password.html",
        {"title": "Reset Password"},
    )
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(
    request: Request,
    exception: StarletteHTTPException,
):
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception)

    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exception: RequestValidationError,
):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exception)

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )


##broadcast 
@app.websocket("/ws/posts/{post_id}/comments")
async def comments_ws(websocket: WebSocket, post_id: int):
    """
    Clients connect here to receive live comment events for a given post.
    The endpoint itself never receives messages from the client — it only
    pushes broadcasts that originate from REST mutations.
    """
    await manager.connect(post_id, websocket)
    try:
        while True:
            # Keep the connection alive; we don't process client messages.
            # recv() will raise WebSocketDisconnect when the client leaves.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(post_id, websocket)
 
 
#for notif system -unicast 
@app.websocket("/ws/notifications")
async def notifications_ws(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    user_id = verify_access_token(token)
    if not user_id:
        await websocket.close(code=1008)
        return

    await notification_manager.connect(int(user_id), websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        notification_manager.disconnect(int(user_id), websocket)


## Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Frame-Options"] = "SAMEORIGIN"

    response.headers["X-Content-Type-Options"] = "nosniff"

    if "Referrer-Policy" not in response.headers:
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    if request.url.hostname not in ("localhost", "127.0.0.1"):
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains"
        )

    return response
