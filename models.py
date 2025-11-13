from datetime import datetime
import re
import uuid
from typing import List, Optional
from sqlalchemy import JSON, Integer, String, ForeignKey, event, and_, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, foreign

def generate_id(prefix: str) -> str:
    uuid_str = str(uuid.uuid4()).replace("-", "")[:8].upper()
    return f"{prefix}-{uuid_str}"


def slugify(value: str) -> str:
    """Converts a string to a URL-safe slug."""
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    value = re.sub(r"[-\s]+", "-", value)
    return value

class Base(DeclarativeBase):
    pass

# --------------------------------------
# Universal Image Table
# --------------------------------------
class Image(Base):
    __tablename__ = "images"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True, unique=True, default=lambda: generate_id("IMG"))
    url: Mapped[str] = mapped_column(String, nullable=False)
    public_id: Mapped[str] = mapped_column(String, nullable=False)

    # Backref to all links (Itinerary, Map, etc.)
    links: Mapped[List["ImageLink"]] = relationship("ImageLink", back_populates="image", cascade="all, delete")


# --------------------------------------
# Universal Image Linker (Polymorphic)
# --------------------------------------
class ImageLink(Base):
    __tablename__ = "image_links"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True, unique=True, default=lambda: generate_id("IMGLNK"))
    image_id: Mapped[str] = mapped_column(String, ForeignKey("images.id", ondelete="CASCADE"))
    entity_type: Mapped[str] = mapped_column(String, nullable=False)  # e.g. "itinerary", "map"
    entity_id: Mapped[str] = mapped_column(String, nullable=False)     # the actual ID of the entity

    image: Mapped["Image"] = relationship("Image", back_populates="links")

# --------------------------------------
# Models
# --------------------------------------
class Itinerary(Base):
    __tablename__ = "itineraries"

    id: Mapped[str] = mapped_column(String, primary_key=True, unique=True, index=True, default=lambda: generate_id("ITI"))
    title: Mapped[str] = mapped_column(String, nullable=False)
    overview: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    arrival_city: Mapped[str] = mapped_column(String, nullable=False)
    departure_city: Mapped[str] = mapped_column(String, nullable=False)
    accommodation: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    discount: Mapped[int] = mapped_column(Integer, default=0)
    cost_inclusive: Mapped[List[dict]] = mapped_column(JSON, nullable=True)
    cost_exclusive: Mapped[List[dict]] = mapped_column(JSON, nullable=True)

    images: Mapped[List["Image"]] = relationship(
        "Image",
        secondary="image_links",
        primaryjoin=and_(
            foreign(ImageLink.entity_id) == id,
            ImageLink.entity_type == 'itinerary'
        ),
        secondaryjoin=foreign(ImageLink.image_id) == Image.id,
        viewonly=True,
    )
    days: Mapped[List["ItineraryDay"]] = relationship("ItineraryDay", back_populates="itinerary", cascade="all, delete-orphan")
    map: Mapped[Optional["Map"]] = relationship("Map", back_populates="itinerary", uselist=False, cascade="all, delete-orphan")
    tags: Mapped[List["Tag"]] = relationship("Tag", back_populates="itinerary", cascade="all, delete-orphan")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


# Insert event
@event.listens_for(Itinerary, "before_insert")
def create_itinerary_slug(mapper, connection, target):
    if target.title and not target.slug:
        target.slug = slugify(target.title)

# Update event
@event.listens_for(Itinerary, "before_update")
def update_itinerary_slug(mapper, connection, target):
    if target.title:
        target.slug = slugify(target.title)

class Map(Base):
    __tablename__ = "maps"

    id: Mapped[str] = mapped_column(String, primary_key=True, unique=True, index=True, default=lambda: generate_id("MAP"))

    # Foreign key to link to Itinerary
    itinerary_id: Mapped[str] = mapped_column(String, ForeignKey("itineraries.id"), nullable=False)

    # Bidirectional relationship
    itinerary: Mapped["Itinerary"] = relationship("Itinerary", back_populates="map")

    # Single image relationship
    image: Mapped[Optional["Image"]] = relationship(
        "Image",
        secondary="image_links",
        primaryjoin=and_(
            foreign(ImageLink.entity_id) == id,
            ImageLink.entity_type == 'map'
        ),
        secondaryjoin=foreign(ImageLink.image_id) == Image.id,
        uselist=False,  # Ensures only one image is returned
        viewonly=True,
    )

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True, unique=True, default=lambda: generate_id("TAG"))
    item: Mapped[str] = mapped_column(String, nullable=False)
    itinerary_id: Mapped[str] = mapped_column(String, ForeignKey("itineraries.id"), nullable=False)

    itinerary: Mapped["Itinerary"] = relationship("Itinerary", back_populates="tags")

class ItineraryDay(Base):
    __tablename__ = "itinerary_days"

    id: Mapped[str] = mapped_column(String, primary_key=True, unique=True, index=True, default=lambda: generate_id("ITIDY"))
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    itinerary_id: Mapped[str] = mapped_column(String, ForeignKey("itineraries.id"), nullable=False)

    itinerary: Mapped["Itinerary"] = relationship("Itinerary", back_populates="days")

    images: Mapped[List["Image"]] = relationship(
        "Image",
        secondary="image_links",
        primaryjoin=and_(
            foreign(ImageLink.entity_id) == id,
            ImageLink.entity_type == 'itinerary_day'
        ),
        secondaryjoin=foreign(ImageLink.image_id) == Image.id,
        viewonly=True,
    )

    hotel_detail: Mapped[Optional["HotelDetail"]] = relationship(
        "HotelDetail", back_populates="day", uselist=False, cascade="all, delete-orphan"
    )


class HotelDetail(Base):
    __tablename__ = "hotel_details"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True, unique=True, default=lambda: generate_id("HOTEL"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=True)
    day_id: Mapped[str] = mapped_column(String, ForeignKey("itinerary_days.id"), nullable=True)

    day: Mapped[Optional["ItineraryDay"]] = relationship("ItineraryDay", back_populates="hotel_detail")

    images: Mapped[List["Image"]] = relationship(
        "Image",
        secondary="image_links",
        primaryjoin=and_(
            foreign(ImageLink.entity_id) == id,
            ImageLink.entity_type == 'hotel_detail'
        ),
        secondaryjoin=foreign(ImageLink.image_id) == Image.id,
        viewonly=True,
    )

