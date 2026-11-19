from fastapi import FastAPI , Request , HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
# from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()
templates = Jinja2Templates(directory="src/learn_fastapi/templates")
app.mount("/static", StaticFiles(directory="src/learn_fastapi/static"), name="static")

posts: list[dict] = [
    {
        "id": 1,
        "author": "Swati Gupta",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "September 10, 2001",
    },
    {
        "id": 2,
        "author": "Pratham Kumar Shaw",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "September 24, 2001",
    },
]

@app.get("/",  include_in_schema=False, name="home")
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {"posts": posts, "title": "Home"},)



@app.get("/posts/{id}", include_in_schema=False, name="post_page") 
def post_page(request: Request, id: int):
    post = next((post for post in posts if post["id"] == id), None)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return templates.TemplateResponse(request, "post.html", {"post": post, "title": post["title"]},)


@app.get("/api/posts")
def get_posts():
    return {"data": posts} 


@app.get("/api/posts/{id}")
def get_post(id: int):
    post = next((post for post in posts if post["id"] == id), None)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return {"data": post}


## StarletteHTTPException Handler
@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
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
    )