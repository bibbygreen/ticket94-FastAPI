import random
from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.constants import SeatStatus
from src.models import Order, OrderItem, Seat, SeatingRow
from src.order.schemas import CreateOrderRequest, CreateOrderResponse
from src.tappay.schemas import TapPayCardHolder, TapPayPaymentRequest
from src.tappay.service import process_tappay_payment


def generate_order_number() -> str:
    date_part = datetime.now(tz=UTC).strftime("%Y%m%d")
    random_part = "".join(random.choices("0123456789", k=6))
    return f"ORD{date_part}{random_part}"


async def create_credit_card_order(
    session: AsyncSession, user_id: int, event_id: int, request: CreateOrderRequest
) -> CreateOrderResponse:
    # 1️⃣ 檢查所有座位仍屬於該使用者，且是 RESERVED 狀態
    result = await session.execute(
        select(Seat)
        .options(selectinload(Seat.row).selectinload(SeatingRow.section))
        .where(
            Seat.seat_id.in_(request.seat_ids),
            Seat.user_id == user_id,
            Seat.status == SeatStatus.RESERVED,
        )
    )
    seats = result.scalars().all()

    if len(seats) != len(request.seat_ids):
        raise HTTPException(
            status_code=400, detail="Some seats are not reserved or not belong to user"
        )

    # 2️⃣ 呼叫 Tappay 金流進行付款
    tappay_result = await process_tappay_payment(
        TapPayPaymentRequest(
            prime=request.prime,
            amount=request.amount,
            cardholder=TapPayCardHolder(**request.cardholder.model_dump()),
        )
    )

    if tappay_result.status != 0:
        raise HTTPException(status_code=400, detail=f"付款失敗: {tappay_result.msg}")

    # 3️⃣ 付款成功，建立訂單與訂單明細
    order_number = generate_order_number()
    now = datetime.now(tz=UTC).replace(tzinfo=None)

    new_order = Order(
        user_id=user_id,
        event_id=event_id,
        order_number=order_number,
        payment_method="CREDIT_CARD",
        total_amount=request.amount,
        status="PAID",
        paid_at=now,
    )
    session.add(new_order)
    await session.flush()

    # 4️⃣ 建立 order_items，並將座位轉為 SOLD
    for seat in seats:
        order_item = OrderItem(
            order_id=new_order.order_id,
            ticket_type_id=seat.row.section.ticket_type_id,
            seat_id=seat.seat_id,
            price=request.amount,  # 假設價格前端計算正確傳入
        )
        session.add(order_item)

        seat.status = SeatStatus.SOLD.value
        seat.hold_expires_at = None
        seat.user_id = None

    await session.commit()

    return CreateOrderResponse(
        order_number=order_number, payment_status="SUCCESS", payment_message="付款成功"
    )
