import os
from datetime import timedelta
from typing import Optional

from fastapi import Depends
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from . import get_admin_dal
from . import router
from database.data_access.adminDAL import AdminDAL

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    id: Optional[str]


class UserAuth(BaseModel):
    email: str
    password: str


@router.post("/auth", status_code=status.HTTP_200_OK)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    adminDAL: AdminDAL = Depends(get_admin_dal),
):
    user = await adminDAL.authenticate_user(form_data.username, form_data.password)

    id = str(user.id)

    access_token_expires = timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    )

    access_token = adminDAL.create_access_token(
        data={"sub": id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
