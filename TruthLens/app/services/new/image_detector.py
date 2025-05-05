import cv2
import numpy as np
from PIL import Image, ExifTags
import requests
from io import BytesIO
from typing import Dict


class ImageDetector:
    async def detect_fake_image(self, image_url: str) -> Dict:
        try:
            # Download image
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))

            return await self.detect_fake_image_from_memory(img)
        except Exception as e:
            return {"error": str(e)}

    async def detect_fake_image_from_memory(self, img: Image) -> Dict:
        """Analyze image already loaded in memory"""
        # 1. Metadata analysis
        metadata = self._analyze_metadata(img)

        # 2. Error Level Analysis
        ela_score = self._perform_ela(img)

        # 3. Deepfake detection
        fake_score = await self._detect_deepfake(img)

        return {
            "is_fake": ela_score > 0.7 or fake_score > 0.8,
            "confidence": max(ela_score, fake_score),
            "details": {
                "metadata": metadata,
                "ela_score": ela_score,
                "deepfake_score": fake_score
            }
        }

    def _analyze_metadata(self, img: Image) -> Dict:
        try:
            exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items()
                    if k in ExifTags.TAGS}
            return {
                "software": exif.get('Software', ''),
                "created": exif.get('DateTimeOriginal', ''),
                "modified": exif.get('DateTimeDigitized', '')
            }
        except:
            return {}

    def _perform_ela(self, img: Image) -> float:
        buffer = BytesIO()
        img.save(buffer, 'JPEG', quality=90)
        compressed = Image.open(buffer)
        diff = np.abs(np.array(img) - np.array(compressed))
        return np.mean(diff) / 255.0

    async def _detect_deepfake(self, img: Image) -> float:
        cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(cv_img, 1.1, 4)
        return 0.8 if len(faces) > 1 else 0.1  # Simplified example