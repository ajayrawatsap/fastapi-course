
from . import models
from . database import engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import post, user, auth, vote
from .config import settings


# Creates all tables if they do not exists. Can be commented if
# you want to use alembic and not generate it automtically
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    # "http://localhost:8080",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
def root():
    return {"message": "Hello World Again"}
