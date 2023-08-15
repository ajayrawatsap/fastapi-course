from typing import List
from fastapi import status
from app import schemas, models
from . conftest import create_post


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


def test_create_post_unauthorized(test_user, client):
    # create_authorized_user("testpost@gmail.com", "pass123", session)

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

    # new_post1 = {
    #     "title": "New Post 1 For Test",
    #     "content": "Post 1Created For Testing",
    #     "published": True,
    #     "owner_id": test_user['id']
    # }

    # print(test_post)
    post_new = test_post["post1"]

    res = authorized_client.get(f"/post/{ post_new.id}")

    post_out = schemas.Post(**res.json())

    assert res.status_code == status.HTTP_200_OK
    assert post_new.owner_id == post_out.owner.id


def test_get_one_post_for_other_user_fail(test_user, test_user2, authorized_client, session):
    """
    User should not get post for other user
    """

    new_post1 = {
        "title": "New Post 1 For User 1",
        "content": "Post 1Created For Testing",
        "published": True,
        "owner_id": test_user['id']
    }

    post_new1 = create_post(session, new_post1)

    new_post2 = {
        "title": "New Post 2 For User 2",
        "content": "Post 1Created For Testing",
        "published": True,
        "owner_id": test_user2['id']
    }

    post_new2 = create_post(session, new_post2)

    res = authorized_client.get(f"/post/{ post_new2.id}")
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_get_one_post_do_not_exist(test_user, authorized_client):
    """
    User cannot get a post which do not exist
    """
    res = authorized_client.get(f"/post/{99999}")
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_get_one_post_unauthorized(test_user, client, session):
    """
    Unautorized user cannot get a post
    """
    new_post1 = {
        "title": "New Post 1 For User 1",
        "content": "Post 1 Created For Testing",
        "published": True,
        "owner_id": test_user['id']
    }

    post_new1 = create_post(session, new_post1)
    res = client.get(f"/post/{post_new1.id}")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_post_success(test_user, authorized_client, session):
    new_post = {
        "title": "New Post 1 For User 1",
        "content": "Post 1 Created For Testing",
        "published": True,
        "owner_id": test_user['id']
    }

    post_new = create_post(session, new_post)
    res = authorized_client.delete(f"/post/{ post_new.id}")
    assert res.status_code == status.HTTP_204_NO_CONTENT


def test_delete_post_unathorized(test_user, client, session):
    new_post = {
        "title": "New Post 1 For User 1",
        "content": "Post 1 Created For Testing",
        "published": True,
        "owner_id": test_user['id']
    }

    post_new = create_post(session, new_post)
    res = client.delete(f"/post/{ post_new.id}")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_post_not_exists_fail(test_user, authorized_client, session):
    new_post = {
        "title": "New Post 1 For User 1",
        "content": "Post 1 Created For Testing",
        "published": True,
        "owner_id": test_user['id']
    }

    post_new = create_post(session, new_post)
    res = authorized_client.delete(f"/post/{99999}")
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_delete_post_for_other_user_fail(test_user, test_user2, authorized_client, session):
    new_post = {
        "title": "New Post 1 For User 1",
        "content": "Post 1 Created For Testing",
        "published": True,
        "owner_id": test_user2['id']
    }

    post_new = create_post(session, new_post)
    res = authorized_client.delete(f"/post/{post_new.id}")
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_update_post_success(test_user, authorized_client, session):
    new_post = {
        "title": "New Post 1 For User 1",
        "content": "Post 1 Created For Testing",
        "published": True,
        "owner_id": test_user['id']
    }

    post_new = create_post(session, new_post)

    updated_post = {
        "title": "Updated Title",
        "content": "Updated Content",
        "published": False
    }

    res = authorized_client.put(f"/post/{ post_new.id}", json=updated_post)

    updated_post_resp = schemas.Post(**res.json())
    assert updated_post_resp.title == updated_post["title"]
    assert updated_post_resp.content == updated_post["content"]
    assert updated_post_resp.published == updated_post["published"]
    assert res.status_code == status.HTTP_200_OK


def test_update_post_unauthorized(test_user, client, session):
    new_post = {
        "title": "New Post 1 For User 1",
        "content": "Post 1 Created For Testing",
        "published": True,
        "owner_id": test_user['id']
    }

    post_new = create_post(session, new_post)

    updated_post = {
        "title": "Updated Title",
        "content": "Updated Content",
        "published": False
    }

    res = client.put(f"/post/{ post_new.id}", json=updated_post)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_post_do_not_exist_fail(test_user, authorized_client, session):

    updated_post = {
        "title": "Updated Title",
        "content": "Updated Content",
        "published": False
    }

    res = authorized_client.put(f"/post/{66666}", json=updated_post)
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_update_post_for_other_user_fail(test_user, test_user2, authorized_client, session):
    new_post = {
        "title": "New Post 1 For User 1",
        "content": "Post 1 Created For Testing",
        "published": True,
        "owner_id": test_user2['id']
    }

    post_new = create_post(session, new_post)

    updated_post = {
        "title": "Updated Title",
        "content": "Updated Content",
        "published": False
    }

    res = authorized_client.put(f"/post/{ post_new.id}", json=updated_post)

    assert res.status_code == status.HTTP_403_FORBIDDEN
