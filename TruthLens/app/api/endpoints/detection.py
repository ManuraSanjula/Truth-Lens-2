from fastapi import APIRouter, HTTPException, Query
from app.services.new.content_detector import ContentDetector
from app.utils.logger import logger
from typing import Optional
import asyncio

router = APIRouter(prefix="/api/v1/detect", tags=["detection"])
detector = ContentDetector()


@router.get("/")
async def detect_content(
        url: str = Query(..., description="URL of content to analyze"),
        detailed: Optional[bool] = Query(False, description="Return full analysis details")
):
    """
    Analyze content from any URL (images, videos, or webpages)

    Example calls:
    - /api/v1/detect?url=https://example.com/image.jpg
    - /api/v1/detect?url=https://example.com/video.mp4&detailed=true
    """
    try:
        if not url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="Invalid URL format")

        # Perform detection
        result = await detector.detect_fake_content(url)

        if "error" in result.get("result", {}):
            raise HTTPException(status_code=400, detail=result["result"]["error"])

        # Return simplified or detailed response
        if detailed:
            return {
                "status": "success",
                "url": url,
                **result
            }
        else:
            return {
                "status": "success",
                "url": url,
                "type": result["type"],
                "is_fake": result["result"]["is_fake"],
                "confidence": result["result"]["confidence"]
            }

    except Exception as e:
        logger.error(f"Detection failed for {url}: {str(e)}")
        raise HTTPException(status_code=500, detail="Content analysis failed")


@router.get("/types")
async def get_supported_types():
    """List supported content types"""
    return {
        "supported_types": [
            {"type": "image", "extensions": [".jpg", ".jpeg", ".png", ".gif"]},
            {"type": "video", "extensions": [".mp4", ".avi", ".mov"]},
            {"type": "webpage", "description": "Generic web pages"}
        ]
    }