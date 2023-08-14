import pytest
from jose import jwt
from fastapi import status
from app import schemas, models, utils
from .database import client, session
from app.config import settings


def create_new_user(email, password, session):
    new_user = models.User(email=email, password=utils.hash(password))
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


def test_root(client):
    res = client.get("/")

    assert res.json() == {"message": "Hello World 123"}
    assert res.status_code == status.HTTP_200_OK


def test_create_user_with_sucess(client):
    user = {
        "email": "dummytest@gmail.com",
        "password": "pass123"
    }

    res = client.post("/users", json=user)

    new_user = schemas.UserOut(**res.json())

    assert new_user.email == "dummytest@gmail.com"
    assert res.status_code == status.HTTP_201_CREATED


def test_create_user_with_invalid_email(client):
    user = {
        "email": "dummytestgmail.com",
        "password": "pass123"
    }
    res = client.post("/users", json=user)
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_sucessfull(client, session):

    new_user = create_new_user("dummytest@gmail.com", "pass123", session)

    user_login = {
        "username": "dummytest@gmail.com",
        "password": "pass123"
    }
    res = client.post("/login", data=user_login)

    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token,
                         settings.secret_key, algorithms=[settings.algorithm])
    id: int = payload.get("user_id")

    assert new_user.id == id
    assert login_res.token_type == "bearer"
    assert res.status_code == status.HTTP_200_OK


@pytest.mark.parametrize("email, password, status_code", [
    ("dummytest@gmail.com",  "wrongpass", status.HTTP_403_FORBIDDEN),
    ("wromgemail@gmail.com",  "pass123", status.HTTP_403_FORBIDDEN),
    ("dummytest@gmail.com",    None, status.HTTP_422_UNPROCESSABLE_ENTITY),
    (None,  "pass123", status.HTTP_422_UNPROCESSABLE_ENTITY),
    ("wromgemail@gmail.com",  "wrongpass", status.HTTP_403_FORBIDDEN),
])
def test_login_fail(client, session, email, password, status_code):

    create_new_user("dummytest@gmail.com", "pass123", session)

    user_login = {
        "username": email,
        "password": password
    }

    res = client.post("/login", data=user_login)

    assert res.status_code == status_code


def test_get_logged_user(client, session):
    create_new_user("dummytest@gmail.com", "pass123", session)

    user_login = {
        "username": "dummytest@gmail.com",
        "password": "pass123"
    }
    res = client.post("/login", data=user_login)
    login_res = schemas.Token(**res.json())
    token = login_res.access_token
    token_type = login_res.token_type

    headers = {
        'Authorization': f'{token_type} {token}'
    }

    res_me = client.get("/users/me", headers=headers)
    logged_user = schemas.UserOut(**res_me.json())

    # print(res_me.json())
    assert logged_user.email == "dummytest@gmail.com"
    assert res.status_code == status.HTTP_200_OK
