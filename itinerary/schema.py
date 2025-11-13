from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

# ----------------------------
# Image Schema
# ----------------------------
class ImageSchema(BaseModel):
    id: str
    url: str
    public_id: str

    class Config:
        from_attributes = True

# ----------------------------
# Hotel Detail Schema
# ----------------------------
class HotelDetailSchema(BaseModel):
    id: str
    name: str
    url: Optional[str]
    images: List[ImageSchema] = []

    class Config:
        from_attributes = True

# ----------------------------
# Itinerary Day Schema
# ----------------------------
class ItineraryDaySchema(BaseModel):
    id: str
    day_number: int
    title: str
    description: str
    images: List[ImageSchema] = []
    hotel_detail: Optional[HotelDetailSchema]

    class Config:
        from_attributes = True

# ----------------------------
# Map Schema
# ----------------------------
class MapSchema(BaseModel):
    id: str
    images: Optional[ImageSchema] = None

    class Config:
        from_attributes = True

# ----------------------------
# Tag Schema
# ----------------------------
class TagSchema(BaseModel):
    id: str
    item: str

    class Config:
        from_attributes = True

# ----------------------------
# Itinerary Schema
# ----------------------------
class ItinerarySchema(BaseModel):
    id: str
    title: str
    overview: str
    slug: str
    duration: int
    arrival_city: str
    departure_city: str
    accommodation: str
    location: str
    discount: int
    price: int
    cost_inclusive: Optional[List[dict]] = []
    cost_exclusive: Optional[List[dict]] = []
    images: List[ImageSchema] = []
    days: List[ItineraryDaySchema] = []
    map: Optional[MapSchema]
    tags: List[TagSchema] = []
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------------------
# Response Wrapper
# ----------------------------
class ItinerariesResponseSchema(BaseModel):
    itineraries: List[ItinerarySchema]
    total: int

class ImageCreateSchema(BaseModel):
    url: str
    public_id: str

class HotelDetailCreateSchema(BaseModel):
    name: str
    url: Optional[str] = None
    images: Optional[List[ImageCreateSchema]] = []

class ItineraryDayCreateSchema(BaseModel):
    day_number: int
    title: str
    description: str
    hotel_detail: Optional[HotelDetailCreateSchema] = None
    images: Optional[List[ImageCreateSchema]] = []

class MapCreateSchema(BaseModel):
    # Only a single image for the map
    image: Optional[ImageCreateSchema] = None

class TagCreateSchema(BaseModel):
    item: str

class ItineraryCreateSchema(BaseModel):
    title: str
    overview: str
    duration: int
    arrival_city: str
    departure_city: str
    accommodation: str
    location: str
    discount: Optional[int] = 0
    price: int
    cost_inclusive: Optional[List[dict]] = []
    cost_exclusive: Optional[List[dict]] = []

    # Nested relationships
    days: Optional[List[ItineraryDayCreateSchema]] = []
    map: Optional[MapCreateSchema] = None
    tags: Optional[List[TagCreateSchema]] = []
    images: Optional[List[ImageCreateSchema]] = []

