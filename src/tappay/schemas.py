from pydantic import BaseModel


class TapPayCardHolder(BaseModel):
    name: str
    email: str
    phone_number: str


class TapPayPaymentRequest(BaseModel):
    prime: str
    amount: int
    cardholder: TapPayCardHolder


class TapPayPaymentResult(BaseModel):
    status: int
    msg: str
