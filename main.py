from fastapi import FastAPI, Depends, HTTPException, status
from fastapi_sqlalchemy import DBSessionMiddleware, db
from fastapi.security import OAuth2PasswordRequestForm
import os
from models import User
from schemas import (
    Token,
    TokenData,
    UserCreate,
    UserInDB
)
from utils import (
    create_access_token,
    get_current_user,
    pwd_context
)

# Initialize FastAPI app
app = FastAPI()

# Add middleware to handle database sessions
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")
app.add_middleware(DBSessionMiddleware, db_url=DATABASE_URL)

# API endpoints


@app.post("/register")
def register(user: UserCreate):
    username = user.username
    password = user.password
    db_user = db.session.query(User).filter(User.username == username).first()
    if db_user:
        raise HTTPException(
            status_code=400, detail="Username already registered")

    hashed_password = pwd_context.hash(password)
    db_user = User(username=username, hashed_password=hashed_password)
    db.session.add(db_user)
    db.session.commit()
    db.session.refresh(db_user)

    return db_user


@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.session.query(User).filter(
        User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserInDB)
def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    return current_user
