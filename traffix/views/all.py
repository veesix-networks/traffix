from fastapi import APIRouter, Request
from math import ceil
from datetime import datetime

from traffix.dependencies import RedisDep
from traffix.main import templates
from traffix.menu import sidebar_menu

router = APIRouter()


@router.get("/game_releases")
async def get_game_releases(
    redis: RedisDep, request: Request, limit: int = 25, offset: int = 0
):
    game_releases = await redis.get("event_game_releases")

    today = datetime.today().date()

    filtered_games = [
        game
        for game in game_releases
        if datetime.strptime(game["date"], "%Y-%m-%d %H:%M:%S").date() >= today
    ]

    total_games = len(filtered_games)

    # Calculate pagination
    total_pages = ceil(total_games / limit)
    current_page = offset // limit + 1

    # Calculate slice indices for pagination
    start_idx = offset
    end_idx = min(offset + limit, total_games)

    paginated_game_releases = filtered_games[start_idx:end_idx]

    if limit > 0:
        paginated_game_releases = paginated_game_releases[:limit]

    sorted_game_releases = sorted(paginated_game_releases, key=lambda x: x["date"])

    context = {
        "game_releases": sorted_game_releases,
        "current_page": current_page,
        "total_pages": total_pages,
        "limit": limit,
        "appTopNav": 1,
        "appSidebarHide": 1,
        "sidebar_menu": sidebar_menu,
    }

    return templates.TemplateResponse(
        request=request, name="pages/game_releases_new.html", context=context
    )


@router.get("/game_updates")
async def get_game_updates(
    redis: RedisDep, request: Request, limit: int = 25, offset: int = 0
):
    game_updates = await redis.get("event_game_updates")
    print(game_updates)

    today = datetime.today().date()

    filtered_updates = [
        update
        for update in game_updates
        if datetime.strptime(update["date"], "%Y-%m-%d %H:%M:%S").date() >= today
    ]

    total_updates = len(filtered_updates)

    # Calculate pagination
    total_pages = ceil(total_updates / limit)
    current_page = offset // limit + 1

    # Calculate slice indices for pagination
    start_idx = offset
    end_idx = min(offset + limit, total_updates)

    paginated_game_updates = filtered_updates[start_idx:end_idx]

    if limit > 0:
        paginated_game_updates = paginated_game_updates[:limit]

    sorted_game_updates = sorted(paginated_game_updates, key=lambda x: x["date"])

    context = {
        "game_updates": sorted_game_updates,
        "current_page": current_page,
        "total_pages": total_pages,
        "limit": limit,
        "appTopNav": 1,
        "appSidebarHide": 1,
        "sidebar_menu": sidebar_menu,
    }

    return templates.TemplateResponse(
        request=request, name="pages/game_updates_new.html", context=context
    )
