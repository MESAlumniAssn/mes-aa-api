import datetime
import os
from typing import Optional

from dateutil.relativedelta import relativedelta
from fastapi import Depends
from fastapi import Header
from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel
from sentry_sdk import capture_exception

from . import get_user_dal
from . import router
from database.data_access.userDAL import UserDAL


class Renewal(BaseModel):
    email: str
    membership_type: str
    payment_amount: int
    membership_valid_upto: str
    membership_certificate_url: Optional[str]
    payment_mode: str

    class Config:
        orm_mode = True


class RenewalHash(BaseModel):
    email: str

    class Config:
        orm_mode = True


class ClearRenewalHash(BaseModel):
    id: str

    class Config:
        orm_mode = True


@router.get("/renewal_details/{renewal_hash}", status_code=status.HTTP_200_OK)
async def renewal_details(renewal_hash: str, userDAL: UserDAL = Depends(get_user_dal)):
    try:
        split_hash = renewal_hash.split("-")

        record = await userDAL.get_user_renewal_details(split_hash[-1])

        if not record:
            return None

        name = (
            record[0].prefix + ". " + record[0].first_name + " " + record[0].last_name
        )

        days_to_renewal = int(
            (record[0].membership_valid_upto - datetime.date.today()).total_seconds()
            / 3600
            / 24
        )

        new_renewal_date = (
            record[0].membership_valid_upto + relativedelta(years=1)
            if days_to_renewal > 0
            else datetime.date.today() + relativedelta(years=1)
        )

        membership_id_prefix = "MESAA-"
        membership_id_suffix = f"{str(record[0].duration_end)[2:]}-{record[0].id}"

        annual_membership_id = membership_id_prefix + "OM-" + membership_id_suffix
        lifetime_membership_id = membership_id_prefix + "LM-" + membership_id_suffix

        return {
            "id": record[0].id,
            "name": name,
            "email": record[0].email,
            "mobile": record[0].mobile,
            "membership_id": annual_membership_id,
            "membership_id_after_upgrade": lifetime_membership_id,
            "current_membership_valid_up_to": record[0].membership_valid_upto.strftime(
                "%d-%b-%Y"
            ),
            "days_until_expiry": days_to_renewal,
            "new_renewal_date": new_renewal_date.strftime("%d-%b-%Y"),
            "membership_certificate_url": os.getenv("SITE_DOMAIN")
            + f"/certificate/{record[0].alt_user_id}",
            "address1": record[0].address1,
            "address2": record[0].address2,
            "city": record[0].city,
            "state": record[0].state,
            "pincode": record[0].pincode,
            "country": record[0].country,
            "alt_user_id": record[0].alt_user_id,
        }

    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch user renewal details",
        )


# Partially job related
@router.put("/membership_renewal", status_code=status.HTTP_201_CREATED)
async def renew_annual_membership(
    membership_renewal: Renewal,
    userDAL: UserDAL = Depends(get_user_dal),
):
    date_renewed = datetime.date.today()

    # Convert date to required format
    valid_up_to_date = datetime.datetime.strptime(
        membership_renewal.membership_valid_upto, "%Y-%m-%d"
    ).date()

    try:
        await userDAL.update_renewal_details(
            membership_renewal.email.lower(),
            membership_renewal.membership_type,
            membership_renewal.payment_amount,
            valid_up_to_date,
            membership_renewal.membership_certificate_url,
            date_renewed,
            membership_renewal.payment_mode,
        )
    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update renewal details",
        )


@router.put("/renewal_hash/clear", status_code=status.HTTP_201_CREATED)
async def clear_hash_after_online_payment(
    renewal_hash: ClearRenewalHash, userDAL: UserDAL = Depends(get_user_dal)
):
    try:
        await userDAL.clear_renewal_hash(renewal_hash.id)
    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not clear hash",
        )


# Job related
@router.get("/expiring_memberships/{days_remaining}", status_code=status.HTTP_200_OK)
async def get_all_memberships_due_to_expire(
    days_remaining: int,
    userDAL: UserDAL = Depends(get_user_dal),
    job_secret: Optional[str] = Header(None),
):
    if not job_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if job_secret != os.getenv("JOB_SECRET"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    expiry_date = datetime.date.today() + relativedelta(days=days_remaining)
    expiry_date = expiry_date.strftime("%Y-%m-%d")

    expiring_memberships = []
    expiring_membership_obj = {}

    try:
        records = await userDAL.get_expiring_memberships(expiry_date)

        if not records:
            return None

        for record in records:
            expiring_membership_obj["name"] = record.first_name.title()
            expiring_membership_obj["email"] = record.email
            expiring_membership_obj["alt_user_id"] = record.alt_user_id
            expiring_membership_obj["days_to_expiry"] = days_remaining

            expiring_memberships.append(expiring_membership_obj.copy())

        return expiring_memberships

    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch expiring memberships",
        )


# Job related
@router.put("/renewal_hash", status_code=status.HTTP_201_CREATED)
async def generate_renewal_hash(
    renewal_hash: RenewalHash,
    userDAL: UserDAL = Depends(get_user_dal),
    job_secret: Optional[str] = Header(None),
):
    if not job_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if job_secret != os.getenv("JOB_SECRET"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        renewal_hash = await userDAL.create_renewal_hash(renewal_hash.email)

        return renewal_hash
    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate the renewal hash",
        )


# Job related
@router.put("/expire_active_memberships", status_code=status.HTTP_201_CREATED)
async def expire_membership(
    email: RenewalHash,
    userDAL: UserDAL = Depends(get_user_dal),
    job_secret: Optional[str] = Header(None),
):
    if not job_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if job_secret != os.getenv("JOB_SECRET"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        await userDAL.mark_membership_as_expired(email.email)

        return status.HTTP_202_ACCEPTED
    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate the renewal hash",
        )


# Job related
@router.get("/recently_expired_memberships", status_code=status.HTTP_200_OK)
async def get_all_recently_expired_memberships(
    userDAL: UserDAL = Depends(get_user_dal),
    job_secret: Optional[str] = Header(None),
):
    if not job_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if job_secret != os.getenv("JOB_SECRET"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    today = datetime.date.today().strftime("%Y-%m-%d")

    expired_memberships = []
    expired_membership_obj = {}

    try:
        records = await userDAL.get_recently_expired_memberships(today)

        if not records:
            return None

        for record in records:
            expired_membership_obj["name"] = record.first_name.title()
            expired_membership_obj["email"] = record.email
            expired_membership_obj["alt_user_id"] = record.alt_user_id
            expired_membership_obj["renewal_hash"] = record.renewal_hash

            expired_memberships.append(expired_membership_obj.copy())

        return expired_memberships

    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch expired memberships",
        )
