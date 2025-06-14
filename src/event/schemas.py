from typing import Annotated, Literal
from datetime import date, datetime, time

from fastapi import Query
from pydantic import BaseModel

from src.schemas import BasicQueryParams


class CreateEventRequest(BaseModel):
    event_name: str
    description: str
    event_date: date
    event_time: time
    sale_time: datetime
    sale_end_time: datetime
    location: str
    address: str
    organizer: str
    category: str
    on_sale: bool
