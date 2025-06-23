import httpx

from src.config import settings
from src.tappay.schemas import TapPayPaymentRequest, TapPayPaymentResult


async def process_tappay_payment(request: TapPayPaymentRequest) -> TapPayPaymentResult:
    payload = {
        "prime": request.prime,
        "partner_key": settings.PARTNER_KEY,
        "merchant_id": settings.MERCHANT_ID,
        "details": "Ticketing Payment",
        "amount": request.amount,
        "cardholder": request.cardholder.dict(),
        "remember": False,
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": settings.PARTNER_KEY,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime",
            headers=headers,
            json=payload,
            timeout=15,
        )
        result = response.json()

    return TapPayPaymentResult(status=result["status"], msg=result.get("msg", ""))
