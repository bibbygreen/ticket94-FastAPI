import base64
import json

import requests
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util import Padding

from src.config import settings
from src.logger import logger
from src.order.schemas import MyPayOrderItem


class StoreOrder:
    store_uid = settings.MYPAY_STORE_UID
    store_key = settings.MYPAY_STORE_KEY.encode("utf-8")
    url = settings.MYPAY_URL

    def get_raw_data(self, cost: str, user_id: str, order_id: str, items: list[MyPayOrderItem]):
        """取得串接欄位資料

        Returns:
            {dict}: 欄位資料
        """
        rawData = {
            "store_uid": self.store_uid,
            "items": items,
            "cost": cost,
            "user_id": user_id,
            "order_id": order_id,
            "ip": "127.0.0.1",
            "pfn": "0",
        }
        return rawData

    def get_service(self):
        return {"service_name": "api", "cmd": "api/orders"}

    def encrypt(self, fields, key):
        data = json.dumps(fields, separators=(",", ":"))
        data = Padding.pad(data.encode("utf-8"), AES.block_size)
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        data = cipher.encrypt(data)
        data = base64.b64encode(iv + data)
        return data

    def post(self, postData):
        result = requests.post(self.url, postData)
        return result.text

    def get_post_data(self, cost: str, user_id: str, order_id: str, items: list[MyPayOrderItem]):
        post_data = {
            "store_uid": self.store_uid,
            "service": self.encrypt(self.get_service(), self.store_key),
            "encry_data": self.encrypt(
                self.get_raw_data(cost=cost, user_id=user_id, order_id=order_id, items=items),
                self.store_key,
            ),
        }
        return post_data

    def run(self, cost: str, user_id: str, order_id: str, items: list[MyPayOrderItem]):
        try:
            post_data = self.get_post_data(
                cost=cost,
                user_id=user_id,
                order_id=order_id,
                items=[item.model_dump() for item in items],
            )

            logger.info(post_data)

            response_text = self.post(post_data)

            return json.loads(response_text)

        except Exception as exc:
            logger.exception(exc)
            raise exc


mypay_store_order = StoreOrder()
