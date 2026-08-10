import os

import pyotp
from dotenv import load_dotenv
from SmartApi import SmartConnect


load_dotenv()


class AngelAuth:

    def __init__(self):
        self.api_key = os.getenv("ANGEL_API_KEY")
        self.client_code = os.getenv("ANGEL_CLIENT_CODE")
        self.pin = os.getenv("ANGEL_PIN")
        self.totp_secret = os.getenv("ANGEL_TOTP_SECRET")

        self.smart_api = None

        self.auth_token = None
        self.refresh_token = None
        self.feed_token = None

    def login(self):

        if not all([
            self.api_key,
            self.client_code,
            self.pin,
            self.totp_secret,
        ]):
            raise ValueError(
                "Missing Angel One credentials in .env"
            )

        self.smart_api = SmartConnect(
            api_key=self.api_key
        )

        totp = pyotp.TOTP(
            self.totp_secret
        ).now()

        session = self.smart_api.generateSession(
            self.client_code,
            self.pin,
            totp,
        )

        if not session.get("status"):
            raise RuntimeError(
                f"Angel One login failed: {session}"
            )

        data = session["data"]

        self.auth_token = data["jwtToken"]
        self.refresh_token = data["refreshToken"]

        self.feed_token = (
            self.smart_api.getfeedToken()
        )

        return {
            "auth_token": self.auth_token,
            "refresh_token": self.refresh_token,
            "feed_token": self.feed_token,
        }