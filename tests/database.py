import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import create_engine
from app.config import settings
from sqlalchemy.orm import sessionmaker
from app.database import get_db, Base

SQLALCHEMY_DB_URL = (f'postgresql://'
                     f'{settings.database_username}:{settings.database_password}'
                     f'@{settings.database_hostname}:{settings.database_port}'
                     f'/{settings.test_database_name}')

engine = create_engine(SQLALCHEMY_DB_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session():
    # Delete all Test Tables
    Base.metadata.drop_all(bind=engine)
    # Create Tables
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
