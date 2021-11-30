from typing import Generator
import datetime
import hmac
import hashlib
import base64
from pydantic import BaseSettings, Field
import httpx


class AuthSettings(BaseSettings):
    """Gets the Coinbase authentication settings from the local env variables or .env file"""

    api_key: str = Field(None, env="coinbase_api_key")
    secret: str = Field(None, env="coinbase_secret")
    passphrase: str = Field(None, env="coinbase_passphrase")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class CoinbaseAuth(httpx.Auth):
    requires_request_body = True

    def __init__(self):
        self.settings = AuthSettings()

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        """Sets the authentication headers on the requests to the Coinbase API"""
        self.timestamp = str(datetime.datetime.now().timestamp())
        request.headers["CB-ACCESS-KEY"] = self.settings.api_key
        request.headers["CB-ACCESS-PASSPHRASE"] = self.settings.passphrase
        request.headers["CB-ACCESS-SIGN"] = self.signature(request)
        request.headers["CB-ACCESS-TIMESTAMP"] = self.timestamp
        yield request

    def signature(self, request: httpx.Request) -> str:
        """Create the signature for the request header"""
        msg = (
            self.timestamp + request.method.upper() + request.url.path + request.content.decode("utf-8")
        )
        key = base64.b64decode(self.settings.secret)
        signature = hmac.new(key, msg.encode("utf-8"), hashlib.sha256)
        return base64.b64encode(signature.digest()).decode("utf-8")
