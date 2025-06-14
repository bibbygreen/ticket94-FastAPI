from datetime import date, datetime, time

from pydantic import BaseModel, field_validator


class CreateEventRequestByAdmin(BaseModel):
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

    @field_validator("sale_time", "sale_end_time", mode="before")
    def remove_tz(cls, v):
        return v.replace(tzinfo=None) if hasattr(v, "tzinfo") and v.tzinfo else v
