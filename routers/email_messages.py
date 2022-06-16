import datetime
import os
from typing import Optional

from dateutil.relativedelta import relativedelta
from fastapi import BackgroundTasks
from fastapi import Header
from fastapi import HTTPException
from fastapi import status
from fastapi.param_functions import Depends
from pydantic import BaseModel
from sendgrid.helpers.mail import Mail
from sentry_sdk import capture_exception

from . import get_user_dal
from . import router
from database.data_access.userDAL import UserDAL
from helpers.random_messages import return_random_message
from helpers.sendgrid_init import send_message


class EmailBase(BaseModel):
    to_email: str
    message: Optional[str]
    year: Optional[int] = datetime.datetime.now().year

    class Config:
        orm_mode = True


class WelcomeEmail(EmailBase):
    alumnus_name: str

    class Config:
        orm_mode = True


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
        orm_mode = True


class PaymentReceiptEmail(EmailBase):
    alumni_name: str
    alumni_address1: str
    alumni_address2: Optional[str]
    city: str
    state: str
    pincode: str
    country: str
    invoice_number: str
    membership_type: str
    renewal_date: Optional[datetime.date] = None

    class Config:
        orm_mode = True


class BirthdayEmail(EmailBase):
    name: str

    class Config:
        orm_mode = True


class RenewalEmail(EmailBase):
    name: str
    days: int
    renewal_url: str

    class Config:
        orm_mode = True


class ExpiredMembershipEmail(EmailBase):
    name: str
    renewal_url: str

    class Config:
        orm_mode = True


class EventNotificationEmail(BaseModel):
    event_name: str
    event_date: datetime.date
    event_time: str
    venue: str
    chief_guest: Optional[str] = None

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
    except Exception as e:
        capture_exception(e)
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
    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="The email could not be sent"
        )


@router.post("/email/payment/manual", status_code=status.HTTP_201_CREATED)
def send_manual_payment_email(
    email: ManualPaymentEmail, background_task: BackgroundTasks
):
    message = Mail(from_email=os.getenv("CONTACT_EMAIL"), to_emails=email.to_email)

    expiry_date = datetime.date.today() + relativedelta(years=1)

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
    except Exception as e:
        capture_exception(e)
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
    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="The email could not be sent"
        )


@router.post("/email/receipt", status_code=status.HTTP_201_CREATED)
def send_payment_receipt(email: PaymentReceiptEmail, background_task: BackgroundTasks):
    message = Mail(from_email=os.getenv("ADMIN_EMAIL"), to_emails=email.to_email)

    message.add_cc(os.getenv("TREASURER_EMAIL"))

    # This line is needed until the SendGrid blacklist issue is resolved
    message.add_bcc(os.getenv("TECH_EMAIL"))

    expiry_date = datetime.date.today() + relativedelta(years=1)

    # renewal_date is sent int payload only for renewals
    # during registration, we just add one year to the current date
    if email.renewal_date:
        validity = email.renewal_date.strftime("%d-%b-%Y")
    else:
        validity = (
            expiry_date.strftime("%d-%b-%Y")
            if email.membership_type == "Annual"
            else "Lifetime"
        )

    message.dynamic_template_data = {
        "alumni_name": email.alumni_name,
        "alumni_address1": email.alumni_address1,
        "alumni_address2": email.alumni_address2,
        "city": email.city,
        "state": email.state,
        "pincode": email.pincode,
        "country": email.country.title(),
        "invoice_number": email.invoice_number,
        "invoice_date": datetime.date.today().strftime("%d-%b-%Y"),
        "membership_type": email.membership_type,
        "amount_paid": os.getenv("LIFETIME_MEMBERSHIP_AMOUNT")
        if email.membership_type == "Lifetime"
        else os.getenv("ANNUAL_MEMBERSHIP_AMOUNT"),
        "validity": validity,
        "year": email.year,
    }

    message.template_id = os.getenv("PAYMENT_RECEIPT_EMAIL_TEMPLATE")

    try:
        background_task.add_task(send_message, message)
        return status.HTTP_202_ACCEPTED
    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="The email could not be sent"
        )


