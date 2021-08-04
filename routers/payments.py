import os
from typing import Dict
from typing import Optional

import razorpay
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel
from razorpay.errors import SignatureVerificationError
from sentry_sdk import capture_exception

from . import get_user_dal
from . import router
from database.data_access.userDAL import UserDAL


class Order(BaseModel):
    amount: int
    currency: str
    receipt: str
    notes: Optional[Dict]


class PaymentVerification(BaseModel):
    order_id: str
    payment_id: str
    signature: str = os.getenv("RAZORPAY_KEY_SECRET")
    email: str


client = razorpay.Client(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))


@router.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_order(order: Order):
    try:
        client = razorpay.Client(
            auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
        )

        order_data = {
            "amount": order.amount,
            "currency": order.currency,
            "receipt": order.receipt,
            "notes": order.notes,
        }

        return client.order.create(order_data)
    except Exception as e:
        capture_exception(e)


@router.post("/verification", status_code=status.HTTP_201_CREATED)
async def verify_payment(
    payment_verification: PaymentVerification, user_dal: UserDAL = Depends(get_user_dal)
):
    client = razorpay.Client(
        auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
    )

    params_dict = {
        "razorpay_order_id": payment_verification.order_id,
        "razorpay_payment_id": payment_verification.payment_id,
        "razorpay_signature": payment_verification.signature,
    }

    try:
        verification_status = client.utility.verify_payment_signature(params_dict)

        await user_dal.update_payment_status_by_email(payment_verification.email)

        if verification_status is None:  # success
            return {"status": verification_status}
    except SignatureVerificationError:
        capture_exception(SignatureVerificationError)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment verification failed",
        )
