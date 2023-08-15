"""
This file is automatically called by Pytest 
The fixtures that you will define will be shared among all tests in your test suite.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import create_engine
from app.config import settings
from sqlalchemy.orm import sessionmaker
from app.database import get_db, Base
from app import models, schemas
from app.oauth2 import create_access_token
from typing import Dict

SQLALCHEMY_DB_URL = (f'postgresql://'
                     f'{settings.database_username}:{settings.database_password}'
                     f'@{settings.database_hostname}:{settings.database_port}'
                     f'/{settings.test_database_name}')

engine = create_engine(SQLALCHEMY_DB_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


def create_user(client, email, password) -> dict:
    user_data = {"email": email,
                 "password": password}
    res = client.post("/users/", json=user_data)

    assert res.status_code == status.HTTP_201_CREATED

    new_user = res.json()
    new_user['password'] = user_data['password']

    return new_user


def create_post(session, post: dict):
    new_post = models.Post(**post)
    session.add(new_post)
    session.commit()
    session.refresh(new_post)
    return new_post


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


@pytest.fixture
def test_user(client):

    return create_user(client, email="testuser@gmail.com",
                       password="password123")


@pytest.fixture
def test_user2(client):

    return create_user(client, email="anontheruser@gmail.com",
                       password="pass123")


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client


@pytest.fixture
def test_post(test_user: dict, test_user2: dict,
              session) -> Dict[str, models.Post]:
    posts = {}
    new_post1 = {
        "title": "New Post 1 For Test",
        "content": "Post 1Created For Testing",
        "published": True,
        "owner_id": test_user['id']
    }

    post1 = create_post(session, new_post1)
    posts['post1_user1'] = post1

    new_post2 = {
        "title": "New Post 2 For Test",
        "content": "Post 2Created For Testing",
        "published": False,
        "owner_id": test_user['id']
    }

    post2 = create_post(session, new_post2)
    posts['post2_user1'] = post2

    new_post3 = {
        "title": "New Post 3 For Test",
        "content": "Post 3 Created For Testing",
        "published": False,
        "owner_id": test_user2['id']
    }

    post3 = create_post(session, new_post3)
    posts['post_user2'] = post3

    return posts
