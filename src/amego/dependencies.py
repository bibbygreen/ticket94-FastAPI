from functools import lru_cache

from src.amego.invoice import InvoiceAPIClient
from src.config import settings


@lru_cache
def get_invoice_client() -> InvoiceAPIClient:
    return InvoiceAPIClient(
        api_base_url=settings.AMEGO_API_BASE_URL,
        api_key=settings.AMEGO_API_KEY,
        api_tax_id=settings.AMEGO_API_TAX_ID,
    )
