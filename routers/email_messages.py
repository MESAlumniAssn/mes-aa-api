import os
from datetime import datetime
from typing import Optional

from fastapi import BackgroundTasks
from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel
from sendgrid.helpers.mail import Mail

from . import router
from helpers.sendgrid_init import send_message


class EmailBase(BaseModel):
    to_email: str
    message: Optional[str]
    year: Optional[int] = datetime.now().year

    class Config:
        orm_mode: True


class WelcomeEmail(EmailBase):
    alumnus_name: str

    class Config:
        orm_mode: True


class ContactEmail(BaseModel):
    sender_email: str
    sender_name: str
    message: str

    class Config:
        orm_mode = True


@router.post("/email/welcome", status_code=status.HTTP_201_CREATED)
def send_welcome_message(email: WelcomeEmail, background_task: BackgroundTasks):
    message = Mail(from_email=os.getenv("PRESIDENT_EMAIL"), to_emails=email.to_email)

    message.dynamic_template_data = {
        "alumni_name": email.alumnus_name,
    }

    message.template_id = os.getenv("WELCOME_EMAIL_TEMPLATE")

    try:
        background_task.add_task(send_message, message)
        return status.HTTP_202_ACCEPTED
    except Exception:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="The email could not be sent"
        )


@router.post("/email/contact", status_code=status.HTTP_201_CREATED)
def send_contact_message(email: ContactEmail, background_task: BackgroundTasks):
    message = Mail(
        from_email=os.getenv("CONTACT_EMAIL"), to_emails=os.getenv("CONTACT_EMAIL")
    )

    message.dynamic_template_data = {
        "sender_email": email.sender_email,
        "sender_name": email.sender_name,
        "message": email.message,
    }

    message.template_id = os.getenv("CONTACT_EMAIL_TEMPLATE")

    try:
        # background_task.add_task(send_message, message)
        send_message(message)
        return status.HTTP_202_ACCEPTED
    except Exception:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="The email could not be sent"
        )
