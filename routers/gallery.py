import os

import cloudinary.api
from fastapi import status

from . import router


@router.get("/gallery/images/all", status_code=status.HTTP_200_OK)
async def get_images_for_gallery():
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    )

    return cloudinary.api.resources(
        prefix="MES-AA/main_gallery", type="upload", context=True, max_results=100
    )

    # return await gallery_DAL.fetch_all_images_for_gallery()
