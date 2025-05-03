from datetime import datetime
from enum import Enum
from typing import Optional, Dict
from pydantic import BaseModel, Field, HttpUrl, validator
from bson import ObjectId
from app.utils.database import db
from app.utils.config import settings


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
    metadata: Dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: ContentStatus = ContentStatus.PENDING


class ContentCreate(ContentBase):

    @classmethod
    def prepare_for_db(cls, data: dict) -> dict:
        """Convert HttpUrl to string for MongoDB"""
        if 'source_url' in data and data['source_url']:
            data['source_url'] = str(data['source_url'])
        return data

    # def dict(self, **kwargs):
    #     data = super().dict(**kwargs)
    #     return self.prepare_for_db(data)

    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("user_id must be a non-empty string")
        return v

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        # Convert HttpUrl to string for MongoDB
        if data.get('source_url'):
            data['source_url'] = str(data['source_url'])
        return data


class Content(ContentBase):
    id: str = Field(..., alias="_id")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

    @classmethod
    async def create(cls, content_data: ContentCreate) -> 'Content':
        """Create new content in database"""
        content_dict = content_data.dict()
        result = await db.client[settings.MONGODB_NAME].contents.insert_one(content_dict)
        created_content = await db.client[settings.MONGODB_NAME].contents.find_one({"_id": result.inserted_id})
        # Convert ObjectId to string before passing to Pydantic model
        if created_content and "_id" in created_content:
            created_content["_id"] = str(created_content["_id"])
        return cls(**created_content)

    @classmethod
    async def get(cls, content_id: str) -> Optional['Content']:
        """Get content by ID"""
        content = await db.client[settings.MONGODB_NAME].contents.find_one({"_id": ObjectId(content_id)})
        # Convert ObjectId to string before passing to Pydantic model
        if content and "_id" in content:
            content["_id"] = str(content["_id"])
        return cls(**content) if content else None

    @classmethod
    async def update_status(cls, content_id: str, status: ContentStatus) -> bool:
        """Update content status"""
        result = await db.client[settings.MONGODB_NAME].contents.update_one(
            {"_id": ObjectId(content_id)},
            {"$set": {"status": status}}
        )
        return result.modified_count > 0

# class Content(ContentBase):
#     id: str = Field(..., alias="_id")
#
#     class Config:
#         allow_population_by_field_name = True
#         json_encoders = {ObjectId: str}
#
#     @classmethod
#     async def create(cls, content_data: ContentCreate) -> 'Content':
#         """Create new content in database"""
#         content_dict = content_data.dict()
#         result = await db.client[settings.MONGODB_NAME].contents.insert_one(content_dict)
#         created_content = await db.client[settings.MONGODB_NAME].contents.find_one({"_id": result.inserted_id})
#         return cls(**created_content)
#
#     @classmethod
#     async def get(cls, content_id: str) -> Optional['Content']:
#         """Get content by ID"""
#         content = await db.client[settings.MONGODB_NAME].contents.find_one({"_id": ObjectId(content_id)})
#         return cls(**content) if content else None
#
#     @classmethod
#     async def update_status(cls, content_id: str, status: ContentStatus) -> bool:
#         """Update content status"""
#         result = await db.client[settings.MONGODB_NAME].contents.update_one(
#             {"_id": ObjectId(content_id)},
#             {"$set": {"status": status}}
#         )
#         return result.modified_count > 0