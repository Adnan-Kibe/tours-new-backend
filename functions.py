from typing import Annotated
from fastapi import Depends, HTTPException, status
from database import get_session
from sqlalchemy.orm import Session

db_dependency = Annotated[Session, Depends(get_session)]