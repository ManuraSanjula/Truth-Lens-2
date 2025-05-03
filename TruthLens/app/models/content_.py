from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl
from bson import ObjectId

from app.utils.config import settings
from app.utils.database import db

class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    URL = "url"


class ContentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ContentBase(BaseModel):
    user_id: str
    content_type: ContentType
    source_url: Optional[HttpUrl] = None
    raw_text: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Optional[Dict] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: ContentStatus = ContentStatus.PENDING


class ContentCreate(ContentBase):
    pass


class Content(ContentBase):
    id: str = Field(..., alias="_id")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


async def create_content(content: ContentCreate) -> Content:
    content_dict = content.dict()
    result = await db.client[settings.MONGODB_NAME].contents.insert_one(content_dict)
    created_content = await db.client[settings.MONGODB_NAME].contents.find_one({"_id": result.inserted_id})
    return Content(**created_content)


async def get_content(content_id: str) -> Optional[Content]:
    content = await db.client[settings.MONGODB_NAME].contents.find_one({"_id": ObjectId(content_id)})
    if content:
        return Content(**content)
    return None


async def update_content_status(content_id: str, status: ContentStatus) -> bool:
    result = await db.client[settings.MONGODB_NAME].contents.update_one(
        {"_id": ObjectId(content_id)},
        {"$set": {"status": status}}
    )
    return result.modified_count > 0