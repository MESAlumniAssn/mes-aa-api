import datetime
import os
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
    year: Optional[int] = datetime.datetime.now().year

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


class ManualPaymentEmail(EmailBase):
    membership_id: str
    alumni_name: str
    membership_type: str

    class Config:
        orm_mode = True


class TestimonialEmail(BaseModel):
    name: str
    batch: str
    message: str
    approve_url: str

    class Config:
        orm_mode: True


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
        background_task.add_task(send_message, message)
        return status.HTTP_202_ACCEPTED
    except Exception:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="The email could not be sent"
        )


@router.post("/email/payment/manual", status_code=status.HTTP_201_CREATED)
def send_manual_payment_email(
    email: ManualPaymentEmail, background_task: BackgroundTasks
):
    message = Mail(from_email=os.getenv("CONTACT_EMAIL"), to_emails=email.to_email)

    expiry_date = datetime.date.today() + datetime.timedelta(days=365)

    message.dynamic_template_data = {
        "alumni_name": email.alumni_name,
        "membership_type": email.membership_type,
        "membership_id": email.membership_id,
        "annual": email.membership_type == "Annual",
        "amount": os.getenv("LIFETIME_MEMBERSHIP_AMOUNT")
        if email.membership_type == "Lifetime"
        else os.getenv("ANNUAL_MEMBERSHIP_AMOUNT"),
        "expiry_date": expiry_date.strftime("%d-%b-%Y")
        if email.membership_type == "Annual"
        else None,
        "bank_account_number": os.getenv("BANK_ACCOUNT_NUMBER"),
        "account_holder": os.getenv("ACCOUNT_HOLDER_NAME"),
        "bank_name": os.getenv("BANK_NAME"),
        "bank_branch": os.getenv("BANK_BRANCH"),
        "bank_ifsc": os.getenv("BANK_IFSC"),
        "year": email.year,
    }

    message.template_id = os.getenv("MANUAL_PAYMENT_EMAIL_TEMPLATE")

    try:
        background_task.add_task(send_message, message)
        # send_message(message)
        return status.HTTP_202_ACCEPTED
    except Exception:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="The email could not be sent"
        )


@router.post("/email/testimonial", status_code=status.HTTP_201_CREATED)
def send_testimonial_approval_message(
    email: TestimonialEmail, background_task: BackgroundTasks
):
    message = Mail(
        from_email=os.getenv("CONTACT_EMAIL"), to_emails=os.getenv("CONTACT_EMAIL")
    )

    message.dynamic_template_data = {
        "name": email.name,
        "batch": email.batch,
        "message": email.message,
        "approve_url": email.approve_url,
    }

    message.template_id = os.getenv("TESTIMONIAL_SUBMISSION_TEMPLATE")

    try:
        background_task.add_task(send_message, message)
        return status.HTTP_202_ACCEPTED
    except Exception:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="The email could not be sent"
        )
