from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from traffix.config import settings
from traffix.menu import sidebar_menu
from traffix.fake_data import FAKE_TOP_EVENTS
from traffix.dependencies import RedisDep

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


@app.get("/old")
async def old(request: Request):
    return templates.TemplateResponse(request=request, name="pages/index.html")


@app.get("/")
async def home(request: Request, redis: RedisDep):
    top_50_game_releases = await redis.get("top_50_game_release")

    context = {
        "appTopNav": 1,
        "appSidebarHide": 1,
        "sidebar_menu": sidebar_menu,
        "fake_data": FAKE_TOP_EVENTS,
        "top_50_game_releases": top_50_game_releases[:5]
        if top_50_game_releases
        else [],
    }

    return templates.TemplateResponse(
        request=request, name="pages/index_new.html", context=context
    )


# Views
from traffix.views.all import router

app.include_router(router)
