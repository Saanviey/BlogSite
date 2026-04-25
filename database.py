from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , DeclarativeBase

db_url = "sqlite:///./blog.db"

engine= create_engine(db_url , connect_args={"check_same_thread" : False})

SessionLocal = sessionmaker( autoflush=False ,bind=engine , autocommit = False)


class Base(DeclarativeBase):
    pass


def get_db():
    db= SessionLocal()

    try:
        yield db
    finally:
        db.close()    
