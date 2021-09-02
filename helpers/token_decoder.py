import os
from datetime import datetime

from jose import jwt
from jose.exceptions import ExpiredSignatureError


def decode_auth_token(token: str):

    try:
        decoded_token = jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )

        return decoded_token["sub"] == os.getenv(
            "ADMIN_UUID"
        ) and datetime.now() < datetime.fromtimestamp(decoded_token["exp"])
    except ExpiredSignatureError:
        return False
