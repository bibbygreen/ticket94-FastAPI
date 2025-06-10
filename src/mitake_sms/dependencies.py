from functools import lru_cache

from src.config import settings
from src.mitake_sms.service import MitakeSMS


@lru_cache
def get_mitake_sms_client() -> MitakeSMS:
    return MitakeSMS(
        api_url=settings.MITAKE_SMS_API_URL,
        check_point_url=settings.MITAKE_SMS_CHECKPOINT_URL,
        username=settings.MITAKE_SMS_USERNAME,
        password=settings.MITAKE_SMS_PASSWORD,
    )
