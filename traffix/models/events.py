from typing import Annotated

from pydantic import BaseModel, HttpUrl, Field


class EventGameRelease(BaseModel):
    name: str
    size: Annotated[int, Field(lt=250)]
    source: HttpUrl
