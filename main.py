from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

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
    return {"message": "hello"}


@app.get("/api/posts")
def get_posts(request : Request):
    return templates.TemplateResponse(request , "home.html" , {"posts":posts, "title": "Home" } )
