from fastapi import APIRouter, Request
from math import ceil

from traffix.dependencies import RedisDep
from traffix.main import templates
from traffix.menu import sidebar_menu

router = APIRouter()


@router.get("/game_releases")
async def get_game_releases(
    redis: RedisDep, request: Request, limit: int = 25, offset: int = 0
):
    game_releases = await redis.get("event_game_releases")

    total_games = len(game_releases)

    # Calculate pagination
    total_pages = ceil(total_games / limit)
    current_page = offset // limit + 1

    # Calculate slice indices for pagination
    start_idx = offset
    end_idx = min(offset + limit, total_games)

    paginated_game_releases = game_releases[start_idx:end_idx]

    if limit > 0:
        paginated_game_releases = paginated_game_releases[:limit]

    context = {
        "game_releases": paginated_game_releases,
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

    total_games = len(game_updates)

    # Calculate pagination
    total_pages = ceil(total_games / limit)
    current_page = offset // limit + 1

    # Calculate slice indices for pagination
    start_idx = offset
    end_idx = min(offset + limit, total_games)

    paginated_game_updates = game_updates[start_idx:end_idx]

    if limit > 0:
        paginated_game_updates = paginated_game_updates[:limit]

    return templates.TemplateResponse(
        request=request,
        name="pages/game_updates.html",
        context={
            "game_updates": paginated_game_updates,
            "current_page": current_page,
            "total_pages": total_pages,
            "limit": limit,
        },
    )


@router.get("/game_updates")
async def get_game_updates(
    redis: RedisDep, request: Request, limit: int = 25, offset: int = 0
):
    game_updates = await redis.get("event_game_updates")

    total_games = len(game_updates)

    # Calculate pagination
    total_pages = ceil(total_games / limit)
    current_page = offset // limit + 1

    # Calculate slice indices for pagination
    start_idx = offset
    end_idx = min(offset + limit, total_games)

    paginated_game_updates = game_updates[start_idx:end_idx]

    if limit > 0:
        paginated_game_updates = paginated_game_updates[:limit]

    return templates.TemplateResponse(
        request=request,
        name="pages/game_updates.html",
        context={
            "game_updates": paginated_game_updates,
            "current_page": current_page,
            "total_pages": total_pages,
            "limit": limit,
        },
    )
