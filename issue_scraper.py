import os
import requests
from traffix.models.events import EventGameRelease
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


def validate_event_game_releases() -> None:
    """Processes an event_game_release issue.

    Args:
        issue:      GitHub Issue.
    """
    for issue in EVENTS.get("event_game_release"):
        body = issue["body"]
        pattern = r"### (.*?)\n(.*?)(?=\n### |\Z)"
        matches = re.findall(pattern, body, re.DOTALL)

        fields = {match[0].strip().lower(): match[1].strip() for match in matches}
        try:
            print(fields)
            event = EventGameRelease.model_validate(fields)
        except ValidationError:
            logger.error(f"Unable to validate Game Release '{fields.get('name')}'.")
            continue

        print(event)


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


"""
# Update YAML file with new issues
def update_yaml_file(issues):
    # Load existing YAML data
    # with open(YAML_FILE, "r") as file:
    #    data = yaml.safe_load(file)

    # Update data with new issues
    for issue in issues:
        # Extract relevant data from the issue
        print(json.dumps(issue, indent=4))
        # issue_data = {
        #    "title": issue["title"],
        #    "url": issue["html_url"],
        #    "created_at": issue["created_at"],
        # }
        # data["issues"].append(issue_data)

    # Save the updated YAML file
    # with open(YAML_FILE, "w") as file:
    #    yaml.safe_dump(data, file)
"""


def main():
    fetch_issues()

    # Process issues
    validate_event_game_releases()


if __name__ == "__main__":
    main()
