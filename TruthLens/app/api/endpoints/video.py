from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.models import Result
from app.services.video_processor import video_processor
from app.models.content import Content, ContentCreate
from app.utils.storage import save_uploaded_file
import logging
from typing import Optional

router = APIRouter(prefix="/api/v1/video", tags=["video"])
logger = logging.getLogger(__name__)


@router.post("/analyze")
async def analyze_video(
        file: UploadFile = File(...),
        user_id: str = Form(...),
        frame_sample_size: Optional[int] = Form(10)
):
    """Dedicated video analysis endpoint"""
    try:
        # Save uploaded file
        file_path = await save_uploaded_file(file)

        # Create content record
        content = await Content.create(ContentCreate(
            user_id=user_id,
            content_type="video",
            file_path=file_path
        ))

        # Process video
        results = await video_processor.process_video(file_path, str(content.id))

        return {
            "content_id": str(content.id),
            "results": [r.dict() for r in results]
        }
    except Exception as e:
        logger.error(f"Video analysis failed: {e}")
        raise HTTPException(500, "Video processing failed")


@router.get("/results/{content_id}")
async def get_video_results(content_id: str):
    """Get video analysis results"""
    try:
        content = await Content.get(content_id)
        if not content or content.content_type != "video":
            raise HTTPException(404, "Video content not found")

        results = await Result.get_by_content(content_id)
        return {"results": [r.dict() for r in results]}
    except Exception as e:
        logger.error(f"Failed to fetch video results: {e}")
        raise HTTPException(500, "Failed to retrieve results")