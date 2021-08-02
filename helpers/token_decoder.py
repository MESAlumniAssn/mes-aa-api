import os

from jose import jwt


def decode_auth_token(token: str):
    decoded_token = jwt.decode(
        token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
    )

    return decoded_token["sub"] == os.getenv("ADMIN_UUID")
