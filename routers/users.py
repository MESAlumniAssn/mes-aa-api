import datetime
import io
import os
import secrets
import uuid
from typing import List
from typing import Optional

from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import status
from fastapi import UploadFile
from PIL import ExifTags
from PIL import Image
from sqlalchemy.exc import SQLAlchemyError

from . import get_user_dal
from . import router
from database.data_access.userDAL import UserDAL
from helpers.imagekit_init import initialize_imagekit

# import cloudinary.uploader


# This function is mainly for images clicked on phones where the exif data causes image rotation
def fix_image_orientation(optimized_image):
    # sourcery skip: remove-unnecessary-else, swap-if-else-branches
    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation] == "Orientation":
            break

    exif = optimized_image._getexif()

    if exif:
        if 274 in exif.keys():
            if exif[274] == 3:
                optimized_image = optimized_image.rotate(180, expand=True)
            elif exif[274] == 6:
                optimized_image = optimized_image.rotate(270, expand=True)
            elif exif[274] == 8:
                optimized_image = optimized_image.rotate(90, expand=True)
    else:
        return optimized_image

    return optimized_image


# def upload_file_to_cloudinary(
#     alt_user_id: str, images: List, userDAL: UserDAL = Depends(get_user_dal)
# ):
#     cloudinary.config(
#         cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
#         api_key=os.getenv("CLOUDINARY_API_KEY"),
#         api_secret=os.getenv("CLOUDINARY_API_SECRET"),
#     )

#     image_size = (300, 300)

#     file_name, file_ext = os.path.splitext(images[0].filename)

#     file_ext = file_ext.lower()

#     if file_ext == ".jpg":
#         file_ext = ".jpeg"

#     optimized_image = Image.open(images[0].file)

#     optimized_image = fix_image_orientation(optimized_image)

#     optimized_image = optimized_image.resize(image_size)

#     in_mem_file = io.BytesIO()
#     optimized_image.save(in_mem_file, format=file_ext[1:], optimized=True)
#     in_mem_file.seek(0)

#     upload_result = cloudinary.uploader.upload(
#         in_mem_file,
#         folder=f"MES-AA/profile/{alt_user_id}",
#         overwrite=True,
#         public_id=alt_user_id,
#     )

#     return upload_result["secure_url"]


def upload_file_to_imagekit(alt_user_id: str, images: List):
    imagekit = initialize_imagekit()

    file_name, file_ext = os.path.splitext(images[0].filename)

    file_ext = file_ext.lower()

    if file_ext == ".jpg":
        file_ext = ".jpeg"

    optimized_image = Image.open(images[0].file)
    optimized_image = fix_image_orientation(optimized_image)

    in_mem_file = io.BytesIO()
    optimized_image.save(in_mem_file, format=file_ext[1:], optimized=True)
    in_mem_file.seek(0)

    random_file_name = secrets.token_hex(8)

    uploaded_image = imagekit.upload_file(
        file=in_mem_file,
        file_name=random_file_name,
        options={
            "folder": f"MES-AA/Profile/{alt_user_id}",
            "is_private_file": False,
            "use_unique_file_name": False,
        },
    )

    return uploaded_image["response"]["url"]


@router.post("/register/user", status_code=status.HTTP_201_CREATED)
async def create_user(
    prefix: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    mobile: str = Form(" "),
    birthday: str = Form(...),
    address1: str = Form(...),
    address2: str = Form(" "),
    city: str = Form(...),
    state: str = Form(...),
    pincode: str = Form(...),
    country: str = Form(...),
    duration_start: int = Form(...),
    duration_end: int = Form(...),
    course_puc: str = Form(" "),
    course_degree: str = Form(" "),
    course_pg: str = Form(" "),
    course_others: str = Form(" "),
    profession: str = Form(...),
    vision: str = Form(" "),
    other_interests: str = Form(" "),
    membership_type: str = Form(...),
    payment_mode: str = Form(...),
    images: Optional[List[UploadFile]] = Form([]),
    userDAL: UserDAL = Depends(get_user_dal),
):
    birthday = datetime.datetime.strptime(birthday, "%Y-%m-%d")
    birthday = birthday.date()

    # Check if email exists
    email_on_record = await userDAL.check_if_email_exists(email.lower())

    if email_on_record:
        raise HTTPException(
            status_code=403,
            detail=f"A registration for {email_on_record.email} already exists. Please use a different email address.",
        )

    # The alternate user id will be used in the urls for the id card and certificate
    alt_user_id = uuid.uuid4()

    # This field is required for annual memberships only
    membership_valid_upto = (
        datetime.date.today() + datetime.timedelta(days=365)
        if membership_type == "Annual"
        else None
    )

    id_card_url = f"/card/{alt_user_id}"

    # Populate this for life members only
    membership_certificate_url = (
        f"/certificate/{alt_user_id}" if membership_type == "Lifetime" else None
    )

    paid_amount = int(
        os.getenv("LIFETIME_MEMBERSHIP_AMOUNT")
        if membership_type == "Lifetime"
        else os.getenv("ANNUAL_MEMBERSHIP_AMOUNT")
    )

    if images:
        # image_url = upload_file_to_cloudinary(str(alt_user_id), images)
        image_url = upload_file_to_imagekit(str(alt_user_id), images)

    try:
        await userDAL.create_user(
            prefix.title(),
            first_name.title(),
            last_name.title(),
            email.lower(),
            mobile,
            birthday,
            address1.title(),
            address2.title(),
            city.title(),
            state.title(),
            pincode.upper(),
            country.title(),
            duration_start,
            duration_end,
            course_puc,
            course_degree,
            course_pg,
            course_others,
            vision,
            profession.title(),
            other_interests,
            membership_type,
            payment_mode,
            str(alt_user_id),
            membership_valid_upto,
            image_url,
            id_card_url,
            membership_certificate_url,
            paid_amount,
        )

        return {
            "prefix": prefix,
            "first_name": first_name,
            "last_name": last_name,
            "email": email.lower(),
            "mobile": mobile,
            "birthday": birthday,
            "address1": address1,
            "address2": address2,
            "city": city,
            "state": state,
            "pincode": pincode,
            "country": country,
            "duration_start": duration_start,
            "duration_end": duration_end,
            "course_puc": course_puc,
            "course_degree": course_degree,
            "course_pg": course_pg,
            "course_others": course_others,
            "vision": vision,
            "profession": profession,
            "other_interests": other_interests,
            "membership_type": membership_type,
            "alt_user_id": alt_user_id,
        }
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registration failed",
        )


