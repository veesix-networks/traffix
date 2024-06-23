from fastapi import APIRouter, Request
from math import ceil

from traffix.dependencies import RedisDep
from traffix.main import templates

router = APIRouter()


@router.get("/game_releases")
async def get_game_releases(
    redis: RedisDep, request: Request, limit: int = 25, offset: int = 0
):
    game_releases = await redis.get("event_game_releases")

    total_games = len(game_releases)
    max_per_page = 5 * 5  # 5 cards per row, up to 5 rows

    # Calculate pagination
    total_pages = ceil(total_games / max_per_page)
    current_page = offset // max_per_page + 1

    # Calculate slice indices for pagination
    start_idx = offset
    end_idx = min(offset + limit, total_games)

    paginated_game_releases = game_releases[start_idx:end_idx]

    if limit > 0:
        paginated_game_releases = paginated_game_releases[:limit]

    return templates.TemplateResponse(
        request=request,
        name="pages/game_releases.html",
        context={
            "game_releases": paginated_game_releases,
            "current_page": current_page,
            "total_pages": total_pages,
            "max_per_page": max_per_page,  # Ensure max_per_page is included in the context
            "limit": limit,
        },  # Optional: include limit if it's needed in the template
    )
