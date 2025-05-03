from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.models.users import create_user
from app.utils.config import settings
from app.utils.database import db
from app.models.users import User, UserInDB, UserCreate
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


async def get_user(username: str) -> Optional[UserInDB]:
    user = await db.client[settings.MONGODB_NAME].users.find_one({"username": username})
    if user:
        return UserInDB(**user)
    return None


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/register", response_model=User)
async def register_user(user_data: UserCreate):
    """
    Register a new user.
    """
    try:
        # Check if user already exists
        existing_user = await db.client[settings.MONGODB_NAME].users.find_one({"username": user_data.username})
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already registered"
            )

        # Create user in database
        user = await create_user(user_data)
        return user
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to register user"
        )


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
async def read_users_me(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user