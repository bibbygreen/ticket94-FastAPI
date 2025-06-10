from functools import lru_cache

from src.mypay.service import StoreOrder


@lru_cache
def get_mypay_store_order() -> StoreOrder:
    return StoreOrder()
