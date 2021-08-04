import random
import secrets

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel
from sentry_sdk import capture_exception

from . import get_testimonial_dal
from . import router
from database.data_access.testimonialDAL import TestimonialDAL


class TestimonialCreate(BaseModel):
    name: str
    batch: str
    message: str

    class Config:
        orm_mode = True


@router.get("/testimonials", status_code=status.HTTP_200_OK)
async def get_testimonias(
    testimonial_dal: TestimonialDAL = Depends(get_testimonial_dal),
):
    try:
        results = await testimonial_dal.fetch_all_testimonials()

        testimonials = []
        testimonial_dict = {}

        for result in results:
            obj = result
            testimonial_dict["name"] = obj.name
            testimonial_dict["initial"] = obj.name[0].upper()
            testimonial_dict["batch"] = obj.batch
            testimonial_dict["message"] = obj.message

            testimonials.append(testimonial_dict.copy())

        return random.sample(testimonials, k=6)
    except Exception as e:
        capture_exception(e)


@router.get("/testimonials/all", status_code=status.HTTP_200_OK)
async def get_all_testimonias(
    testimonial_dal: TestimonialDAL = Depends(get_testimonial_dal),
):
    try:
        return await testimonial_dal.fetch_all_testimonials()
    except Exception as e:
        capture_exception(e)


@router.post("/testimonials/create", status_code=status.HTTP_201_CREATED)
async def create_new_testimonial(
    testimonial: TestimonialCreate,
    testimonial_dal: TestimonialDAL = Depends(get_testimonial_dal),
):
    hash_value = secrets.token_hex(50)

    try:
        return await testimonial_dal.create_testimonial(
            testimonial.name.title(),
            testimonial.batch,
            testimonial.message,
            False,
            hash_value,
        )
    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create testimonial"
        )


@router.get("/testimonial/verify/{testimonial_hash}", status_code=status.HTTP_200_OK)
async def verify_testimonial(
    testimonial_hash: str,
    testimonial_dal: TestimonialDAL = Depends(get_testimonial_dal),
):
    verification_hash, testimonial_id = testimonial_hash.split("+")

    try:
        record = await testimonial_dal.verify_if_testimonial_exists(
            verification_hash, int(testimonial_id)
        )

        if record:
            await testimonial_dal.update_testimonial_verification_status(
                verification_hash
            )
            return "Testimonial verified"
        else:
            return "Could not verify this testimonial"
    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while verifying testimonial",
        )
