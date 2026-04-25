from fastapi import FastAPI, Request , HTTPException , status , Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from schemas import PostCreate , PostResponse , UserCreate
import models
from database import Base,engine,get_db ,SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session

#creates db tables at app startup
Base.metadata.create_all(bind=engine)

app= FastAPI()
templates= Jinja2Templates(directory="templates")

app.mount("/static" ,StaticFiles(directory= "static") , name="static")

app.mount("/media" , StaticFiles(directory="media") , name="media")



#api endpoints
@app.get("/")
def home():
    return {"message": "home"}

#get all posts 
@app.get("/api/posts" , response_model=list[PostResponse])
def get_posts(request : Request , db:Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return templates.TemplateResponse(request , "home.html", {"posts" : posts , "title": "Home"} )

#create a post
@app.post("/api/posts")
def post_create(new_post: PostCreate, db:Session=Depends(get_db)):
    post_data= models.Post(title= new_post.title , content =new_post.content ,user_id= new_post.user_id)
    db.add(post_data)
    db.commit()
    db.refresh(post_data)
    return post_data


#look at a single post on a different page 
@app.get("/post/{post_id}")
def get_post(post_id:int , request: Request,db:Session= Depends(get_db)):
    post = db.query(models.Post).where(models.Post.id==post_id).first()
    if post:
      title= post.title[:50]
      return templates.TemplateResponse(request , "post.html",{"post" :post , "title": title})
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="post not found")

#create a user
@app.post("/api/users")
def create_user(usercreate: UserCreate , db:Session = Depends(get_db)):
    username = db.query(models.User).where(models.User.username==usercreate.username).first()
    email = db.query(models.User).where(models.User.email==usercreate.email).first()

    if username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="username already exists")
    if email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= "email already registered")
    user_data= models.User(username=usercreate.username , email= usercreate.email )   
    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    return user_data

#get user
@app.get("/api/users/{user_id}")
def get_user(user_id : int, db:Session= Depends(get_db)):
    user= db.query(models.User).where(models.User.id==user_id).first()
    if user:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail = "user not found")

@app.get("/api/users/{user_id}/posts")
def get_user_posts(user_id: int , db:Session= Depends(get_db)):
    posts    





#exception/error handling
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

