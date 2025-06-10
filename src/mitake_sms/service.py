import urllib.parse

import httpx

from src.logger import logger


class MitakeSMS:
    def __init__(self, api_url: str, check_point_url: str, username: str, password: str):
        self.username = username
        self.password = password
        self.api_url = api_url
        self.check_point_url = check_point_url

    async def send_sms_code(self, phone: str, sms_message: str) -> None:
        data = {
            "username": self.username,
            "password": self.password,
            "dstaddr": phone,
            "smbody": sms_message.encode("big5"),
        }

        encoded_data = urllib.parse.urlencode(data, encoding="big5")

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                self.api_url,
                data=encoded_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        if "AccountPoint=" in response.text:
            account_point = response.text.split("AccountPoint=")[-1]

            self.points = int(account_point)

        if "statuscode=1" in response.text:
            logger.info(
                f"[MitakeSMS][成功]: 點數剩 {self.points}點，發送至 {phone}，內容為: {sms_message}"
            )
        else:
            logger.error(f"[MitakeSMS][失敗]: error message: {response.text}")
            raise Exception(f"[MitakeSMS][失敗]: error message: {response.text}")

    async def query_sms_points(self) -> dict:
        data = {
            "username": self.username,
            "password": self.password,
        }

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                self.check_point_url,
                params=data,
                headers={"Content-Type": "application/json"},
            )

        if "AccountPoint=" in response.text:
            account_point = response.text.split("AccountPoint=")[-1]
            self.points = int(account_point)

            msg = f"[MitakeSMS][成功]: 點數剩餘 {self.points}"

            return {"success": True, "message": msg, "points": self.points}
        else:
            error_msg = f"[MitakeSMS][失敗]: error message: {response.text}"

            return {"success": False, "message": error_msg}
