from datetime import datetime

from pydantic import BaseModel


class CardHolder(BaseModel):
    name: str
    email: str
    phone_number: str


class CreateOrderRequest(BaseModel):
    seat_ids: list[int]
    amount: float
    prime: str
    cardholder: CardHolder

    model_config = {
        "json_schema_extra": {
            "example": {
                "seat_ids": [1, 2, 3],
                "amount": 100,
                "prime": "test_3a2fb2b7e892b914a03c95dd4dd5dc7970c908df67a49527c0a648b2bc9",
                "cardholder": {
                    "name": "test_name",
                    "email": "test_email",
                    "phone_number": "test_phone_number",
                },
            }
        }
    }


class CreateOrderResponse(BaseModel):
    order_number: str
    payment_status: str
    payment_message: str


class MyOrderListItem(BaseModel):
    order_number: str
    status: str
    total_amount: float
    paid_at: datetime | None


class MyOrderListResponse(BaseModel):
    orders: list[MyOrderListItem]

    model_config = {
        "json_schema_extra": {
            "example": {
                "orders": [
                    {
                        "order_number": "test_order_number",
                        "status": "test_status",
                        "total_amount": 100,
                        "paid_at": "2023-01-01T00:00:00",
                    }
                ]
            }
        }
    }


class SeatDetail(BaseModel):
    section_name: str
    row_name: str
    seat_number: str


class OrderDetailResponse(BaseModel):
    order_number: str
    status: str
    total_amount: float
    payment_method: str
    paid_at: datetime | None
    seats: list[SeatDetail]
