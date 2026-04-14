from fastapi import FastAPI, Request , HTTPException , status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError


app= FastAPI()
templates= Jinja2Templates(directory="templates")

app.mount("/static" ,StaticFiles(directory= "static") , name="static")

posts : list[dict] = [
    
  {
    "id": 1,
    "author": "Aarav Mehta",
    "title": "The Art of Small Steps",
    "content": "Progress is rarely loud. It is built quietly through small, consistent efforts that often go unnoticed.",
    "date_posted": "2026-03-12"
  },
  {
    "id": 2,
    "author": "Diya Sharma",
    "title": "When Ideas Collide",
    "content": "Great innovation often comes from unexpected intersections of different thoughts and perspectives.",
    "date_posted": "2026-01-28"
  },
  {
    "id": 3,
    "author": "Rohan Kapoor",
    "title": "Late Night Thoughts",
    "content": "There is something about silence at night that makes even the simplest questions feel profound.",
    "date_posted": "2026-02-10"
  },
  {
    "id": 4,
    "author": "Ananya Iyer",
    "title": "Learning to Unlearn",
    "content": "Sometimes growth is not about adding more, but about letting go of what no longer serves you.",
    "date_posted": "2026-04-01"
  },
  {
    "id": 5,
    "author": "Kabir Singh",
    "title": "Moments That Matter",
    "content": "In the rush of everyday life, we often miss the quiet moments that truly define our happiness.",
    "date_posted": "2026-03-25"
  }

]

@app.get("/")
def home():
    return {"message": "home"}


@app.get("/api/posts")
def get_posts(request : Request):
    return templates.TemplateResponse(request , "home.html" , {"posts":posts, "title": "Home" } )


@app.get("/post/{post_id}" , include_in_schema=False)
def post_page(request : Request , post_id : int):
     for post in posts:
       if post.get("id")==post_id:
          title= post["title"]
          return templates.TemplateResponse(request , "post.html" , { "post": post , "title": title } )
        
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="post not found")  



@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )
#json response for /api home route
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
        )   
#html response for rest/ handling while accessing posts
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



### RequestValidationError Handler
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        #note - entering status code twice , one is just for returning html response in the context field , the other
        # one at the end actually returns the http response to the browser and letting it know that an error happened
    )