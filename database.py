from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Base

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def initialize_database():
    Base.metadata.create_all(bind=engine)

def get_session():
    with Session(engine) as session:
        yield session