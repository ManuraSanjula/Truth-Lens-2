from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from app.utils.database import db
from app.utils.config import settings


class DetectionType(str, Enum):
    FAKE_NEWS = "fake_news"
    IMAGE_MANIPULATION = "image_manipulation"
    VIDEO_MANIPULATION = "video_manipulation"
    AUDIO_MANIPULATION = "audio_manipulation"


class ResultBase(BaseModel):
    content_id: str
    detection_type: str
    is_fake: bool
    confidence: float
    explanation: str = ""
    model_used: str
    model_version: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Result(ResultBase):
    id: Optional[str] = Field(alias="_id", default=None)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

    @classmethod
    async def create(cls, result_data: ResultBase) -> 'Result':
        """Create new result in database"""
        # Convert to dict and prepare for MongoDB
        result_dict = result_data.dict()

        # Insert into database
        inserted = await db.client[settings.MONGODB_NAME].results.insert_one(result_dict)

        # Fetch the created document
        created_result = await db.client[settings.MONGODB_NAME].results.find_one(
            {"_id": inserted.inserted_id}
        )

        # Convert ObjectId to string before passing to Pydantic model
        if created_result and "_id" in created_result:
            created_result["_id"] = str(created_result["_id"])

        return cls(**created_result)

    @classmethod
    async def get(cls, result_id: str) -> Optional['Result']:
        """Get result by ID"""
        result = await db.client[settings.MONGODB_NAME].results.find_one(
            {"_id": ObjectId(result_id)}
        )

        # Convert ObjectId to string before passing to Pydantic model
        if result and "_id" in result:
            result["_id"] = str(result["_id"])

        return cls(**result) if result else None

    @classmethod
    async def get_by_content_id(cls, content_id: str) -> list['Result']:
        """Get all results for a given content ID"""
        cursor = db.client[settings.MONGODB_NAME].results.find(
            {"content_id": content_id}
        )

        results = []
        async for doc in cursor:
            # Convert ObjectId to string before passing to Pydantic model
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            results.append(cls(**doc))

        return results