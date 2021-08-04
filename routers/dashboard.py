import datetime
import os
from functools import reduce
from typing import Optional

from babel.numbers import format_decimal
from fastapi import Depends
from fastapi import Header
from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel
from sentry_sdk import capture_exception

from . import get_admin_dal
from . import get_user_dal
from . import router
from database.data_access.adminDAL import AdminDAL
from database.data_access.userDAL import UserDAL
from helpers.token_decoder import decode_auth_token


class JobsBase(BaseModel):
    job_id: int

    class Config:
        orm_mode = True


# Endpoints
@router.get("/alumniassn/dashboard/totals", status_code=status.HTTP_200_OK)
async def generate_dashboard_information(
    userDAL: UserDAL = Depends(get_user_dal),
    authorization: Optional[str] = Header(None),
):
    if not authorization:
        return "Uh uh uh... You didn't say the magic word"

    valid_token = decode_auth_token(authorization)

    if not valid_token:
        return "Uh uh uh... You didn't say the magic word"

    try:
        records = await userDAL.get_all_users()

        # Total registrations
        total_registrations = len([record for record in records])

        # Total successful registrations
        successful_registrations = len(
            [record for record in records if record.payment_status]
        )

        # Pending registrations
        pending_registrations = int(total_registrations) - int(successful_registrations)

        # Total life members
        life_members = len(
            [
                record
                for record in records
                if record.membership_type == "Lifetime" and record.payment_status
            ]
        )

        # Total pending life members
        pending_life_members = len(
            [
                record
                for record in records
                if record.membership_type == "Lifetime" and not record.payment_status
            ]
        )

        # Annual members
        annual_members = len(
            [
                record
                for record in records
                if record.membership_type == "Annual" and record.payment_status
            ]
        )

        # Total pending annual members
        pending_annual_members = len(
            [
                record
                for record in records
                if record.membership_type == "Annual" and not record.payment_status
            ]
        )

        # Total amount collected
        total_amount = 0

        amounts = [record.payment_amount for record in records if record.payment_status]

        if amounts:
            total_amount = reduce(lambda x, y: x + y, amounts)

        # Total amount from life members
        total_amount_lm = 0

        amounts_lm = [
            record.payment_amount
            for record in records
            if record.membership_type == "Lifetime" and record.payment_status
        ]

        if amounts_lm:
            total_amount_lm = reduce(lambda x, y: x + y, amounts_lm)

        # Total amount from annual members
        total_amount_am = 0

        amounts_am = [
            record.payment_amount or 0
            for record in records
            if record.membership_type == "Annual" and record.payment_status
        ]

        if amounts_am:
            total_amount_am = reduce(lambda x, y: x + y, amounts_am)

        return {
            "total_registrations": format_decimal(total_registrations, locale="en_IN"),
            "successful_registrations": format_decimal(
                successful_registrations, locale="en_IN"
            ),
            "pending_registrations": format_decimal(
                pending_registrations, locale="en_IN"
            ),
            "life_members": format_decimal(life_members, locale="en_IN"),
            "annual_members": format_decimal(annual_members, locale="en_IN"),
            "total_amount_collected": format_decimal(total_amount, locale="en_IN"),
            "total_amount_from_life_members": format_decimal(
                total_amount_lm, locale="en_IN"
            ),
            "total_amount_from_annual_members": format_decimal(
                total_amount_am, locale="en_IN"
            ),
            "pending_life_members": format_decimal(
                pending_life_members, locale="en_IN"
            ),
            "pending_annual_members": format_decimal(
                pending_annual_members, locale="en_IN"
            ),
        }
    except Exception as e:
        capture_exception(e)


