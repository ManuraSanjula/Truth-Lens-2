import asyncio
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.content_processor import process_content
from app.models import Content, ContentCreate, ContentType
from app.utils.storage import save_uploaded_file
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/submit")
async def submit_content(
    content_type: str = Form(...),
    source_url: Optional[str] = Form(None),
    raw_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    user_id: str = Form(...),
):
    try:
        # Validate URL format if provided
        if source_url and not source_url.startswith(('http://', 'https://')):
            raise HTTPException(400, detail="Invalid URL format")

        # Prepare content data
        if content_type == "url" and source_url:
            content_data = ContentCreate(
                user_id=user_id,
                content_type=ContentType.URL,
                source_url=source_url
            )
        elif content_type == "text" and raw_text:
            content_data = ContentCreate(
                user_id=user_id,
                content_type=ContentType.TEXT,
                raw_text=raw_text
            )
        elif content_type in ["image", "video"] and file:
            file_path = await save_uploaded_file(file)
            content_data = ContentCreate(
                user_id=user_id,
                content_type=ContentType(content_type),
                file_path=file_path
            )
        else:
            raise HTTPException(400, detail="Invalid content submission")

        content = await Content.create(content_data)
        asyncio.create_task(process_content(str(content.id)))

        return {
            "message": "Content processing started",
            "content_id": str(content.id),
            "status": content.status.value
        }

    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        logger.error(f"Submission error: {e}", exc_info=True)
        raise HTTPException(500, detail="Content processing failed")


@router.get("/status/{content_id}")
async def get_status(content_id: str):
    """Check processing status"""
    content = await Content.get(content_id)
    if not content:
        raise HTTPException(404, "Content not found")
    return {"status": content.status}