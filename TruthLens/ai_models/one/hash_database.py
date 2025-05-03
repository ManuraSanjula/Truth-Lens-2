# app/core/hash_database.py
import os
import sqlite3
import imagehash
from PIL import Image
import numpy as np
import cv2
from app.utils.config import settings
import logging

logger = logging.getLogger(__name__)


class HashDatabase:
    """Database for querying perceptual hashes of known fake images"""

    def __init__(self):
        self.db_path = os.path.join(settings.MODEL_CACHE_PATH, "fake_image_hashes.db")
        self.conn = None
        self.cursor = None
        self._connect()

    def _connect(self):
        """Connect to the hash database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            return False

    def query_hash(self, img_hash, threshold=0):
        """Check if an image hash matches any known fake hashes"""
        if not self.conn:
            if not self._connect():
                return {"match": False, "confidence": 0}

        try:
            # For exact match
            hash_str = str(img_hash)
            self.cursor.execute("SELECT classification, confidence FROM fake_image_hashes WHERE hash = ?", (hash_str,))
            result = self.cursor.fetchone()

            if result:
                return {
                    "match": True,
                    "classification": result[0],
                    "confidence": result[1]
                }

            return {"match": False, "confidence": 0}
        except sqlite3.Error as e:
            logger.error(f"Hash query error: {e}")
            return {"match": False, "confidence": 0}

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None


# This would be used in your DeepfakeDetector class - modified _hash_analysis method
def improved_hash_analysis(self, image_path: str) -> dict:
    """Enhanced perceptual hash analysis using database lookup"""
    try:
        img = Image.open(image_path)
        img_hash = imagehash.phash(img)

        # Initialize hash database
        hash_db = HashDatabase()
        try:
            # Query the hash against known fakes
            result = hash_db.query_hash(img_hash)

            return {
                "hash": str(img_hash),
                "match_known_fake": result["match"],
                "confidence": result["confidence"] if result["match"] else 0.0,
                "classification": result.get("classification", None)
            }
        finally:
            hash_db.close()
    except Exception as e:
        logger.warning(f"Hash analysis failed: {e}")
        return {
            "hash": None,
            "match_known_fake": False,
            "confidence": 0.0
        }