import cv2
import numpy as np
import requests
import tempfile
import os
from typing import Dict
from PIL import Image
import asyncio
from app.services.new.image_detector import ImageDetector  # Import ImageDetector


class VideoDetector:
    def __init__(self):
        self.image_detector = ImageDetector()  # Initialize detector

    async def detect_fake_video(self, video_url: str) -> Dict:
        try:
            # Download video
            response = requests.get(video_url, stream=True)
            temp_path = os.path.join(tempfile.gettempdir(), "temp_video.mp4")

            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

            # Analyze video
            result = await self._analyze_video(temp_path)
            os.remove(temp_path)
            return result
        except Exception as e:
            return {"error": str(e)}

    async def _analyze_video(self, video_path: str) -> Dict:
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        sample_rate = max(1, total_frames // 10)

        frame_results = []
        for i in range(0, total_frames, sample_rate):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                result = await self.image_detector.detect_fake_image_from_memory(img)
                frame_results.append(result)

        cap.release()

        if not frame_results:
            return {"error": "No frames analyzed"}

        avg_confidence = sum(r.get('confidence', 0) for r in frame_results) / len(frame_results)
        is_fake = any(r.get('is_fake', False) for r in frame_results)

        return {
            "is_fake": is_fake,
            "confidence": avg_confidence,
            "frames_analyzed": len(frame_results),
            "frame_results": frame_results
        }