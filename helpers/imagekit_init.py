import os

from imagekitio import ImageKit


def initialize_imagekit():
    return ImageKit(
        private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
        public_key=os.getenv("IMAGEKIT_PUBLIC_KEY"),
        url_endpoint=os.getenv("IMAGEKIT_URL_ENDPOINT"),
    )


def initialize_imagekit_prod():
    return ImageKit(
        private_key=os.getenv("IMAGEKIT_PRIVATE_KEY_PROD"),
        public_key=os.getenv("IMAGEKIT_PUBLIC_KEY_PROD"),
        url_endpoint=os.getenv("IMAGEKIT_URL_ENDPOINT_PROD"),
    )
