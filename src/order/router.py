from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.database import get_db_session
from src.models import User
from src.order.schemas import (
    CreateOrderRequest,
    CreateOrderResponse,
)
from src.order.service import (
    create_credit_card_order,
)

router = APIRouter(
    tags=["order"],
)


@router.post(
    "/orders/{event_id}",
    response_model=CreateOrderResponse,
)
async def _create_credit_card_order(
    event_id: Annotated[int, Path()],
    request: CreateOrderRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        return await create_credit_card_order(
            session=session,
            user_id=current_user.user_id,
            event_id=event_id,
            request=request,
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
