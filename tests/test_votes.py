
from fastapi import status


def test_create_vote_success(test_post, authorized_client):
    post_test_user = test_post["post1_user1"]
    post_id = post_test_user.id
    payload = {
        "post_id": post_id,
        "dir": 1
    }

    res = authorized_client.post("/vote", json=payload)
    assert res.status_code == status.HTTP_201_CREATED

    payload = {
        "post_id": post_id,
        "dir": 0
    }

    res = authorized_client.post("/vote", json=payload)
    assert res.status_code == status.HTTP_201_CREATED


def test_create_vote_unauthorized(test_post, client):
    post_test_user = test_post["post1_user1"]

    payload = {
        "post_id": post_test_user.id,
        "dir": 1
    }

    res = client.post("/vote", json=payload)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_vote_non_existing_post_fail(authorized_client):

    payload = {
        "post_id": 1,
        "dir": 1
    }

    res = authorized_client.post("/vote", json=payload)
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_create_vote_duplicate_fail(test_post, authorized_client):
    """
    A user cannot vote for same post multiple times
    """
    post_test_user = test_post["post1_user1"]
    post_id = post_test_user.id
    payload = {
        "post_id": post_id,
        "dir": 1
    }

    res = authorized_client.post("/vote", json=payload)
    assert res.status_code == status.HTTP_201_CREATED

    payload = {
        "post_id": post_id,
        "dir": 1
    }

    res = authorized_client.post("/vote", json=payload)
    assert res.status_code == status.HTTP_409_CONFLICT


def test_create_vote_remove_fail(test_post, authorized_client):
    """
    A user cannot unvote a post that user has not voted
    """
    post_test_user = test_post["post1_user1"]

    payload = {
        "post_id": post_test_user.id,
        "dir": 0
    }

    res = authorized_client.post("/vote", json=payload)
    assert res.status_code == status.HTTP_404_NOT_FOUND
