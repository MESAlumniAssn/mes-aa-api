from functools import reduce

from babel.numbers import format_decimal
from fastapi import Depends
from fastapi import status

from . import get_user_dal
from . import router
from database.data_access.userDAL import UserDAL


# Endpoints
@router.get("/alumniassn/dashboard/totals", status_code=status.HTTP_200_OK)
async def generate_dashboard_information(userDAL: UserDAL = Depends(get_user_dal)):
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
        "pending_registrations": format_decimal(pending_registrations, locale="en_IN"),
        "life_members": format_decimal(life_members, locale="en_IN"),
        "annual_members": format_decimal(annual_members, locale="en_IN"),
        "total_amount_collected": format_decimal(total_amount, locale="en_IN"),
        "total_amount_from_life_members": format_decimal(
            total_amount_lm, locale="en_IN"
        ),
        "total_amount_from_annual_members": format_decimal(
            total_amount_am, locale="en_IN"
        ),
        "pending_life_members": format_decimal(pending_life_members, locale="en_IN"),
        "pending_annual_members": format_decimal(
            pending_annual_members, locale="en_IN"
        ),
    }


# Pull all active registrations based on type of membership
@router.get(
    "/alumniassn/dashboard/{membership_type}/{payment_status}",
    status_code=status.HTTP_200_OK,
)
async def get_all_active_members(
    membership_type: str, payment_status: int, userDAL: UserDAL = Depends(get_user_dal)
):
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

        all_members.append(member.copy())

    return all_members