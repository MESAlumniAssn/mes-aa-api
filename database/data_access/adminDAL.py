import os
from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import Optional

from fastapi import HTTPException
from fastapi import status
from jose import jwt
from passlib.hash import pbkdf2_sha256
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from database.models import Admin
from database.models import Job


class AdminDAL:
    def __init__(self, session: Session):
        self.session = session

    async def find_user_by_email(self, email: str):
        q = await self.session.execute(select(Admin).where(Admin.email == email))
        return q.scalars().first()

    def verify_password(self, plain_text_password: str, password_hash: str):
        return pbkdf2_sha256.verify(plain_text_password, password_hash)

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ):
        # sourcery skip: inline-immediately-returned-variable
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=43200)

        to_encode.update({"exp": expire, "iat": datetime.utcnow()})

        # to_encode.update({"iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(
            to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM")
        )
        return encoded_jwt

    async def authenticate_user(self, email: str, password: str):
        email = email.lower()

        user = await self.find_user_by_email(email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"{email} is not valid"
            )

        if not self.verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="That password is incorrect",
            )

        return user

    async def update_job_last_runtime_date(self, job_id: int):
        q = update(Job).where(Job.job_id == job_id)
        q = q.values(job_last_runtime=date.today())

        await self.session.execute(q)
