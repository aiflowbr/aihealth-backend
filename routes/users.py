from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from database import crud, schemas
from database.database import get_db
from datetime import datetime, timedelta

# auth
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from config.security import (
    OAUTH2_SCHEME,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    verify_password,
)

router = APIRouter()


# Function to authenticate user
def authenticate_user(db, username: str, password: str):
    user = crud.get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# Function to create access token
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Token route
@router.post("/authenticate", tags=["Users"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Token decode
@router.post("/token_decode", response_model=schemas.TokenDecoded, tags=["Users"])
async def token_decode(
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
):
    return {
        "name": "Admin",
        "username": "admin",
        "mail": "admin@admin.net",
        "photo": "https://cdn3d.iconscout.com/3d/premium/thumb/doctor-avatar-10107433-8179550.png?f=png",
    }


@router.post("", response_model=schemas.User, tags=["Users"])
def create_user(
    user: schemas.UserCreate,
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
    db: Session = Depends(get_db),
):
    print(token)
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@router.put("/{user_id}", response_model=schemas.User, tags=["Users"])
def update_user(
    user_id: int,
    user: schemas.UserUpdate,
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
    db: Session = Depends(get_db),
):
    db_user = crud.get_user(db, user_id=user_id)
    print(token)
    if not db_user:
        raise HTTPException(status_code=400, detail="User ID not found")
    try:
        ret = crud.update_user(db=db, db_user=db_user, userdata=user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ret


@router.get("", response_model=list[schemas.User], tags=["Users"])
def read_users(
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=schemas.User, tags=["Users"])
def read_user(
    user_id: int,
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
    db: Session = Depends(get_db),
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.delete("/{user_id}", response_model=schemas.User, tags=["Users"])
def delete_setting(
    id: int,
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
    db: Session = Depends(get_db),
):
    db_user = crud.get_user(db, user_id=id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.delete_user(db, db_user)
