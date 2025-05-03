import os
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline
)
import torch
import joblib
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class FakeNewsDetector:
    def __init__(self):
        self.bert_model = None
        self.bert_tokenizer = None
        self.tfidf_vectorizer = None
        self.svm_model = None
        self.reliable_sources = [
            'bbc', 'reuters', 'ap', 'afp', 'dw', 'aljazeera',
            'nytimes', 'washingtonpost', 'theguardian', 'bloomberg',
            'financialtimes', 'wsj', 'economist', 'apnews'
        ]
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

    async def analyze_text(self, text: str, source: Optional[str] = None) -> Dict:

        if not text.strip():
            return {"error": "Empty text provided"}

        try:
            # 1. Primary BERT Analysis
            bert_result = self._bert_analysis(text)

            # 2. Secondary Analysis (if models available)
            svm_result = self._svm_analysis(text) if self.svm_model else None

            # 3. Linguistic Analysis
            linguistic_flags = self._linguistic_analysis(text)

            # 4. Source Reliability Check
            source_score = self._check_source_reliability(source) if source else 0.5

            # Combine results with intelligent weighting
            final_result = self._combine_results(
                bert_result,
                svm_result,
                linguistic_flags,
                source_score
            )

            return final_result

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                "error": str(e),
                "is_fake": False,
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
        """Check for linguistic patterns of fake news"""
        text_lower = text.lower()

        # Trust indicators
        trusted_phrases = [
            "according to official sources",
            "as reported by",
            "official statement",
            "press release",
            "confirmed by"
        ]

        # Warning indicators
        warning_phrases = [
            "unverified reports",
            "sources say",
            "anonymous tip",
            "insider claims",
            "rumors suggest"
        ]

        # Count sensationalism markers
        sensational_markers = sum(
            text_lower.count(marker)
            for marker in ['!', '!!!', 'breaking', 'shocking', 'astonishing']
        )

        return {
            "is_trusted": any(phrase in text_lower for phrase in trusted_phrases),
            "warning_flags": sum(1 for phrase in warning_phrases if phrase in text_lower),
            "sensational_markers": sensational_markers,
            "all_caps_words": sum(1 for word in text.split() if word.isupper() and len(word) > 3)
        }

    def _check_source_reliability(self, source: str) -> float:
        """Return reliability score 0-1 based on source"""
        source = source.lower()

        # Check against known reliable sources
        if any(reliable in source for reliable in self.reliable_sources):
            return 0.9  # Highly reliable

        # Government/educational sources
        if any(domain in source for domain in ['.gov', '.edu', '.ac.']):
            return 0.8

        # Blog/opinion platforms
        if any(platform in source for platform in ['blog', 'medium.com', 'substack.com']):
            return 0.4

        # Social media
        if any(social in source for social in ['twitter.com', 'facebook.com', 'tiktok.com']):
            return 0.3

        return 0.5  # Default unknown reliability

    def _combine_results(self, bert_result: Dict, svm_result: Optional[Dict],
                         linguistic_flags: Dict, source_score: float) -> Dict:
        """
        Intelligently combine all analysis results with weighting

        Returns final classification decision
        """
        MIN_CONFIDENCE = 0.65  # Only classify as fake if confidence > 65%

        # Base confidence from BERT (primary)
        confidence = bert_result["confidence"]

        # Adjust based on SVM if available
        if svm_result:
            confidence = (confidence * 0.6) + (svm_result["confidence"] * 0.4)

        # Adjust based on linguistic analysis
        if linguistic_flags["is_trusted"]:
            confidence *= 0.7  # Reduce fake probability for trusted phrasing

        if linguistic_flags["warning_flags"] > 0:
            confidence *= 1.1  # Slightly increase for warning phrases

        if linguistic_flags["sensational_markers"] > 3:
            confidence *= 1.15  # Increase for sensational language

        # Apply source reliability adjustment
        confidence *= (1.3 - source_score)  # Higher source score reduces fake probability

        # Cap confidence between 0 and 1
        confidence = max(0.0, min(1.0, confidence))

        # Final decision
        is_fake = (
                bert_result["is_fake"] and
                (svm_result["is_fake"] if svm_result else True) and
                confidence >= MIN_CONFIDENCE and
                not linguistic_flags["is_trusted"]
        )

        return {
            "is_fake": is_fake,
            "confidence": confidence,
            "model_used": "BERT+SVM+LINGUISTIC+SOURCE" if svm_result else "BERT+LINGUISTIC+SOURCE",
            "details": {
                "bert_result": bert_result,
                "svm_result": svm_result,
                "linguistic_analysis": linguistic_flags,
                "source_reliability": source_score,
                "final_confidence": confidence,
                "threshold_used": MIN_CONFIDENCE
            }
        }


# Singleton instance
fake_news_detector = FakeNewsDetector()
