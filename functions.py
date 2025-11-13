import os
from typing import Annotated, List, Protocol, Sequence
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from database import get_session
from sqlalchemy.orm import Session
import cloudinary

from itinerary.schema import ImageCreateSchema
from models import Image, ImageLink

db_dependency = Annotated[Session, Depends(get_session)]

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


# Protocol to accept any object with url and public_id
class ImageLike(Protocol):
    url: str
    public_id: str

def add_images_with_links(db: Session, images: Sequence[ImageLike] | None, entity_type: str, entity_id: str):
    """
    Create Image objects and link them to an entity using ImageLink.
    """
    for img in images or []:
        image_obj = Image(url=img.url, public_id=img.public_id)
        db.add(image_obj)
        db.flush()  
        link = ImageLink(
            image_id=image_obj.id,
            entity_type=entity_type,
            entity_id=entity_id
        )
        db.add(link)