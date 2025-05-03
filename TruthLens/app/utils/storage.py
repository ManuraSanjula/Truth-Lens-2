import os
import uuid
from fastapi import UploadFile
from app.utils.config import settings
import logging

logger = logging.getLogger(__name__)


async def save_uploaded_file(file: UploadFile) -> str:
    try:
        # Create media storage directory if not exists
        os.makedirs(settings.MEDIA_STORAGE_PATH, exist_ok=True)

        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(settings.MEDIA_STORAGE_PATH, filename)

        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        logger.info(f"File saved to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise