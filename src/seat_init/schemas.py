from pydantic import BaseModel, Field


class CreateSectionRequest(BaseModel):
    name: str = Field(..., example="VIP區")
    ticket_type_id: int = Field(..., example=1)
    sort_order: int = Field(default=0)


class SeatingRowInitRequest(BaseModel):
    row_name: str = Field(..., example="A")
    seat_count: int = Field(..., example=10)


class InitializeSeatsRequest(BaseModel):
    rows: list[SeatingRowInitRequest]

    model_config = {
        "json_schema_extra": {
            "example": {
                "rows": [
                    {"row_name": "01", "seat_count": 25},
                    {"row_name": "02", "seat_count": 25},
                    {"row_name": "03", "seat_count": 25},
                    {"row_name": "04", "seat_count": 25},
                ]
            }
        }
    }