@router.get("/user/{alt_id}", status_code=status.HTTP_200_OK)
async def get_user_from_email(alt_id: str, userDAL: UserDAL = Depends(get_user_dal)):
    record = await userDAL.get_user_details_for_alt_id(alt_id)
    if not record:
        return None

    membership_id = f"MESAA-{'LM' if record.membership_type == 'Lifetime' else 'OM'}-{str(record.duration_end)[-2:]}-{record.id}"

    return {
        "name": record.first_name + " " + record.last_name,
        "email": record.email,
        "membership_id": membership_id,
    }


@router.get("/card_details/{alt_user_id}", status_code=status.HTTP_200_OK)
async def get_user_details(alt_user_id: str, userDAL: UserDAL = Depends(get_user_dal)):
    record = await userDAL.get_user_details_for_alt_id(alt_user_id)

    if not record:
        return None

    membership_id = f"MESAA-{'LM' if record.membership_type == 'Lifetime' else 'OM'}-{str(record.duration_end)[-2:]}-{record.id}"

    return {
        "name": record.prefix + ". " + record.first_name + " " + record.last_name,
        "batch": record.duration_end,
        "course_puc": record.course_puc,
        "course_degree": record.course_degree,
        "course_pg": record.course_pg,
        "course_others": record.course_others,
        "membership_id": membership_id,
        "membership_start_date": record.date_created.strftime("%d-%b-%Y"),
        "membership_end_date": record.membership_valid_upto.strftime("%d-%m-%Y")
        if record.membership_type == "Annual"
        else None,
        "membership_type": record.membership_type,
        "profile_url": record.profile_url,
    }


@router.get("/user/id/{email}", status_code=status.HTTP_200_OK)
async def get_user_details_from_email(
    email: str, userDAL: UserDAL = Depends(get_user_dal)
):
    record = await userDAL.check_if_email_exists(email.lower())

    if not record:
        return None

    # Return nothing if the alumnus has chosen the online payment option
    if record.payment_mode == "O" or record.payment_status:
        return None

    membership_id = f"MESAA-{'LM' if record.membership_type == 'Lifetime' else 'OM'}-{str(record.duration_end)[-2:]}-{record.id}"

    alumnus_name = f"{record.prefix}. {record.first_name} {record.last_name}"

    return {
        "membership_id": membership_id,
        "membership_type": record.membership_type,
        "first_name": record.first_name,
        "full_name": alumnus_name,
        "email": record.email,
        "manual_payment_notification": record.manual_payment_notification,
    }


@router.get("/membership/{membership_id}", status_code=status.HTTP_200_OK)
async def get_user_details_from_membership_d(
    membership_id: str, userDAL: UserDAL = Depends(get_user_dal)
):
    user_id = int(membership_id.split("-")[3])

    record = await userDAL.get_user_details_for_id(user_id)

    membership_id = f"MESAA-{'LM' if record.membership_type == 'Lifetime' else 'OM'}-{str(record.duration_end)[-2:]}-{record.id}"

    return {
        "user_id": record.id,
        "membership_id": membership_id,
        "name": record.prefix + ". " + record.first_name + " " + record.last_name,
        "email": record.email,
        "membership_type": record.membership_type,
        "payment_status": record.payment_status,
    }


@router.put("/payment_status/{user_id}", status_code=status.HTTP_201_CREATED)
async def update_user_payment_status(
    user_id: int, userDAL: UserDAL = Depends(get_user_dal)
):
    await userDAL.update_payment_status(user_id)

    return "User details updated"


@router.put("/manual_payment/notification/{email}", status_code=status.HTTP_201_CREATED)
async def update_user_manual_payment_notification_status(
    email: str, userDAL: UserDAL = Depends(get_user_dal)
):
    await userDAL.update_manual_payment_notification(email)

    return "Manual payment notification sent"