# Job related
@router.post("/email/birthday", status_code=status.HTTP_201_CREATED)
def send_birthday_message(
    email: BirthdayEmail,
    background_task: BackgroundTasks,
    job_secret: Optional[str] = Header(None),
):
    if not job_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if job_secret != os.getenv("JOB_SECRET"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    message = Mail(from_email=os.getenv("CONTACT_EMAIL"), to_emails=email.to_email)

    birthday_message = return_random_message()

    message.dynamic_template_data = {
        "name": email.name,
        "birthday_message": birthday_message,
    }

    message.template_id = os.getenv("BIRTHDAY_EMAIL_TEMPLATE")

    try:
        background_task.add_task(send_message, message)
        return status.HTTP_202_ACCEPTED
    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="The email could not be sent"
        )


# Job related
@router.post("/email/renewal", status_code=status.HTTP_201_CREATED)
def send_renewal_notification(
    email: RenewalEmail,
    background_task: BackgroundTasks,
    job_secret: Optional[str] = Header(None),
):
    if not job_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if job_secret != os.getenv("JOB_SECRET"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    message = Mail(from_email=os.getenv("ADMIN_EMAIL"), to_emails=email.to_email)

    message.dynamic_template_data = {
        "name": email.name,
        "days": email.days,
        "day": email.days == 1,
        "renewal_url": email.renewal_url,
    }

    message.template_id = os.getenv("RENEWAL_EMAIL_TEMPLATE")

    try:
        background_task.add_task(send_message, message)
        return status.HTTP_202_ACCEPTED
    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="The email could not be sent"
        )


# Partial job related. Hence skipping the secret
@router.post("/email/expired_membership", status_code=status.HTTP_201_CREATED)
def send_expiry_notification(
    email: ExpiredMembershipEmail, background_task: BackgroundTasks
):

    message = Mail(from_email=os.getenv("ADMIN_EMAIL"), to_emails=email.to_email)

    message.dynamic_template_data = {
        "name": email.name,
        "renewal_url": email.renewal_url,
    }

    message.template_id = os.getenv("MEMBERSHIP_EXPIRED_EMAIL_TEMPLATE")

    try:
        background_task.add_task(send_message, message)
        return status.HTTP_202_ACCEPTED
    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="The email could not be sent"
        )


@router.post("/email/events", status_code=status.HTTP_201_CREATED)
async def send_event_notification(
    email: EventNotificationEmail,
    background_task: BackgroundTasks,
    userDAL: UserDAL = Depends(get_user_dal),
):
    records = await userDAL.get_all_users_subscribed_to_emails()

    emails = [record.email for record in records]

    message = Mail(from_email=os.getenv("ADMIN_EMAIL"), to_emails=emails)

    message.dynamic_template_data = {
        "event_name": email.event_name,
        "event_date": email.event_date.strftime("%d %B %Y"),
        "event_time": email.event_time,
        "venue": email.venue,
        "chief_guest": email.chief_guest,
    }

    message.template_id = os.getenv("EVENT_NOTIFICATION_EMAIL_TEMPLATE")

    try:
        background_task.add_task(send_message, message)
        return status.HTTP_202_ACCEPTED
    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="The email could not be sent"
        )


@router.post("/email/auto_response", status_code=status.HTTP_201_CREATED)
async def send_auto_response_email(email: EmailBase, background_task: BackgroundTasks):
    message = Mail(
        from_email=os.getenv("ADMIN_EMAIL"),
        to_emails=email.to_email,
    )

    message.template_id = os.getenv("AUTO_RESPONSE_EMAIL_TEMPLATE")

    try:
        background_task.add_task(send_message, message)
        return status.HTTP_202_ACCEPTED
    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="The email could not be sent"
        )
