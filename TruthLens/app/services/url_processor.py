import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

import logging
import re
logger = logging.getLogger(__name__)

class URLProcessor:
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    async def process_url(self, url: str, content_id: str) -> dict:
        """Extract and analyze content from URL"""
        try:
            url_str = str(url)

            # 1. Validate URL
            if not self._is_valid_url(url_str):
                return {"error": "Invalid URL"}

            # 2. Fetch URL content
            content = await self._fetch_url_content(url_str)
            if not content:
                return {"error": "Failed to fetch URL content"}

            # 3. Extract main text content
            text_content = self._extract_main_content(content)
            print(text_content)
            # 4. Analyze text
            return {
                "url": url,
                "domain": urlparse(url_str).netloc,
                "content": text_content,
                # "analysis": await fake_news_detector.analyze_text(text_content, url_str)
            }
        except Exception as e:
            logger.error(f"URL processing failed: {e}")
            raise

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    async def _fetch_url_content(self, url: str) -> str:
        """Fetch HTML content from URL"""
        try:
            headers = {"User-Agent": self.user_agent}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.warning(f"URL fetch failed: {e}")
            return None

    def _extract_main_content(self, html: str) -> str:
        """Extract main article text from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer']):
                element.decompose()

            # Get text from common article containers
            article_text = ""
            for tag in ['article', 'main', 'div']:
                elements = soup.find_all(tag)
                for element in elements:
                    if len(element.text) > len(article_text):
                        article_text = element.get_text(separator=" ", strip=True)

            # Fallback to body if no article found
            if not article_text:
                article_text = soup.body.get_text(separator=" ", strip=True)

            # Clean up text
            article_text = re.sub(r'\s+', ' ', article_text).strip()
            return article_text
        except Exception as e:
            logger.warning(f"Content extraction failed: {e}")
            return ""

url_processor = URLProcessor()
