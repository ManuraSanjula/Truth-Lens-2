import os
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)
import torch
import joblib
import logging
import re
from typing import Dict, Optional, List, Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class FakeNewsDetector:
    def __init__(self):
        self.bert_model = None
        self.bert_tokenizer = None
        self.tfidf_vectorizer = None
        self.svm_model = None

        # More comprehensive list of reliable sources with proper domain names
        self.reliable_sources = {
            # Tier 1: Major international news agencies (highest trust)
            'reuters.com': 0.95,
            'apnews.com': 0.95,
            'afp.com': 0.95,

            # Tier 2: Well-established news organizations (high trust)
            'bbc.com': 0.9,
            'bbc.co.uk': 0.9,
            'nytimes.com': 0.9,
            'washingtonpost.com': 0.9,
            'theguardian.com': 0.9,
            'dw.com': 0.9,
            'aljazeera.com': 0.85,
            'bloomberg.com': 0.85,
            'ft.com': 0.85,  # Financial Times
            'wsj.com': 0.85,
            'economist.com': 0.85,
            'cnn.com': 0.8,
            'nbcnews.com': 0.8,
            'abcnews.go.com': 0.8,
            'cbsnews.com': 0.8,

            # Tier 3: Other reputable news organizations (good trust)
            'npr.org': 0.8,
            'pbs.org': 0.8,
            'politico.com': 0.75,
            'thehill.com': 0.75,
            'time.com': 0.75,
            'forbes.com': 0.75,
            'latimes.com': 0.75,
            'usatoday.com': 0.75,
            'theatlantic.com': 0.75,
            'newyorker.com': 0.75,
            'vox.com': 0.7
        }

        # Load all models
        self.load_models()

    def load_models(self):
        """Load all required NLP models"""
        try:
            # Load BERT model for fake news detection
            bert_path = os.path.join("models", "bert-fakenews")
            os.makedirs(bert_path, exist_ok=True)

            model_name = "jy46604790/Fake-News-Bert-Detect"  # Proper fake news model

            self.bert_tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=bert_path
            )

            self.bert_model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                cache_dir=bert_path
            )

            logger.info("BERT model for fake news loaded successfully")

            # Load secondary models if available
            self._load_secondary_models()

        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise

    def _load_secondary_models(self):
        """Load TF-IDF and SVM models if available"""
        try:
            tfidf_path = os.path.join("models", "tfidf.pkl")
            svm_path = os.path.join("models", "svm_model.pkl")

            if os.path.exists(tfidf_path) and os.path.exists(svm_path):
                self.tfidf_vectorizer = joblib.load(tfidf_path)
                self.svm_model = joblib.load(svm_path)
                logger.info("Secondary models (TF-IDF+SVM) loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load secondary models: {e}")

    def extract_domain(self, url: str) -> str:
        """Extract and validate domain from URL"""
        if not url:
            return ""

        # Add http prefix if not present for proper parsing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc

            # Handle common issues
            domain = domain.lower()
            if domain.startswith('www.'):
                domain = domain[4:]  # Remove www. prefix

            return domain
        except Exception as e:
            logger.warning(f"Error parsing URL {url}: {e}")
            return ""

    async def analyze_text(self, text: str, source: Optional[str] = None) -> Dict:
        """Main analysis function that evaluates news content"""
        if not text.strip():
            return {"error": "Empty text provided"}

        try:
            # 1. Primary BERT Analysis
            bert_result = self._bert_analysis(text)

            # 2. Secondary Analysis (if models available)
            svm_result = self._svm_analysis(text) if self.svm_model else None

            # 3. Linguistic Analysis
            linguistic_flags = self._linguistic_analysis(text)

            # 4. Source Reliability Check - improved with proper domain extraction
            source_reliability = self._check_source_reliability(source) if source else {
                "score": 0.5,
                "domain": None,
                "tier": "unknown"
            }

            # 5. Content Analysis - new feature
            content_flags = self._analyze_content(text)

            # Combine results with improved weighting system
            final_result = self._combine_results(
                bert_result,
                svm_result,
                linguistic_flags,
                source_reliability,
                content_flags
            )

            return final_result

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                "error": str(e),
                "classification": "error",
                "confidence": 0.0,
                "status": "analysis_failed"
            }

    def _bert_analysis(self, text: str) -> Dict:
        """Analyze text using BERT model for fake news detection"""
        inputs = self.bert_tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )

        with torch.no_grad():
            outputs = self.bert_model(**inputs)

        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        predicted_class = torch.argmax(probs).item()
        confidence = float(probs[0][predicted_class])

        # Most fake news models use 0=real, 1=fake
        return {
            "is_fake": bool(predicted_class),
            "confidence": confidence,
            "model": "FakeNews-BERT",
            "raw_output": {
                "class": predicted_class,
                "probabilities": probs.tolist()[0]
            }
        }

    def _svm_analysis(self, text: str) -> Optional[Dict]:
        """Analyze text using traditional ML approach"""
        try:
            features = self.tfidf_vectorizer.transform([text])
            prediction = self.svm_model.predict(features)[0]
            proba = self.svm_model.predict_proba(features)[0]

            return {
                "is_fake": bool(prediction),
                "confidence": float(max(proba)),
                "model": "SVM"
            }
        except Exception as e:
            logger.warning(f"SVM analysis failed: {e}")
            return None

    def _linguistic_analysis(self, text: str) -> Dict:
        """Enhanced check for linguistic patterns of news credibility"""
        text_lower = text.lower()

        # Trust indicators - expanded list
        trusted_phrases = [
            "according to official sources",
            "as reported by",
            "official statement",
            "press release",
            "confirmed by",
            "according to research",
            "studies show",
            "data indicates",
            "experts confirm",
            "according to documents",
            "verified by",
            "investigation found"
        ]

        # Warning indicators - expanded list
        warning_phrases = [
            "unverified reports",
            "sources say",
            "anonymous tip",
            "insider claims",
            "rumors suggest",
            "allegedly",
            "supposedly",
            "some people believe",
            "could potentially",
            "may have",
            "they don't want you to know",
            "what they aren't telling you",
            "the truth about",
            "they're hiding"
        ]

        # Exaggeration phrases
        exaggeration_phrases = [
            "historic",
            "unprecedented",
            "massive",
            "blockbuster",
            "game-changing",
            "explosive",
            "bombshell",
            "devastating",
            "earth-shattering",
            "groundbreaking"
        ]

        # Count attribution phrases
        attribution_count = sum(text_lower.count(phrase) for phrase in trusted_phrases)

        # Count warning indicators
        warning_count = sum(text_lower.count(phrase) for phrase in warning_phrases)

        # Count exaggeration phrases
        exaggeration_count = sum(text_lower.count(phrase) for phrase in exaggeration_phrases)

        # Count sensationalism markers
        exclamation_count = text.count('!')

        # Calculate all-caps words ratio
        words = text.split()
        all_caps_words = sum(1 for word in words if word.isupper() and len(word) > 3)
        all_caps_ratio = all_caps_words / len(words) if words else 0

        # Check for balanced presentation
        has_opposing_views = any(phrase in text_lower for phrase in [
            "on the other hand",
            "however",
            "critics argue",
            "opponents say",
            "alternatively",
            "others disagree",
            "some argue",
            "in contrast"
        ])

        return {
            "attribution_count": attribution_count,
            "warning_count": warning_count,
            "exaggeration_count": exaggeration_count,
            "exclamation_count": exclamation_count,
            "all_caps_ratio": all_caps_ratio,
            "all_caps_words": all_caps_words,
            "has_attribution": attribution_count > 0,
            "has_opposing_views": has_opposing_views,
            "sensationalism_score": (
                    exclamation_count * 0.5 +
                    exaggeration_count * 1.0 +
                    all_caps_ratio * 10.0
            )
        }


    def _analyze_content(self, text: str) -> Dict:
        """Analyze the actual content for signs of credibility/non-credibility"""
        text_lower = text.lower()

        # Check for statistical claims
        has_statistics = bool(re.search(r'\d+%|\d+ percent', text_lower))

        # Check for date references
        has_dates = bool(re.search(
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b',
            text_lower))

        # Check for quotes
        quote_count = len(re.findall(r'"[^"]*"|\'[^\']*\'', text))

        # Check for hedging language
        hedging_words = [
            "possibly", "perhaps", "maybe", "appears to", "seems to",
            "could be", "potentially", "reportedly", "allegedly"
        ]

        hedging_count = sum(text_lower.count(word) for word in hedging_words)

        # Check for conspiracy theory language
        conspiracy_phrases = [
            "they don't want you to know",
            "the truth about",
            "what they aren't telling you",
            "government cover up",
            "conspiracy",
            "new world order",
            "deep state",
            "illuminati",
            "mainstream media won't report"
        ]
        conspiracy_count = sum(text_lower.count(phrase) for phrase in conspiracy_phrases)

        # Calculate credibility score based on these factors
        credibility_score = 0.5  # Neutral starting point

        if has_statistics:
            credibility_score += 0.1  # Statistical claims can increase credibility

        if has_dates:
            credibility_score += 0.1  # Specific dates increase credibility

        if quote_count > 0:
            credibility_score += min(0.1, quote_count * 0.02)  # Quotes increase credibility

        if hedging_count > 5:
            credibility_score -= 0.1  # Too much hedging reduces credibility

        if conspiracy_count > 0:
            credibility_score -= min(0.3,
                                     conspiracy_count * 0.1)  # Conspiracy language significantly reduces credibility

        return {
            "has_statistics": has_statistics,
            "has_dates": has_dates,
            "quote_count": quote_count,
            "hedging_count": hedging_count,
            "conspiracy_count": conspiracy_count,
            "content_credibility_score": max(0, min(1, credibility_score))
        }

    def _check_source_reliability(self, source: str) -> Dict:
        """Enhanced reliability scoring based on proper domain verification"""
        if not source:
            return {"score": 0.5, "domain": None, "tier": "unknown"}

        # Extract domain
        domain = self.extract_domain(source)
        if not domain:
            return {"score": 0.5, "domain": None, "tier": "unknown"}

        # Direct match with reliable sources
        if domain in self.reliable_sources:
            score = self.reliable_sources[domain]
            tier = self._get_tier_from_score(score)
            return {"score": score, "domain": domain, "tier": tier}

        # Check for subdomain of reliable source
        for reliable_domain, reliable_score in self.reliable_sources.items():
            if domain.endswith('.' + reliable_domain):
                # Subdomains are slightly less trusted
                score = reliable_score * 0.9
                tier = self._get_tier_from_score(score)
                return {"score": score, "domain": domain, "tier": tier}

        # Government/educational sources
        if domain.endswith('.gov') or domain.endswith('.edu') or '.ac.' in domain:
            return {"score": 0.8, "domain": domain, "tier": "institutional"}

        # News aggregators
        if any(agg in domain for agg in ['news.google.com', 'news.yahoo.com']):
            return {"score": 0.6, "domain": domain, "tier": "aggregator"}

        # Blog/opinion platforms
        if any(platform in domain for platform in ['medium.com', 'substack.com', 'blogspot.com', 'wordpress.com']):
            return {"score": 0.4, "domain": domain, "tier": "blog platform"}

        # Social media
        if any(social in domain for social in
               ['twitter.com', 'facebook.com', 'instagram.com', 'tiktok.com', 'reddit.com']):
            return {"score": 0.3, "domain": domain, "tier": "social media"}

        # Unknown source
        return {"score": 0.5, "domain": domain, "tier": "unknown"}

    def _get_tier_from_score(self, score: float) -> str:
        """Convert reliability score to meaningful tier label"""
        if score >= 0.9:
            return "highly trusted"
        elif score >= 0.8:
            return "trusted"
        elif score >= 0.7:
            return "generally reliable"
        elif score >= 0.5:
            return "medium reliability"
        elif score >= 0.3:
            return "low reliability"
        else:
            return "unreliable"

    def _combine_results(self, bert_result: Dict, svm_result: Optional[Dict],
                         linguistic_flags: Dict, source_reliability: Dict,
                         content_flags: Dict) -> Dict:
        """
        Intelligently combine all analysis results with improved weighting

        Returns nuanced classification instead of binary fake/not fake
        """
        # Extract initial model predictions
        bert_fake_prob = bert_result["confidence"] if bert_result["is_fake"] else 1.0 - bert_result["confidence"]

        # Start with BERT as base
        fake_probability = bert_fake_prob

        # Integrate SVM if available (less weight than BERT)
        if svm_result:
            svm_fake_prob = svm_result["confidence"] if svm_result["is_fake"] else 1.0 - svm_result["confidence"]
            # Blend with 70% BERT, 30% SVM
            fake_probability = (fake_probability * 0.7) + (svm_fake_prob * 0.3)

        # Apply source reliability - stronger influence
        # Higher reliability = lower fake probability
        source_score = source_reliability["score"]
        fake_probability *= (1.0 - (source_score * 0.5))

        # Apply linguistic analysis with more moderate adjustments
        # Attribution reduces fake probability
        if linguistic_flags["has_attribution"]:
            fake_probability *= max(0.7, 1.0 - (linguistic_flags["attribution_count"] * 0.05))

        # Warning phrases increase fake probability moderately
        fake_probability *= min(1.5, 1.0 + (linguistic_flags["warning_count"] * 0.1))

        # Sensationalism increases fake probability
        fake_probability *= min(1.3, 1.0 + (linguistic_flags["sensationalism_score"] * 0.05))

        # Balanced presentation decreases fake probability
        if linguistic_flags["has_opposing_views"]:
            fake_probability *= 0.8

        # Apply content analysis
        # Statistical claims and dates reduce fake probability
        if content_flags["has_statistics"] or content_flags["has_dates"]:
            fake_probability *= 0.9

        # Quotes reduce fake probability
        if content_flags["quote_count"] > 0:
            fake_probability *= max(0.7, 1.0 - (content_flags["quote_count"] * 0.03))

        # Conspiracy language increases fake probability
        if content_flags["conspiracy_count"] > 0:
            fake_probability *= min(2.0, 1.0 + (content_flags["conspiracy_count"] * 0.2))

        # Integrate content credibility score
        content_credibility = content_flags["content_credibility_score"]
        fake_probability *= (1.5 - content_credibility)

        # Cap probability between 0 and 1
        fake_probability = max(0.0, min(1.0, fake_probability))

        # Determine classification based on nuanced thresholds
        classification = self._get_classification_from_probability(fake_probability)

        # Special case: Override for highly trusted sources with good content
        if (source_reliability["score"] >= 0.85 and
                linguistic_flags["has_attribution"] and
                content_flags["content_credibility_score"] >= 0.7 and
                fake_probability < 0.7):
            classification = "likely true"
            fake_probability = min(fake_probability, 0.3)

        return {
            "classification": classification,
            "is_fake": fake_probability,
            "credibility_score": 1.0 - fake_probability,
            "source_info": source_reliability,
            "model_information": {
                "models_used": "BERT+SVM+Linguistic+Source+Content" if svm_result else "BERT+Linguistic+Source+Content",
                "bert_result": bert_result,
                "svm_result": svm_result
            },
            "analysis_details": {
                "linguistic_analysis": linguistic_flags,
                "content_analysis": content_flags,
                "source_reliability": source_reliability
            }
        }

    def _get_classification_from_probability(self, fake_probability: float) -> str:
        """Convert fake probability to nuanced classification"""
        if fake_probability < 0.2:
            return "verified"
        elif fake_probability < 0.4:
            return "likely true"
        elif fake_probability < 0.6:
            return "unclear"
        elif fake_probability < 0.8:
            return "misleading"
        else:
            return "false"


# Factory function to get detector instance
def get_fake_news_detector():
    return FakeNewsDetector()

fake_news_detector = FakeNewsDetector()