import pytest
from jose import jwt
from fastapi import status
from app import schemas
from app.config import settings


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


def test_login_sucessfull(client, test_user: dict):

    user_login = {
        "username": test_user['email'],
        "password": test_user['password']
    }
    res = client.post("/login", data=user_login)

    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token,
                         settings.secret_key, algorithms=[settings.algorithm])
    id: int = payload.get("user_id")

    assert test_user['id'] == id
    assert login_res.token_type == "bearer"
    assert res.status_code == status.HTTP_200_OK


@pytest.mark.parametrize("email, password, status_code", [
    ("dummytest@gmail.com",  "wrongpass", status.HTTP_403_FORBIDDEN),
    ("wromgemail@gmail.com",  "password123", status.HTTP_403_FORBIDDEN),
    ("dummytest@gmail.com",    None, status.HTTP_422_UNPROCESSABLE_ENTITY),
    (None,  "password123", status.HTTP_422_UNPROCESSABLE_ENTITY),
    ("wromgemail@gmail.com",  "wrongpass", status.HTTP_403_FORBIDDEN),
    ("testuser@gmail.com", "password123", status.HTTP_200_OK)
])
def test_incorrect_login(client, test_user, email, password, status_code):

    user_login = {
        "username": email,
        "password": password
    }

    res = client.post("/login", data=user_login)

    assert res.status_code == status_code


def test_get_logged_user(client, test_user):

    user_login = {
        "username": test_user['email'],
        "password": test_user['password']
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
    assert logged_user.email == test_user['email']
    # assert res.status_code == status.HTTP_200_OK
    assert res.status_code == 201
