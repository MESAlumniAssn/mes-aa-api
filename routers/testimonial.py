import random

from fastapi import Depends
from fastapi import status

from . import get_testimonial_dal
from . import router
from database.data_access.testimonialDAL import TestimonialDAL


@router.get("/testimonials", status_code=status.HTTP_200_OK)
async def get_testimonias(
    testimonial_dal: TestimonialDAL = Depends(get_testimonial_dal),
):
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


@router.get("/testimonials/all", status_code=status.HTTP_200_OK)
async def get_all_testimonias(
    testimonial_dal: TestimonialDAL = Depends(get_testimonial_dal),
):
    return await testimonial_dal.fetch_all_testimonials()
