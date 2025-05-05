from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId
from TruthLens.app.utils.database import db
from TruthLens.app.utils.config import settings
from passlib.context import CryptContext
import logging

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str
    disabled: bool = False


class User(UserBase):
    id: str = Field(..., alias="_id")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


async def get_user(username: str) -> Optional[User]:
    user = await db.client[settings.MONGODB_NAME].users.find_one({"username": username})
    if user:
        return User(**user)
    return None


async def create_user(user: UserCreate) -> User:
    """
    Create a new user in database with hashed password
    """
    try:
        hashed_password = pwd_context.hash(user.password)
        user_dict = user.dict(exclude={"password"})
        user_dict.update({
            "hashed_password": hashed_password,
            "disabled": False
        })

        result = await db.client[settings.MONGODB_NAME].users.insert_one(user_dict)
        if result.inserted_id:
            created_user = await db.client[settings.MONGODB_NAME].users.find_one({"_id": result.inserted_id})
            created_user["_id"] = str(created_user["_id"])
            return User(**created_user)
        raise Exception("Failed to create user")
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise