import cv2
import numpy as np
from PIL import Image
import imagehash
from TruthLens.app.utils.config import settings
import os
import logging
import tensorflow as tf

# Try multiple import paths for compatibility
try:
    # Try the current import path first
    from tf_keras.models import load_model
except ImportError:
    try:
        # Try standard tensorflow import
        from tensorflow.keras.models import load_model
    except ImportError:
        print("==================================")
        # Fallback to direct keras import
        #from keras.models import load_model

logger = logging.getLogger(__name__)


class DeepfakeDetector:
    def __init__(self):
        self.model = self._load_model()
        self.ela_threshold = 10
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

    def _load_model(self):
        """Load pre-trained deepfake detection model with robust error handling"""
        try:
            # First, check if the file exists
            model_path = os.path.join(settings.MODEL_CACHE_PATH, "deepfake_model.h5")
            if not os.path.exists(model_path):
                # Check for alternative model files
                alternatives = [
                    "deepfake.weights.h5",
                    "deepfake_model.keras",
                    "model.h5"
                ]

                for alt_name in alternatives:
                    alt_path = os.path.join(settings.MODEL_CACHE_PATH, alt_name)
                    if os.path.exists(alt_path):
                        logger.info(f"Using alternative model: {alt_path}")
                        model_path = alt_path
                        break
                else:
                    raise FileNotFoundError("Deepfake model not found")

            # Try to load the model with custom_objects for compatibility
            try:
                return load_model(model_path)
            except (TypeError, ValueError) as e:
                logger.warning(f"Standard loading failed: {e}. Trying alternative loading method...")

                # If normal loading fails due to version issues, try loading with custom_objects
                return load_model(model_path, compile=False)

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            # Create a simple emergency model if everything fails
            logger.warning("Creating a basic fallback model")
            return self._create_emergency_model()

    def _create_emergency_model(self):
        """Create a basic model for emergency fallback"""
        inputs = tf.keras.layers.Input(shape=(256, 256, 3))
        x = tf.keras.layers.Conv2D(32, (3, 3), activation='relu')(inputs)
        x = tf.keras.layers.MaxPooling2D(2, 2)(x)
        x = tf.keras.layers.Conv2D(64, (3, 3), activation='relu')(x)
        x = tf.keras.layers.MaxPooling2D(2, 2)(x)
        x = tf.keras.layers.Flatten()(x)
        x = tf.keras.layers.Dense(64, activation='relu')(x)
        outputs = tf.keras.layers.Dense(1, activation='sigmoid')(x)

        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

        logger.warning("Using emergency model - detection may be unreliable!")
        return model

    async def analyze_image(self, image_path: str) -> dict:
        """Full image analysis pipeline"""
        try:
            # 1. Basic image validation
            if not self._validate_image(image_path):
                return {
                    "is_fake": False,
                    "confidence": 0.3,
                    "model_used": "Validation",
                    "details": {"error": "Invalid image file"}
                }

            # 2. Face detection
            faces = self._detect_faces(image_path)
            if not faces:
                return {
                    "is_fake": False,
                    "confidence": 0.3,
                    "model_used": "FaceDetection",
                    "details": {"reason": "No faces detected"}
                }

            # 3. Deepfake prediction
            img = self._preprocess_image(image_path)
            try:
                prediction = float(self.model.predict(np.expand_dims(img, axis=0))[0][0])
            except Exception as e:
                logger.error(f"Prediction failed: {e}")
                prediction = 0.5  # Default to uncertain

            # 4. Error Level Analysis
            ela_result = self._perform_ela(image_path)

            # 5. Hash analysis
            hash_result = self._hash_analysis(image_path)

            # Combine results safely
            is_fake = bool(prediction > 0.7) or bool(ela_result["is_manipulated"])
            confidence = float(max(prediction, ela_result["confidence"]))

            return {
                "is_fake": is_fake,
                "confidence": confidence,
                "model_used": "CNN+ELA",
                "details": {
                    "faces_detected": len(faces),
                    "deepfake_score": prediction,
                    "ela_result": ela_result,
                    "hash_match": hash_result
                }
            }
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {
                "is_fake": False,
                "confidence": 0.3,
                "model_used": "Fallback",
                "details": {
                    "error": str(e)
                }
            }

    def _validate_image(self, image_path: str) -> bool:
        """Verify the image is valid and can be processed"""
        try:
            img = Image.open(image_path)
            img.verify()
            return True
        except:
            return False

    def _detect_faces(self, image_path: str) -> list:
        """Detect faces in image using OpenCV with better error handling"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Could not read image")

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            return [] if faces is None else faces.tolist()  # Ensure we return a list
        except Exception as e:
            logger.warning(f"Face detection failed: {e}")
            return []

    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """Prepare image for model prediction with better type safety"""
        try:
            img = Image.open(image_path).resize((256, 256))
            arr = np.array(img)
            if arr.dtype != np.float32:
                arr = arr.astype(np.float32) / 255.0
            return arr
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return np.zeros((256, 256, 3), dtype=np.float32)  # Return blank image

    def _perform_ela(self, image_path: str, quality: int = 90) -> dict:
        """Error Level Analysis for image forensics"""
        try:
            original = Image.open(image_path)
            temp_path = os.path.join(settings.MEDIA_STORAGE_PATH, "temp.jpg")

            original.save(temp_path, 'JPEG', quality=quality)
            compressed = Image.open(temp_path)

            ela_image = np.abs(np.array(original) - np.array(compressed))
            # Ensure we get a single mean value
            mean_diff = float(np.mean(ela_image))  # Explicitly convert to float

            return {
                "is_manipulated": mean_diff > self.ela_threshold,
                "confidence": min(0.9, mean_diff / 20),
                "mean_difference": mean_diff
            }
        except Exception as e:
            logger.warning(f"ELA analysis failed: {e}")
            return {
                "is_manipulated": False,
                "confidence": 0.3,
                "mean_difference": 0.0
            }
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass

    def _hash_analysis(self, image_path: str) -> dict:
        """Perceptual hash analysis"""
        try:
            img = Image.open(image_path)
            img_hash = imagehash.phash(img)

            # In production, compare against database of known fakes
            return {
                "hash": str(img_hash),
                "match_known_fake": False,
                "confidence": 0.5
            }
        except Exception as e:
            logger.warning(f"Hash analysis failed: {e}")
            return {
                "hash": None,
                "match_known_fake": False,
                "confidence": 0.3
            }

    async def analyze_video(self, video_path: str) -> dict:
        """Analyze video by processing key frames"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {"error": "Could not open video file"}

            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sampled_frames = max(10, frame_count // 10)

            results = []
            for i in range(sampled_frames):
                frame_pos = int(i * (frame_count / sampled_frames))
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = cap.read()

                if ret:
                    frame_path = os.path.join(
                        settings.MEDIA_STORAGE_PATH,
                        f"frame_{i}.jpg"
                    )
                    cv2.imwrite(frame_path, frame)
                    results.append(await self.analyze_image(frame_path))
                    try:
                        os.remove(frame_path)
                    except:
                        pass

            cap.release()

            # Aggregate frame results
            if not results:
                return {"error": "No valid frames processed"}

            avg_confidence = sum(r.get('confidence', 0) for r in results) / len(results)
            is_fake = any(r.get('is_fake', False) for r in results)

            return {
                "is_fake": is_fake,
                "confidence": avg_confidence,
                "model_used": "Video CNN",
                "frames_analyzed": len(results),
                "frame_results": results
            }
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            return {
                "error": str(e),
                "is_fake": False,
                "confidence": 0.3
            }

deepfake_detector = DeepfakeDetector()