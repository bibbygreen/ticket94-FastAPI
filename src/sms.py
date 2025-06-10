import logging

import requests

from src.logger import logger


class MitakeSMS:
    def __init__(self, api_url, check_point_url, username, password):
        self.username = username
        self.password = password
        self.api_url = api_url
        self.check_point_url = check_point_url

        logging.basicConfig(
            filename="mitake_sms.log",
            level=logging.INFO,
            format="[%(levelname)s] %(asctime)s - %(message)s",
        )
        self.logger = logging.getLogger("mitake_sms")

    def send_sms_code(self, phone: str, sms_message: str):
        self.phone = phone
        self.sms_message = sms_message
        data = {
            "username": self.username,
            "password": self.password,
            "dstaddr": phone,
            "smbody": sms_message.encode("big5"),
        }

        response = requests.post(
            self.API_URL,
            params=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )

        if "AccountPoint=" in response.text:
            account_point = response.text.split("AccountPoint=")[-1]

            self.points = int(account_point)

        if "statuscode=1" in response.text:
            msg = f"[成功]: 點數剩餘 {self.points} 發送至 {self.phone}，內容為: {self.sms_message}"

            self.logger.info(msg)
            logger.info(msg)
        else:
            logger.error(f"[失敗]: error message: {response.text}")
            self.logger.error(f"[失敗]: error message: {response.text}")

    def query_sms_points(self):
        data = {
            "username": self.username,
            "password": self.password,
        }

        response = requests.post(
            self.check_point_url,
            params=data,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        if "AccountPoint=" in response.text:
            account_point = response.text.split("AccountPoint=")[-1]
            self.points = int(account_point)
            msg = f"[成功]: 點數剩餘 {self.points}"
            self.logger.info(msg)
            return {"success": True, "message": msg, "points": self.points}
        else:
            error_msg = f"[失敗]: error message: {response.text}"
            self.logger.error(error_msg)
            return {"success": False, "message": error_msg}
