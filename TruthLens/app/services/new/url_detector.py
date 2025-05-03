import tldextract
import requests
import ssl
import socket  # Added missing import
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Dict, Optional
import asyncio


class URLDetector:
    def __init__(self):
        self.known_fake_domains = {"fake-news.com", "deceptive.org"}  # Load from DB in production

    async def detect_fake_url(self, url: str) -> Dict:
        # 1. Domain analysis
        domain_info = tldextract.extract(url)
        domain_rating = self._check_domain_reputation(domain_info.domain)

        # 2. SSL verification
        ssl_valid = await self._verify_ssl(url)

        # 3. Content similarity check
        similarity_score = await self._check_content_similarity(url)

        return {
            "is_fake": domain_rating < 0.5 or not ssl_valid or similarity_score > 0.8,
            "confidence": max(domain_rating, similarity_score),
            "details": {
                "domain_rating": domain_rating,
                "ssl_valid": ssl_valid,
                "similarity_score": similarity_score
            }
        }

    def _check_domain_reputation(self, domain: str) -> float:
        return 0.0 if domain in self.known_fake_domains else 1.0

    async def _verify_ssl(self, url: str) -> bool:
        try:
            hostname = url.split('//')[1].split('/')[0]
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
                s.connect((hostname, 443))
                cert = s.getpeercert()
            return datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z') > datetime.now()
        except:
            return False

    async def _check_content_similarity(self, url: str) -> float:
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            return self._calculate_similarity(text)  # Implement similarity algorithm
        except:
            return 0.0

    def _calculate_similarity(self, text: str) -> float:
        """Placeholder for text similarity calculation"""
        return 0.0