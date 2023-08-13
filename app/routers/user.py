from .. import models, schemas, utils, oauth2
from .. database import get_db
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

router = APIRouter(
    tags=["Users"]  # to group it in swagger docs
)


@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    user.password = utils.hash(user.password)
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get('/users/me', response_model=schemas.UserOut)
def get_user(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(
        models.User.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No User Found')
    return user
