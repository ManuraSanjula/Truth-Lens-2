from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from bson import ObjectId
from TruthLens.app.utils.database import db
from TruthLens.app.utils.config import settings
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class DetectionType(str, Enum):
    FAKE_NEWS = "fake_news"
    DEEPFAKE = "deepfake"
    IMAGE_MANIPULATION = "image_manipulation"


class ResultBase(BaseModel):
    content_id: str
    detection_type: DetectionType
    is_fake: bool
    confidence: float
    explanation: str
    model_used: str
    model_version: str
    metadata: Optional[Dict] = {}
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class ResultCreate(ResultBase):
    pass


class Result(ResultBase):
    id: str = Field(..., alias="_id")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

    @classmethod
    def from_mongo(cls, data: dict) -> "Result":
        """Convert MongoDB document to Pydantic model"""
        if data.get("_id"):
            # Convert ObjectId to string
            data["_id"] = str(data["_id"])
        return cls(**data)


async def create_result(result: ResultCreate) -> Result:
    result_dict = result.dict()
    inserted = await db.client[settings.MONGODB_NAME].results.insert_one(result_dict)
    created = await db.client[settings.MONGODB_NAME].results.find_one({"_id": inserted.inserted_id})
    # Use the from_mongo class method to handle ObjectId conversion
    return Result.from_mongo(created)


async def get_results_by_content(content_id: str) -> List[Result]:
    results = await db.client[settings.MONGODB_NAME].results.find({"content_id": content_id}).to_list(None)
    # Use the from_mongo class method for each result
    return [Result.from_mongo(result) for result in results]