from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

SQLALCHEMY_DB_URL = (f'postgresql://'
                     f'{settings.database_username}:{settings.database_password}'
                     f'@{settings.database_hostname}:{settings.database_port}'
                     f'/{settings.database_name}')

print("*****************************************", SQLALCHEMY_DB_URL)

engine = create_engine(SQLALCHEMY_DB_URL)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
