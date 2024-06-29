from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict


class EventEnum(str, Enum):
    game_release = "game_release"
    game_update = "game_update"


class BaseEvent(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    name: str
    github_issue_id: int
    type: EventEnum
    date: datetime


class EventGameRelease(BaseEvent):
    size: Annotated[int, Field(lt=500)]
    source: str
    image: Annotated[str, Field(max_length=256)]


class EventGameUpdate(BaseEvent):
    version: str
    size: Annotated[int, Field(lt=500)]
    source: str


class GitHubEventUIEnum(str, Enum):
    game_release = "Release"
    game_update = "Update"


class GitHubEvent(BaseModel):
    id: int
    title: str
    type: EventEnum
    user: str
    created_at: datetime
    created_at_human_readable: str
    updated_at: datetime | None = None
    closed_at: datetime | None = None
