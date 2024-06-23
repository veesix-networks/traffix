import os
import requests
from traffix.models.events import BaseEvent, EventGameRelease, EventEnum
from pydantic import ValidationError
import yaml
import logging
import re

logger = logging.getLogger(__name__)

# Configuration
OWNER = "veesix-networks"
REPO = "traffix"
EVENTS = {
    "event_game_release": [],
    "event_game_update": [],
}

COMMUNITY_APPROVAL_TRIGGER = 1
MAX_SIZE_BEFORE_MANUAL_APPROVAL = 250  # 250GB, games are quite big these days...

# GitHub API URL to fetch issues
GITHUB_API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/issues"


# Fetch issues from GitHub
def fetch_issues():
    headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
    all_issues = []

    for label in EVENTS.keys():
        params = {"state": "open", "labels": label}
        response = requests.get(GITHUB_API_URL, headers=headers, params=params)
        response.raise_for_status()
        issues = response.json()

        # Avoid duplicate issues
        issue_ids = {issue["id"] for issue in all_issues}
        for issue in issues:
            if issue["id"] not in issue_ids:
                name = issue.get("title")
                plus_one = issue["reactions"].get("rocket")
                if plus_one < COMMUNITY_APPROVAL_TRIGGER:
                    logger.warning(
                        f"Skipping Issue '{name}' due to low community approval..."
                    )
                    continue

                EVENTS[label].append(issue)
                issue_ids.add(issue["id"])


def validate_event_game_releases() -> list[EventGameRelease]:
    """Processes an event_game_release issue.

    Args:
        issue:      GitHub Issue.
    """
    events = []
    for issue in EVENTS.get("event_game_release"):
        body = issue["body"]
        pattern = r"### (.*?)\n(.*?)(?=\n### |\Z)"
        matches = re.findall(pattern, body, re.DOTALL)
        fields = {match[0].strip().lower(): match[1].strip() for match in matches}
        fields["type"] = EventEnum.game_release
        fields["github_issue_id"] = issue.get("number")

        try:
            event = EventGameRelease.model_validate(fields)
        except ValidationError as err:
            logger.error(
                f"Unable to validate Game Release '{fields.get('name')}'. Due to error:\n{err}"
            )
            continue

        events.append(event)
    return events


def validate_gigabytes(number: str | int) -> int | None:
    if isinstance(number, str):
        try:
            number = int(number)
        except Exception as err:
            logger.error(f"gigabytes field is not formatted properly: {err}")
            return

    if number > MAX_SIZE_BEFORE_MANUAL_APPROVAL:
        return

    return number


# Update YAML file with new issues
def process_events(yaml_file: str, events: list[BaseEvent]):
    # Load existing YAML data
    data = []

    try:
        with open(yaml_file, "r") as file:
            data_loaded: list[BaseEvent] = yaml.safe_load(file)
            if data_loaded:
                data = data_loaded
    except Exception as err:
        logger.error(f"Unable to open YAML file {yaml_file} due to {err}")

    names = [d.get("name") for d in data]
    github_issue_ids = [d.get("github_issue_id") for d in data]

    for event in events:
        if event.name in names or event.github_issue_id in github_issue_ids:
            logger.warning(
                f"Event name and/or github issue ID is already in use: {event.name} ({event.github_issue_id})"
            )
            continue

        data.append(event.model_dump())

    # Save the updated YAML file
    with open(yaml_file, "w") as file:
        yaml.safe_dump(data, file)


def main():
    fetch_issues()

    # Process issues
    game_releases = validate_event_game_releases()

    process_events("datastore/event_game_releases.yml", game_releases)
    print(game_releases)


if __name__ == "__main__":
    main()
