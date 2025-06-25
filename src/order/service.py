import random
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.constants import SeatStatus
from src.models import Order, OrderItem, Seat, SeatingRow, User
from src.order.schemas import (
    CreateOrderRequest,
    CreateOrderResponse,
    GetEventOrderListByAdminQueryParams,
    GetMyOrderListQueryParams,
    MyOrderListItem,
    MyOrderListResponse,
    OrderDetailResponse,
    SeatDetail,
)
from src.schemas import (
    PaginatedDataResponse,
)
from src.tappay.schemas import TapPayCardHolder, TapPayPaymentRequest
from src.tappay.service import process_tappay_payment


def generate_order_number() -> str:
    date_part = datetime.now(tz=UTC).strftime("%Y%m%d")
    random_part = "".join(random.choices("0123456789", k=6))
    return f"ORD{date_part}{random_part}"


async def create_credit_card_order(
    session: AsyncSession, user_id: int, event_id: int, request: CreateOrderRequest
) -> CreateOrderResponse:
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

    tappay_result = await process_tappay_payment(
        TapPayPaymentRequest(
            prime=request.prime,
            amount=request.amount,
            cardholder=TapPayCardHolder(**request.cardholder.model_dump()),
        )
    )

    if tappay_result.status != 0:
        raise HTTPException(status_code=400, detail=f"付款失敗: {tappay_result.msg}")

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

    for seat in seats:
        order_item = OrderItem(
            order_id=new_order.order_id,
            ticket_type_id=seat.row.section.ticket_type_id,
            seat_id=seat.seat_id,
            price=request.amount,
        )
        session.add(order_item)

        seat.status = SeatStatus.SOLD.value
        seat.hold_expires_at = None
        seat.user_id = None

    await session.commit()

    return CreateOrderResponse(
        order_number=order_number, payment_status="SUCCESS", payment_message="付款成功"
    )


async def get_my_orders(
    query_params: GetMyOrderListQueryParams,
    session: AsyncSession,
    current_user: User,
) -> PaginatedDataResponse[MyOrderListResponse]:
    try:
        page = query_params.page
        page_size = query_params.page_size
        order_by = query_params.order_by

        valid_sort_fields = {"created_at", "updated_at"}
        if query_params.sort_by not in valid_sort_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort_by field: {query_params.sort_by}",
            )

        sort_column = getattr(Order, query_params.sort_by)
        order_expression = asc if order_by == "asc" else desc
        offset = (page - 1) * page_size

        count_stmt = select(func.count()).select_from(Order)
        total_count_result = await session.execute(count_stmt)
        total_count = total_count_result.scalar_one()

        result = await session.execute(
            select(Order)
            .where(Order.user_id == current_user.user_id)
            .order_by(order_expression(sort_column))
            .offset(offset)
            .limit(page_size)
        )
        orders = result.scalars().all()

        response_orders = [
            MyOrderListItem(
                order_number=order.order_number,
                status=order.status,
                total_amount=order.total_amount,
                paid_at=order.paid_at,
            )
            for order in orders
        ]
        total_pages = (total_count + page_size - 1) // page_size

        return PaginatedDataResponse[MyOrderListItem](
            total_count=total_count,
            total_pages=total_pages,
            current_page=page,
            data=response_orders,
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


async def get_order_detail(
    order_number: str,
    session: AsyncSession,
    current_user: User,
):
    try:
        result = await session.execute(
            select(Order).where(
                Order.order_number == order_number,
                Order.user_id == current_user.user_id,
            )
        )
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        result_items = await session.execute(
            select(OrderItem)
            .options(
                selectinload(OrderItem.seat).selectinload(Seat.row).selectinload(SeatingRow.section)
            )
            .where(OrderItem.order_id == order.order_id)
        )

        order_items = result_items.scalars().all()

        seats = []

        for item in order_items:
            if item.seat:
                seats.append(
                    SeatDetail(
                        section_name=item.seat.row.section.name,
                        row_name=item.seat.row.row_name,
                        seat_number=item.seat.seat_number,
                    )
                )

        return OrderDetailResponse(
            order_number=order.order_number,
            status=order.status,
            payment_method=order.payment_method,
            total_amount=order.total_amount,
            paid_at=order.paid_at,
            seats=seats,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


async def get_event_orders_by_admin(
    event_id: int,
    query_params: GetEventOrderListByAdminQueryParams,
    session: AsyncSession,
    current_user: User,
) -> PaginatedDataResponse[MyOrderListItem]:
    try:
        page = query_params.page
        page_size = query_params.page_size
        order_by = query_params.order_by

        valid_sort_fields = {"created_at", "updated_at"}
        if query_params.sort_by not in valid_sort_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort_by field: {query_params.sort_by}",
            )

        sort_column = getattr(Order, query_params.sort_by)
        order_expression = asc if order_by == "asc" else desc

        filters = [Order.event_id == event_id]

        if query_params.order_number:
            filters.append(Order.order_number == query_params.order_number)

        if query_params.status:
            filters.append(Order.status == query_params.status)

        offset = (page - 1) * page_size
        count_stmt = select(func.count()).select_from(Order).where(*filters)
        total_count_result = await session.execute(count_stmt)
        total_count = total_count_result.scalar_one()

        result = await session.execute(
            select(Order)
            .where(*filters)
            .order_by(order_expression(sort_column))
            .offset(offset)
            .limit(page_size)
        )
        orders = result.scalars().all()

        response_orders = [
            MyOrderListItem(
                order_number=order.order_number,
                status=order.status,
                total_amount=order.total_amount,
                paid_at=order.paid_at,
            )
            for order in orders
        ]
        total_pages = (total_count + page_size - 1) // page_size

        return PaginatedDataResponse[MyOrderListItem](
            total_count=total_count,
            total_pages=total_pages,
            current_page=page,
            data=response_orders,
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
