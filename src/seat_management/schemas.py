from pydantic import BaseModel


class SeatStatusResponse(BaseModel):
    seat_id: int
    seat_number: str
    status: str


class RowSeatResponse(BaseModel):
    row_name: str
    seats: list[SeatStatusResponse]


class SectionSeatMapResponse(BaseModel):
    section_id: int
    rows: list[RowSeatResponse]
