
from .. import models, schemas, oauth2
from .. database import get_db
from fastapi import Response, status, HTTPException, Depends, APIRouter
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

router = APIRouter(
    tags=["Posts"]  # to group it in swagger docs
)


# @router.get("/posts", response_model=List[schemas.Post])

@router.get("/posts", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user), limit: int = None, skip: int = 0, search: Optional[str] = ""):

    # posts = (
    #     db.query(models.Post).
    #     filter(models.Post.owner_id == current_user.id).
    #     filter(models.Post.title.contains(search)).
    #     limit(limit).
    #     offset(skip).
    #     all()
    # )
    posts = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes")).
        join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).
        group_by(models.Post.id).
        filter(models.Post.owner_id == current_user.id).
        filter(models.Post.title.contains(search)).
        limit(limit).
        offset(skip).
        all()
    )

    # The join returns lits of tuple need to convert in list of dict
    posts_new = [{"Post": post, "votes": votes}
                 for post, votes in posts]

    return posts_new


@router.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/post/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    post = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes")).
        join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).
        group_by(models.Post.id).
        filter(models.Post.id == id).first()

    )

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with is {id} not found')
    if post[0].owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Not Authorized to perform Requested Action')
    return post


@router.delete("/post/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with is {id} not found')

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Not Authorized to perform Requested Action')

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/post/{id}", response_model=schemas.Post,)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {id} not found')

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Not Authorized to perform Requested Action')

    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()
