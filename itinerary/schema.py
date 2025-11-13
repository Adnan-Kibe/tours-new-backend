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
    name: Optional[str]
    images: List[ImageSchema] = []

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
    cost_inclusive: Optional[List[dict]] = []
    cost_exclusive: Optional[List[dict]] = []
    images: List[ImageSchema] = []
    days: List[ItineraryDaySchema] = []
    map: Optional[MapSchema]
    tags: List[TagSchema] = []

    class Config:
        from_attributes = True

# ----------------------------
# Response Wrapper
# ----------------------------
class ItinerariesResponseSchema(BaseModel):
    itineraries: List[ItinerarySchema]
    total: int
