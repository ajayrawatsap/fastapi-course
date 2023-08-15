from pydantic import BaseModel, EmailStr, ConfigDict, conint
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    created_at: datetime


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class Post(PostBase):
    # Response class to send the data as ouput
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    # owner_id: int
    owner: UserOut


class PostOut(BaseModel):
    # model_config = ConfigDict(from_attributes=True)
    Post: Post
    votes: int


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)  # 0 or 1
