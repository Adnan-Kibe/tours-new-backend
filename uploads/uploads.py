# routes/uploads.py
from fastapi import APIRouter
from datetime import datetime
import os
import cloudinary
import cloudinary.utils
from dotenv import load_dotenv

from uploads.schema import SignatureResponseSchema

load_dotenv()

router = APIRouter(prefix="/uploads", tags=["Uploads"])

@router.get("/signature", response_model=SignatureResponseSchema)
async def get_upload_signature():
    """
    Generates a signed upload signature for Cloudinary without using an upload preset.
    You can specify folder and transformations directly.
    """
    timestamp = int(datetime.now().timestamp())

    params_to_sign = {
        "timestamp": timestamp,
        "folder": "itineraries",                     
    }

    signature = cloudinary.utils.api_sign_request(
        params_to_sign,
        os.getenv("CLOUDINARY_API_SECRET")
    )

    return {
        "cloud_name": os.getenv("CLOUDINARY_CLOUD_NAME"),
        "api_key": os.getenv("CLOUDINARY_API_KEY"),
        "timestamp": timestamp,
        "signature": signature,
        "folder": "itineraries",
        "resource_type": "image"
    }
