from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from traffix.config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=("POST", "GET", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)

app.mount("/static", StaticFiles(directory="traffix/ui/static"), name="static")
templates = Jinja2Templates(directory="traffix/ui/templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="pages/index.html")


# Views
from traffix.views.all import router

app.include_router(router)
