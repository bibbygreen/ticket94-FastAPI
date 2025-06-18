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
