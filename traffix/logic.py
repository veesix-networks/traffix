from datetime import datetime, timedelta
from dateutil.parser import parse

from aioredis import Redis
from structlog import get_logger

from traffix.models.events import GitHubEvent

logger = get_logger()


def make_date_human_readable(date: datetime | str) -> str:
    """Makes a date human readable from a UI perspective.

    Args:
        date:   datetime object.

    The idea of this function is to:
        - datetime < 1hr readable as eg. "23 mins ago"
        - datetime < 24hrs readable as  eg. "6 hours ago"
        - datetime < 30 days readable as eg. "23 days ago"
        - datetime < 12 months readable as eg. "7 months ago"
        - datetime > 12 months readable as eg. "1 year ago" or "2 years ago"
    """
    if isinstance(date, str):
        date = parse(date)

    now = datetime.now(date.tzinfo)
    diff = now - date

    if diff < timedelta(minutes=1):
        return "just now"
    elif diff < timedelta(hours=1):
        minutes = diff.seconds // 60
        return f"{minutes} mins ago"
    elif diff < timedelta(days=1):
        hours = diff.seconds // 3600
        return f"{hours} hours ago"
    elif diff < timedelta(days=30):
        days = diff.days
        return f"{days} days ago"
    elif diff < timedelta(days=365):
        months = diff.days // 30
        return f"{months} months ago"
    else:
        years = diff.days // 365
        return f"{years} years ago"


async def load_latest_events(client: Redis, limit: int = 0) -> list[GitHubEvent]:
    github_events = await client.get("github_events")

    events = []
    for event in github_events:
        try:
            event_type, title = event["title"].split(":", 1)
        except Exception as err:
            logger.warning(f"Unable to load an event due to: {err}")

        event_type_stripped = (
            str(event_type).replace("[", "", 1).replace("]", "", 1).lower()
        )
        events.append(
            GitHubEvent(
                id=event["number"],
                title=title,
                type=event_type_stripped,
                user=event["user"]["login"],
                created_at=event["created_at"],
                created_at_human_readable=make_date_human_readable(event["created_at"]),
                updated_at=event["updated_at"],
                closed_at=event["closed_at"],
            )
        )

    if limit:
        if len(events) < limit:
            return events
        else:
            return events[:limit]
    return events
