# import os
from pydantic import BaseModel

# from fastapi import BackgroundTasks
# from fastapi import HTTPException
# from fastapi import status

# from sendgrid.helpers.mail import Mail


class EmailBase(BaseModel):
    from_email: str

    class Config:
        orm_mode: True
