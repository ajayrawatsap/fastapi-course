from typing import List
from fastapi import status
from app import schemas, models


def test_create_post_sucessfull(test_user, authorized_client):

    new_post = {
        "title": "New Post For Test",
        "content": "Created For Testing",
        "published": True
    }

    response = authorized_client.post('/posts', json=new_post)
    post_created = schemas.Post(**response.json())

    assert post_created.title == new_post['title']
    assert post_created.content == new_post['content']
    assert post_created.published == new_post['published']
    assert post_created.owner.id == test_user['id']
    assert response.status_code == status.HTTP_201_CREATED


def test_create_post_unauthorized(client):

    new_post = {
        "title": "New Post For Test",
        "content": "Created For Testing",
        "published": True}

    response = client.post('/posts', json=new_post)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_posts_for_user_sucesfully(test_user, test_post, authorized_client):
    """
    Only posts created by a user should be retrieved
    """

    res = authorized_client.get('/posts')
    result: List = res.json()

    assert len(result) == 2

    for post in result:
        assert post['owner']['id'] == test_user['id']

    assert res.status_code == status.HTTP_200_OK


def test_get_posts_for_unauthorized_user(test_user, test_post, client):
    """
    User not autheticated should not be able to retrieve posts
    """

    res = client.get('/posts')
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_one_post_succesfully(test_user, test_post, authorized_client, session):
    """
    Retreive a single post created by a user    
    """

    post_test_user = test_post["post1_user1"]

    res = authorized_client.get(f"/post/{ post_test_user.id}")

    post_out = schemas.Post(**res.json())

    assert res.status_code == status.HTTP_200_OK
    assert post_test_user.owner_id == post_out.owner.id


def test_get_one_post_for_other_user_fail(test_post, authorized_client):
    """
    User should not get post for other user
    """

    post_test_user2 = test_post["post_user2"]

    res = authorized_client.get(f"/post/{ post_test_user2.id}")
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_get_one_post_do_not_exist(authorized_client):
    """
    User cannot get a post which do not exist
    """
    res = authorized_client.get(f"/post/{99999}")
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_get_one_post_unauthorized(test_post, client):
    """
    Unautorized user cannot get a post
    """

    post_test_user = test_post["post1_user1"]
    res = client.get(f"/post/{post_test_user.id}")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_post_success(test_post, authorized_client):

    post_test_user = test_post["post1_user1"]

    res = authorized_client.delete(f"/post/{ post_test_user.id}")
    assert res.status_code == status.HTTP_204_NO_CONTENT


def test_delete_post_unathorized(test_post, client):

    post_test_user = test_post["post1_user1"]
    res = client.delete(f"/post/{ post_test_user.id}")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_post_not_exists_fail(authorized_client):

    res = authorized_client.delete(f"/post/{99999}")
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_delete_post_for_other_user_fail(test_post, authorized_client):

    post_test_user2 = test_post["post_user2"]
    res = authorized_client.delete(f"/post/{post_test_user2.id}")
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_update_post_success(test_post, authorized_client):
    post_test_user = test_post["post1_user1"]

    updated_post = {
        "title": "Updated Title",
        "content": "Updated Content",
        "published": False
    }

    res = authorized_client.put(
        f"/post/{ post_test_user.id}", json=updated_post)

    updated_post_resp = schemas.Post(**res.json())
    assert updated_post_resp.title == updated_post["title"]
    assert updated_post_resp.content == updated_post["content"]
    assert updated_post_resp.published == updated_post["published"]
    assert res.status_code == status.HTTP_200_OK


def test_update_post_unauthorized(test_post, client):
    post_test_user = test_post["post1_user1"]

    updated_post = {
        "title": "Updated Title",
        "content": "Updated Content",
        "published": False
    }

    res = client.put(f"/post/{ post_test_user.id}", json=updated_post)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_post_do_not_exist_fail(authorized_client):

    updated_post = {
        "title": "Updated Title",
        "content": "Updated Content",
        "published": False
    }

    res = authorized_client.put(f"/post/{66666}", json=updated_post)
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_update_post_for_other_user_fail(test_post, authorized_client):
    post_test_user2 = test_post["post_user2"]

    updated_post = {
        "title": "Updated Title",
        "content": "Updated Content",
        "published": False
    }

    res = authorized_client.put(
        f"/post/{ post_test_user2.id}", json=updated_post)

    assert res.status_code == status.HTTP_403_FORBIDDEN