# Pull all active registrations based on type of membership
@router.get(
    "/alumniassn/dashboard/{membership_type}/{payment_status}",
    status_code=status.HTTP_200_OK,
)
async def get_all_active_members(
    membership_type: str,
    payment_status: int,
    userDAL: UserDAL = Depends(get_user_dal),
    authorization: Optional[str] = Header(None),
):
    if not authorization:
        return "Uh uh uh... You didn't say the magic word"

    valid_token = decode_auth_token(authorization)

    if not valid_token:
        return "Uh uh uh... You didn't say the magic word"

    try:
        records = await userDAL.get_registered_members(membership_type, payment_status)

        all_members = []
        member = {}

        for record in records:
            member["id"] = record.id
            member[
                "membership_id"
            ] = f"MESAA-LM-{str(record.duration_end)[-2:]}-{record.id}"
            member["full_name"] = (
                record.prefix + ". " + record.first_name + " " + record.last_name
            )
            member["email"] = record.email
            member["mobile"] = record.mobile
            member["birthday"] = record.birthday
            member["address1"] = record.address1
            member["address2"] = record.address2
            member["city"] = record.city
            member["state"] = record.state
            member["pincode"] = record.pincode
            member["country"] = record.country
            member["batch"] = record.duration_end
            member["puc"] = record.course_puc
            member["degree"] = record.course_degree
            member["pg"] = record.course_pg
            member["other_courses"] = record.course_others
            member["profession"] = record.profession
            member["other_interests"] = record.other_interests
            member["vision"] = record.vision
            member["id_card_url"] = record.id_card_url
            member["membership_certificate_url"] = record.membership_certificate_url

            all_members.append(member.copy())

        return all_members
    except Exception as e:
        capture_exception(e)


@router.get("/alumniassn/dashboard/expired_members", status_code=status.HTTP_200_OK)
async def get_all_expired_memberships(
    userDal: UserDAL = Depends(get_user_dal),
    authorization: Optional[str] = Header(None),
):
    if not authorization:
        return "Uh uh uh... You didn't say the magic word"

    valid_token = decode_auth_token(authorization)

    if not valid_token:
        return "Uh uh uh... You didn't say the magic word"

    try:
        records = await userDal.fetch_expired_members()

        expired_memberships = []
        member = {}

        for record in records:
            member["id"] = record.id
            member[
                "membership_id"
            ] = f"MESAA-LM-{str(record.duration_end)[-2:]}-{record.id}"
            member["full_name"] = (
                record.prefix + ". " + record.first_name + " " + record.last_name
            )
            member["email"] = record.email
            member["id_card_url"] = record.id_card_url
            member["membership_certificate_url"] = record.membership_certificate_url

            expired_memberships.append(member.copy())

        return expired_memberships
    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch expired memberships",
        )


@router.get("/alumniassn/dashboard/recently_renewed", status_code=status.HTTP_200_OK)
async def get_recently_renewed_memberships(
    userDAL: UserDAL = Depends(get_user_dal),
    authorization: Optional[str] = Header(None),
):

    if not authorization:
        return "Uh uh uh... You didn't say the magic word"

    valid_token = decode_auth_token(authorization)

    if not valid_token:
        return "Uh uh uh... You didn't say the magic word"
    try:
        records = await userDAL.fetch_recently_renewed_memberships()

        if not records:
            return []

        today = datetime.date.today()
        renewed_memberships = []
        member = {}

        for record in records:
            if int((today - record.date_renewed).total_seconds() / 3600 / 24) < 30:
                member["id"] = record.id
                member[
                    "membership_id"
                ] = f"MESAA-LM-{str(record.duration_end)[-2:]}-{record.id}"
                member["full_name"] = (
                    record.prefix + ". " + record.first_name + " " + record.last_name
                )
                member["email"] = record.email
                member["id_card_url"] = record.id_card_url
                member["membership_certificate_url"] = record.membership_certificate_url

                renewed_memberships.append(member.copy())

        return renewed_memberships
    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch renewed memberships",
        )


@router.put("/jobs", status_code=status.HTTP_201_CREATED)
async def job_runtime(
    job: JobsBase,
    adminDAL: AdminDAL = Depends(get_admin_dal),
    job_secret: Optional[str] = Header(None),
):
    if not job_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if job_secret != os.getenv("JOB_SECRET"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        await adminDAL.update_job_last_runtime_date(job.job_id)
    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update job run date",
        )
