import datetime
import hmac
import hashlib
import base64
import json
from pydantic import BaseSettings, Field


class Auth(BaseSettings):
    """Class to generate the authentication headers for Coinbase requests"""

    api_key: str = Field(None, env="coinbase_api_key")
    secret: str = Field(None, env="coinbase_secret")
    passphrase: str = Field(None, env="coinbase_passphrase")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def request_header(
        self, endpoint: str, method: str = "GET", body: dict = None
    ) -> dict:
        """Create the request header for authenticationg Coinbase requests"""
        if body is None:
            body = ""
        else:
            body = json.dumps(body)
        timestamp = str(datetime.datetime.now().timestamp())
        msg = timestamp + method.upper() + endpoint + body
        return {
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-PASSPHRASE": self.passphrase,
            "CB-ACCESS-SIGN": self.create_signature(msg, self.secret),
            "CB-ACCESS-TIMESTAMP": timestamp,
        }

    @staticmethod
    def create_signature(msg: str, secret: str) -> str:
        """Create the signature for the request header"""
        key = base64.b64decode(secret)
        signature = hmac.new(key, msg.encode("utf-8"), hashlib.sha256)
        return base64.b64encode(signature.digest()).decode("utf-8")
