import asyncio
import json
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from aioredis import from_url, Redis
from structlog import get_logger
import aiohttp
import yaml

from traffix.config import settings
from traffix.models.events import (
    BaseEvent,
    EventGameRelease,
    EventGameUpdate,
    EventEnum,
)

logger = get_logger()


async def fetch_latest_commit_sha(yaml_file: str) -> str:
    url = f"https://api.github.com/repos/{settings.GITHUB_REPO}/commits?path=datastore/{yaml_file}&per_page=1"
    headers = {"Accept": "application/vnd.github.v3+json"}

    file_commit_sha = None

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                if not data or not data[0]:
                    return
                file_commit_sha = data[0].get(
                    "sha"
                )  # Get the SHA of the latest commit for this file
            else:
                response.raise_for_status()
    return file_commit_sha


async def fetch_yaml_from_github(yaml_file: str) -> str:
    url = f"https://raw.githubusercontent.com/{settings.GITHUB_REPO}/main/datastore/{yaml_file}"

    data = None
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = yaml.safe_load(await response.text())
            else:
                response.raise_for_status()

    return data


async def update_event_list_redis(
    client: Redis, datastore_file: str
) -> list[BaseEvent | EventGameRelease | EventGameUpdate]:
    key_normalized = (
        datastore_file.split(".")[0].lower().replace("-", "_").replace(" ", "_")
    )

    logger.info(f"Validating and checking: '{key_normalized}'")
    file_sha = await fetch_latest_commit_sha(datastore_file)

    # redis_event_sha = await client.get(f"{key_normalized}_sha")
    # if redis_event_sha:
    #    redis_event_sha = redis_event_sha.decode("utf-8")
    #    if redis_event_sha == file_sha:
    #        logger.info("Commit SHA is the same, skipping sync for these events...")
    #        return

    events = await fetch_yaml_from_github(datastore_file)
    total_events = len(events)
    await client.set(f"{key_normalized}_sha", file_sha)
    await client.set(key_normalized, json.dumps(events, default=str))
    await client.set(f"{key_normalized}_len", total_events)

    logger.info(f"Updated {key_normalized}")
    return events


async def update_latest_50_event_list_redis(
    client: Redis, events: list[BaseEvent], event_type: EventEnum
) -> None:
    """Updates Redis with the latest 50 events coming out based on the provided events.

    Args:
        client:         Redis client.
        events:         List of events.
        event_type:     EventEnum.
    """
    if not events:
        return

    if not isinstance(event_type, EventEnum):
        logger.warning(f"'{event_type}' is not a valid event type")
        return

    now = datetime.now()

    filtered_objects = [obj for obj in events if obj["date"] >= now]

    # Sort filtered objects by datetime in ascending order
    sorted_objects = sorted(filtered_objects, key=lambda obj: obj["date"])

    # Retrieve top 50 items
    top_50_events = sorted_objects[:50]
    await client.set(
        f"top_50_{event_type.value}", json.dumps(top_50_events, default=str)
    )
    return top_50_events


async def run_job():
    logger.info("Checking if any redis keys need to be updated...")

    try:
        client = from_url(str(settings.REDIS))
        await client.ping()
    except Exception as err:
        logger.error(f"Unable to connect to Redis due to: {err}")
        exit()

    game_releases = await update_event_list_redis(
        client, settings.EVENT_GAME_RELEASES_YAML
    )
    game_updates = await update_event_list_redis(
        client, settings.EVENT_GAME_UPDATES_YAML
    )

    print(game_releases)
    # Set top 50 for various redis queues
    await update_latest_50_event_list_redis(
        client, game_releases, EventEnum.game_release
    )
    await update_latest_50_event_list_redis(client, game_updates, EventEnum.game_update)


if __name__ == "__main__":
    scheduler = AsyncIOScheduler()

    trigger = IntervalTrigger(minutes=10)

    scheduler.add_job(run_job, trigger=trigger, id="sync_datastore")
    scheduler.start()

    if settings.RUN_NOW:
        logger.info("Running Job straight away")
        scheduler.modify_job(job_id="sync_datastore", next_run_time=datetime.now())
        job = scheduler.get_job(job_id="sync_datastore")

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
