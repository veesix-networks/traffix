import asyncio
import json
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aioredis import from_url, Redis
from structlog import get_logger
import aiohttp
import yaml

from traffix.config import settings
from traffix.models.events import BaseEvent

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


async def update_event_list_redis(datastore_file: str, redis_client: Redis) -> None:
    key_normalized = (
        datastore_file.split(".")[0].lower().replace("-", "_").replace(" ", "_")
    )

    logger.info(f"Validating and checking: '{key_normalized}'")
    file_sha = await fetch_latest_commit_sha(datastore_file)

    redis_event_sha = await redis_client.get(f"{key_normalized}_sha")
    # if redis_event_sha:
    #    redis_event_sha = redis_event_sha.decode("utf-8")
    #    if redis_event_sha == file_sha:
    #        logger.info("Commit SHA is the same, skipping sync for these events...")
    #        return

    events = await fetch_yaml_from_github(datastore_file)
    total_events = len(events)
    await redis_client.set(f"{key_normalized}_sha", file_sha)
    await redis_client.set(key_normalized, json.dumps(events, default=str))
    await redis_client.set(f"{key_normalized}_len", total_events)

    logger.info(f"Updated {key_normalized}")


async def run_job():
    logger.info("Checking if any redis keys need to be updated...")

    try:
        client = from_url(str(settings.REDIS))
        await client.ping()
    except Exception as err:
        logger.error(f"Unable to connect to Redis due to: {err}")
        return

    await update_event_list_redis(settings.EVENT_GAME_RELEASES_YAML, client)


if __name__ == "__main__":
    scheduler = AsyncIOScheduler()

    trigger = CronTrigger(minute=10)

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
