from urllib.parse import urlparse
from typing import Dict
from TruthLens.app.services.new.url_detector import URLDetector  # Import URLDetector
from TruthLens.app.services.new.image_detector import ImageDetector  # Import ImageDetector
from TruthLens.app.services.new.video_detector import VideoDetector  # Import VideoDetector


class ContentDetector:
    def __init__(self):
        self.url_detector = URLDetector()
        self.image_detector = ImageDetector()
        self.video_detector = VideoDetector()

    async def detect_fake_content(self, url: str) -> Dict:
        url_result = await self.url_detector.detect_fake_url(url)

        if url_result.get('is_fake', False):
            return {"type": "url", "result": url_result}

        content_type = self._get_content_type(url)

        if content_type == "image":
            result = await self.image_detector.detect_fake_image(url)
            return {"type": "image", "result": result}
        elif content_type == "video":
            result = await self.video_detector.detect_fake_video(url)
            return {"type": "video", "result": result}
        else:
            return {
                "type": "webpage",
                "result": await self._analyze_web_content(url)
            }

    def _get_content_type(self, url: str) -> str:
        parsed = urlparse(url)
        path = parsed.path.lower()

        if any(path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
            return "image"
        elif any(path.endswith(ext) for ext in ['.mp4', '.avi', '.mov']):
            return "video"
        return "webpage"

    async def _analyze_web_content(self, url: str) -> Dict:
        return {
            "is_fake": False,
            "confidence": 0.0,
            "details": "Web content analysis not implemented"
        }