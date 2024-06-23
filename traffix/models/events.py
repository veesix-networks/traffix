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
    size: Annotated[int, Field(lt=250)]
    source: str
    image: Annotated[str, Field(max_length=256)]


class EventGameUpdate(BaseEvent):
    version: str
    size: Annotated[int, Field(lt=250)]
    source: str
