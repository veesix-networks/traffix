# Future plans is to build a base class for any notifier
# eg. Slack, Discord, Email, Twitter, etc... and implement a generic send_notification() method on all classes.

import asyncio
import json
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aioredis import from_url, Redis
from structlog import get_logger
from slack_sdk.webhook.async_client import AsyncWebhookClient as SlackClient
from slack_sdk.models.blocks import (
    HeaderBlock,
    DividerBlock,
    ContextBlock,
    MarkdownTextObject,
    SectionBlock,
    ButtonElement,
)

from traffix.config import settings
from traffix.models.events import EventGameRelease, EventGameUpdate

logger = get_logger()


async def load_events(
    event_name: str, client: Redis
) -> list[EventGameRelease | EventGameUpdate]:
    data = await client.get(event_name)
    if not data:
        return []

    try:
        data = json.loads(data)
    except Exception as err:
        logger.error(f"Unable to load events due to error: {err}")
        return []

    events = []
    for event in data:
        event_type = event.get("type")
        match event_type:
            case "game_release":
                event = EventGameRelease.model_validate(event)
            case "game_update":
                event = EventGameUpdate.model_validate(event)
            case _:
                continue

        events.append(event)

    return events


async def send_events_slack_released_within_days(
    events: list[EventGameRelease] | list[EventGameUpdate], days: int = 60
) -> None:
    blocks = []
    now = datetime.now()
    interesting_date = now + timedelta(days=days)

    filtered_events = [
        event for event in events if now <= event.date <= interesting_date
    ]

    # Sort events by size in descending order
    sorted_events = sorted(filtered_events, key=lambda event: event.date)

    total_events = 0
    for event in sorted_events:
        logger.info(
            f"Event {event} is scheduled to release within the next {days} days"
        )

        event_block = [
            HeaderBlock(text=event.name),
            SectionBlock(
                text=f"Estimated Size: {event.size}GB\nType: {event.type}",
                accessory=ButtonElement(
                    text=f"Issue #{event.github_issue_id}",
                    url=f"https://github.com/veesix-networks/traffix/issues/{event.github_issue_id}",
                ),
            ),
            ContextBlock(
                elements=[MarkdownTextObject(text=f"Estimated date: {event.date}")]
            ),
            DividerBlock(),
        ]
        total_events += 1

        blocks.extend(event_block)

    if total_events:
        blocks.insert(
            0,
            ContextBlock(
                elements=[
                    MarkdownTextObject(
                        text=f"Here is a summary of all the game releases and updates coming out within the next {days} days."
                    )
                ]
            ),
        )
    else:
        blocks.insert(
            0,
            ContextBlock(
                elements=[
                    MarkdownTextObject(
                        text=f"No game releases or updates are being released that Traffix knows about within the next {days} days."
                    )
                ]
            ),
        )

    client = SlackClient(url=settings.SLACK_WEBHOOK)
    await client.send(blocks=blocks)


async def run_job() -> None:
    logger.info("Checking if any redis keys need to be updated...")

    try:
        client = from_url(str(settings.REDIS))
        await client.ping()
    except Exception as err:
        logger.error(f"Unable to connect to Redis due to: {err}")
        exit()

    events = []

    events.extend(await load_events("event_game_releases", client))
    events.extend(await load_events("event_game_updates", client))

    await send_events_slack_released_within_days(events)


if __name__ == "__main__":
    scheduler = AsyncIOScheduler()

    trigger = CronTrigger(hour=8, minute=30)

    scheduler.add_job(run_job, trigger=trigger, id="notifier")
    scheduler.start()

    if settings.RUN_NOW:
        logger.info("Running Job straight away")
        scheduler.modify_job(job_id="notifier", next_run_time=datetime.now())
        job = scheduler.get_job(job_id="notifier")

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
