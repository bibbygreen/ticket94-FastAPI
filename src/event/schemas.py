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
    picture_url: str

    @field_validator("sale_time", "sale_end_time", mode="before")
    def remove_tz(cls, v):
        return v.replace(tzinfo=None) if hasattr(v, "tzinfo") and v.tzinfo else v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "event_name": "2025 五月天巡迴演唱會",
                    "description": "五月天全新巡演，感動再升級！",
                    "event_date": "2025-08-20",
                    "event_time": "19:30:00",
                    "sale_time": "2025-07-01T10:00:00+08:00",
                    "sale_end_time": "2025-08-19T23:59:00+08:00",
                    "location": "台北小巨蛋",
                    "address": "台北市松山區南京東路四段2號",
                    "organizer": "相信音樂",
                    "category": "演唱會",
                    "on_sale": True,
                    "picture_url": "https://reurl.cc/AMV85",
                }
            ]
        },
    }


class GetEventDetailByIdResponse(BaseModel):
    event_id: int
    event_name: str
    description: str
    event_date: date
    event_time: time
    sale_time: datetime
    sale_end_time: datetime
    location: str
    address: str
    organizer: str
    on_sale: bool
    category: str
    picture_url: str
