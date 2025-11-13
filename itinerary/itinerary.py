from fastapi import APIRouter, HTTPException, status
from typing import List

from pydantic import ValidationError
from itinerary.schema import ItinerariesResponseSchema, ItineraryCreateSchema, ItinerarySchema
from models import HotelDetail, Itinerary, ItineraryDay, Map, Tag
from functions import add_images_with_links, db_dependency
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from services.logger import logger

router = APIRouter(
    prefix="/itineraries",
    tags=["Itineraries"],
)

@router.get("/", response_model=ItinerariesResponseSchema)
async def get_itineraries(db: db_dependency):
    try:
        itineraries = (
            db.query(Itinerary)
            .options(
                selectinload(Itinerary.images),
                selectinload(Itinerary.days)
                    .selectinload(ItineraryDay.images),
                selectinload(Itinerary.days)
                    .selectinload(ItineraryDay.hotel_detail)
                    .selectinload(HotelDetail.images),
                selectinload(Itinerary.map)
                    .selectinload(Map.image),
                selectinload(Itinerary.tags)
            )
            .all()
        )

        return ItinerariesResponseSchema(
            itineraries=[ItinerarySchema.model_validate(item) for item in itineraries],
            total=len(itineraries)
        )
    
    except SQLAlchemyError as e:
    # Database-specific errors
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except ValidationError as e:
        # Pydantic validation errors
        logger.error(f"Data validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Data validation error"
        )
    except Exception as e:
        # Catch-all for other errors
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    
@router.get("/{slug}", response_model=ItinerarySchema)
async def get_itinerary(slug: str, db: db_dependency):
    try:
        logger.info(f"Fetching itinerary with slug: {slug}")
        itinerary = (
            db.query(Itinerary)
            .options(
                selectinload(Itinerary.images),
                selectinload(Itinerary.days)
                    .selectinload(ItineraryDay.images),
                selectinload(Itinerary.days)
                    .selectinload(ItineraryDay.hotel_detail)
                    .selectinload(HotelDetail.images),
                selectinload(Itinerary.map)
                    .selectinload(Map.image),
                selectinload(Itinerary.tags)
            )
            .filter(Itinerary.slug == slug)
            .first()
        )

        if not itinerary:
            logger.warning(f"Itinerary with slug '{slug}' not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Itinerary not found"
            )

        return ItinerarySchema.model_validate(itinerary)
    
    except SQLAlchemyError as e:
    # Database-specific errors
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except ValidationError as e:
        # Pydantic validation 
        logger.error(f"Data validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Data validation error"
        )
    except Exception as e:
        # Catch-all for other errors
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    
@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_itinerary(slug: str, db: db_dependency):
    try:
        itinerary = db.query(Itinerary).filter(Itinerary.slug == slug).first()

        if not itinerary:
            logger.warning(f"Itinerary with slug '{slug}' not found for deletion.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Itinerary not found"
            )

        db.delete(itinerary)
        db.commit()
        logger.info(f"Itinerary with slug '{slug}' deleted successfully.")
        return
    
    except SQLAlchemyError as e:
    # Database-specific errors
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        # Catch-all for other errors
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    
@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_itinerary(request: ItineraryCreateSchema, db: db_dependency):
    new_itinerary = Itinerary(
        title=request.title,
        overview=request.overview,
        duration=request.duration,
        arrival_city=request.arrival_city,
        departure_city=request.departure_city,
        accommodation=request.accommodation,
        location=request.location,
        discount=request.discount or 0,
        cost_inclusive=request.cost_inclusive,
        cost_exclusive=request.cost_exclusive,
    )
    db.add(new_itinerary)
    db.flush()

    # Add main itinerary images
    add_images_with_links(db, request.images, "itinerary", new_itinerary.id)

    # Add itinerary days and their images + hotel details
    for day in request.days or []:
        day_obj = ItineraryDay(
            day_number=day.day_number,
            title=day.title,
            description=day.description,
            itinerary=new_itinerary
        )
        db.add(day_obj)
        db.flush()
        add_images_with_links(db, day.images, "itinerary_day", day_obj.id)

        if day.hotel_detail:
            hotel = HotelDetail(
                name=day.hotel_detail.name,
                url=day.hotel_detail.url,
                day=day_obj
            )
            db.add(hotel)
            db.flush()
            add_images_with_links(db, day.hotel_detail.images, "hotel_detail", hotel.id)

    # Add map (single image)
    if request.map and request.map.image:
        map_obj = Map(itinerary=new_itinerary)
        db.add(map_obj)
        db.flush()
        add_images_with_links(db, [request.map.image], "map", map_obj.id)

    # Add tags
    for tag in request.tags or []:
        tag_obj = Tag(item=tag.item, itinerary=new_itinerary)
        db.add(tag_obj)

    db.commit()
    db.refresh(new_itinerary)

    return {"message": "Itinerary created successfully", "itinerary_id": new_itinerary.id}
