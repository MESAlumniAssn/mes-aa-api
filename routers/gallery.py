from fastapi import status

from . import router
from helpers.imagekit_init import initialize_imagekit

# import cloudinary.api


@router.get("/gallery/images/all", status_code=status.HTTP_200_OK)
async def get_images_for_gallery():
    # cloudinary.config(
    #     cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    #     api_key=os.getenv("CLOUDINARY_API_KEY"),
    #     api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    # )

    # return cloudinary.api.resources(
    #     prefix="MES-AA/main_gallery", type="upload", context=True, max_results=100
    # )

    transformed_files = []
    file_obj = {}

    imagekit = initialize_imagekit()

    files = imagekit.list_files({"path": "MES-AA/Gallery", "limit": 100})

    for file in files["response"]:
        file_url = imagekit.url(
            {
                "src": file["url"],
                "transformation": [{"quality": "90"}],
            }
        )

        file_url = file_url.split("?")

        file_obj["url"] = file_url[0]
        file_obj["fileId"] = file["fileId"]
        file_obj["height"] = file["height"]
        file_obj["width"] = file["width"]

        transformed_files.append(file_obj.copy())

    return transformed_files[::-1]
    # return await gallery_DAL.fetch_all_images_for_gallery()
