import os
from typing import Annotated
from fastapi import Depends, HTTPException, status
from database import get_session
from sqlalchemy.orm import Session
import cloudinary

db_dependency = Annotated[Session, Depends(get_session)]

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)