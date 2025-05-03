import logging
import sys
from logging.handlers import RotatingFileHandler
from app.utils.config import settings


def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = RotatingFileHandler(
        "app.log",
        maxBytes=1024 * 1024 * 10,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()