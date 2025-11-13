from fastapi import APIRouter, HTTPException, status
from typing import List

from pydantic import ValidationError
from itinerary.schema import ItinerariesResponseSchema, ItinerarySchema
from models import HotelDetail, Itinerary, ItineraryDay, Map
from functions import db_dependency
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
                    .selectinload(Map.images),
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
                    .selectinload(Map.images),
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