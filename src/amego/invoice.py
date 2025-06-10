import hashlib
import time
import urllib.parse

import httpx

from src.amego.schemas import CreateAmegoInvoiceRequest


class InvoiceAPIClient:
    def __init__(self, api_base_url: str, api_key: str, api_tax_id: str):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.api_tax_id = api_tax_id

    def generate_signature(self, invoice_data: CreateAmegoInvoiceRequest, timestamp: int) -> str:
        """生成請求簽名"""
        s_api_data = invoice_data.model_dump_json()
        hash_text = s_api_data + str(timestamp) + self.api_key
        m = hashlib.md5()
        m.update(hash_text.encode("utf-8"))
        return m.hexdigest()

    async def create_invoice(self, invoice_data: CreateAmegoInvoiceRequest) -> dict:
        """發送開立發票請求"""

        crate_invoice_url = f"{self.api_base_url}/json/f0401"

        timestamp = int(time.time())
        signature = self.generate_signature(invoice_data, timestamp)

        post_data = {
            "invoice": self.api_tax_id,
            "data": invoice_data.model_dump_json(),
            "time": timestamp,
            "sign": signature,
        }

        payload = urllib.parse.urlencode(post_data, doseq=True)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        async with httpx.AsyncClient() as client:
            response = await client.post(url=crate_invoice_url, headers=headers, data=payload)
            return response.json()
