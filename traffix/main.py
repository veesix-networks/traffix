from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json

from traffix.config import settings
from traffix.menu import sidebar_menu
from traffix.dependencies import RedisDep
from traffix.logic import load_latest_events

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
    github_events = await load_latest_events(redis, limit=10)

    context = {
        "appTopNav": 1,
        "appSidebarHide": 1,
        "sidebar_menu": sidebar_menu,
        "top_50_game_releases": top_50_game_releases[:5]
        if top_50_game_releases
        else [],
        "github_events": github_events,
    }

    return templates.TemplateResponse(
        request=request, name="pages/index_new.html", context=context
    )


# Views
from traffix.views.all import router

app.include_router(router)
