import cv2
import numpy as np
from PIL import Image
import imagehash
from app.utils.config import settings
import os
import logging
import tensorflow as tf
from typing import Dict, List, Union, Tuple, Any
import time

# Try multiple import paths for compatibility with different TensorFlow versions
try:
    # Try the current import path first
    from tf_keras.models import load_model
except ImportError:
    try:
        # Try standard tensorflow import
        from tensorflow.keras.models import load_model
    except ImportError:
        print("Failed to import Keras model loader")
        # Fallback import handled in _load_model method

logger = logging.getLogger(__name__)


class DeepfakeDetector:
    def __init__(self):
        self.model = self._load_model()
        self.ela_threshold = 10
        # Load face detection models with priority fallbacks
        self.face_detector = self._initialize_face_detector()
        # Cache for previously analyzed images
        self._result_cache = {}
        self.cache_expiry = 3600  # Results expire after 1 hour

    def _initialize_face_detector(self) -> Any:
        """Initialize face detector with multiple fallback options"""
        # Try to load DNN face detector first (more accurate)
        try:
            face_net = cv2.dnn.readNetFromCaffe(
                os.path.join(settings.MODEL_CACHE_PATH, "deploy.prototxt"),
                os.path.join(settings.MODEL_CACHE_PATH, "res10_300x300_ssd_iter_140000.caffemodel")
            )
            logger.info("Loaded DNN face detector")
            return {"type": "dnn", "model": face_net}
        except Exception as e:
            logger.warning(f"Failed to load DNN face detector: {e}")

        # Fall back to Haar cascade
        try:
            cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            if not cascade.empty():
                logger.info("Loaded Haar cascade face detector")
                return {"type": "haar", "model": cascade}
        except Exception as e:
            logger.warning(f"Failed to load Haar cascade: {e}")

        # Last resort - load alternative Haar cascade
        try:
            alt_path = os.path.join(settings.MODEL_CACHE_PATH, "haarcascade_frontalface_default.xml")
            if os.path.exists(alt_path):
                cascade = cv2.CascadeClassifier(alt_path)
                if not cascade.empty():
                    logger.info("Loaded alternative Haar cascade face detector")
                    return {"type": "haar", "model": cascade}
        except Exception as e:
            logger.error(f"All face detectors failed: {e}")

        # Return a dummy detector as last resort
        logger.error("Using dummy face detector - detection will be limited")
        return {"type": "dummy", "model": None}

    def _load_model(self) -> Any:
        """Load pre-trained deepfake detection model with robust error handling"""
        try:
            # Check various model file paths
            model_paths = [
                os.path.join(settings.MODEL_CACHE_PATH, "deepfake_model.h5"),
                os.path.join(settings.MODEL_CACHE_PATH, "deepfake.weights.h5"),
                os.path.join(settings.MODEL_CACHE_PATH, "deepfake_model.keras"),
                os.path.join(settings.MODEL_CACHE_PATH, "model.h5")
            ]

            for model_path in model_paths:
                if os.path.exists(model_path):
                    logger.info(f"Found model at: {model_path}")

                    # Try different loading methods
                    try:
                        return load_model(model_path)
                    except Exception as e1:
                        logger.warning(f"Standard loading failed: {e1}")
                        try:
                            return load_model(model_path, compile=False)
                        except Exception as e2:
                            logger.warning(f"Uncompiled loading failed: {e2}")
                            continue

            # If we get here, no models worked
            raise FileNotFoundError("No usable deepfake model found")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return self._create_emergency_model()

    def _create_emergency_model(self) -> tf.keras.Model:
        """Create a basic model for emergency fallback"""
        logger.warning("Creating emergency fallback model")
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

    async def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Full image analysis pipeline"""
        # Check cache first
        cache_key = f"{image_path}:{os.path.getmtime(image_path)}"
        if cache_key in self._result_cache:
            cache_entry = self._result_cache[cache_key]
            if time.time() - cache_entry["timestamp"] < self.cache_expiry:
                logger.info(f"Using cached result for {image_path}")
                return cache_entry["result"]

        try:
            start_time = time.time()

            # 1. Basic image validation
            if not self._validate_image(image_path):
                result = {
                    "is_fake": False,
                    "confidence": 0.3,
                    "model_used": "Validation",
                    "details": {"error": "Invalid image file"}
                }
                self._update_cache(cache_key, result)
                return result

            # 2. Face detection
            faces = self._detect_faces(image_path)
            if not faces:
                result = {
                    "is_fake": False,
                    "confidence": 0.3,
                    "model_used": "FaceDetection",
                    "details": {"reason": "No faces detected"}
                }
                self._update_cache(cache_key, result)
                return result

            # 3. Deepfake prediction with better preprocessing
            img = self._preprocess_image(image_path)
            prediction = self._make_prediction(img)

            # 4. Error Level Analysis
            ela_result = self._perform_ela(image_path)

            # 5. Hash analysis
            hash_result = self._hash_analysis(image_path)

            # 6. Noise analysis (new)
            noise_result = self._analyze_noise(image_path)

            # Combine results with weighted confidence
            # CNN has greater weight in the final decision
            cnn_weight = 0.7
            ela_weight = 0.2
            noise_weight = 0.1

            # Determine if fake based on multiple signals
            is_fake = (prediction > 0.65 or
                       (ela_result["is_manipulated"] and prediction > 0.5) or
                       (noise_result["is_suspicious"] and prediction > 0.5))

            # Calculate weighted confidence
            confidence = min(0.99, (
                    prediction * cnn_weight +
                    ela_result["confidence"] * ela_weight +
                    noise_result["confidence"] * noise_weight
            ))

            result = {
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

            logger.info(f"Analysis completed in {time.time() - start_time:.2f}s")
            self._update_cache(cache_key, result)
            return result

        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            result = {
                "is_fake": False,
                "confidence": 0.3,
                "model_used": "Fallback",
                "details": {
                    "error": str(e)
                }
            }
            return result

    def _update_cache(self, key: str, result: Dict[str, Any]) -> None:
        """Update the result cache"""
        self._result_cache[key] = {
            "timestamp": time.time(),
            "result": result
        }

        # Cleanup old cache entries
        current_time = time.time()
        expired_keys = [k for k, v in self._result_cache.items()
                        if current_time - v["timestamp"] > self.cache_expiry]
        for k in expired_keys:
            del self._result_cache[k]

    def _validate_image(self, image_path: str) -> bool:
        """Verify the image is valid and can be processed"""
        try:
            img = Image.open(image_path)
            img.verify()

            # Additional checks for minimum size and valid format
            img = Image.open(image_path)
            if min(img.size) < 64:
                logger.warning("Image too small for reliable analysis")
                return False

            return True
        except Exception as e:
            logger.warning(f"Image validation failed: {e}")
            return False

    def _detect_faces(self, image_path: str) -> List[List[int]]:
        """Detect faces in image using best available detector"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Could not read image")

            # Handle different detector types
            if self.face_detector["type"] == "dnn":
                return self._detect_faces_dnn(img)
            elif self.face_detector["type"] == "haar":
                return self._detect_faces_haar(img)
            else:
                # Dummy detector - guess based on image dimensions
                h, w = img.shape[:2]
                return [[w // 4, h // 4, w // 2, h // 2]]  # Return a guessed face region

        except Exception as e:
            logger.warning(f"Face detection failed: {e}")
            return []

    def _detect_faces_dnn(self, img: np.ndarray) -> List[List[int]]:
        """Detect faces using DNN detector"""
        h, w = img.shape[:2]
        blob = cv2.dnn.blobFromImage(
            cv2.resize(img, (300, 300)),
            1.0, (300, 300),
            (104.0, 177.0, 123.0)
        )

        face_net = self.face_detector["model"]
        face_net.setInput(blob)
        detections = face_net.forward()

        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:  # Filter by confidence
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                x1, y1, x2, y2 = box.astype("int")
                faces.append([x1, y1, x2 - x1, y2 - y1])  # Convert to [x,y,w,h] format

        return faces

    def _detect_faces_haar(self, img: np.ndarray) -> List[List[int]]:
        """Detect faces using Haar cascade"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Improved parameters for better detection
        cascade = self.face_detector["model"]
        faces = cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        return [] if len(faces) == 0 else faces.tolist()

    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """Prepare image for model prediction with advanced preprocessing"""
        try:
            # Open with PIL for better color handling
            img = Image.open(image_path).convert('RGB')
            img = img.resize((256, 256), Image.LANCZOS)  # Use high quality resize

            # Convert to numpy array and normalize properly
            arr = np.array(img, dtype=np.float32) / 255.0

            # Apply light preprocessing for better model performance
            # Center the data around zero with std of 1 (important for neural nets)
            arr = (arr - 0.5) * 2

            return arr

        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return np.zeros((256, 256, 3), dtype=np.float32)  # Return blank image

    def _make_prediction(self, img: np.ndarray) -> float:
        """Make model prediction with error handling and multiple attempts"""
        try:
            # First attempt with standard prediction
            prediction = float(self.model.predict(np.expand_dims(img, axis=0), verbose=0)[0][0])
            return prediction
        except Exception as e:
            logger.warning(f"Standard prediction failed: {e}, trying alternative method")
            try:
                # Try alternative prediction approach
                batch = np.expand_dims(img, axis=0)
                # Run inference manually if the model object allows it
                if hasattr(self.model, 'predict_on_batch'):
                    prediction = float(self.model.predict_on_batch(batch)[0][0])
                    return prediction
            except Exception as e2:
                logger.error(f"Alternative prediction also failed: {e2}")
                return 0.5  # Default to uncertain

    def _perform_ela(self, image_path: str, quality: int = 90) -> Dict[str, Any]:
        """Error Level Analysis for image forensics with improved algorithm"""
        try:
            original = Image.open(image_path).convert('RGB')
            temp_path = os.path.join(settings.MEDIA_STORAGE_PATH, f"temp_{os.path.basename(image_path)}")

            # Save with specified JPEG quality
            original.save(temp_path, 'JPEG', quality=quality)
            compressed = Image.open(temp_path).convert('RGB')

            # Calculate ELA difference
            ela_image = np.abs(np.array(original, dtype=np.float32) - np.array(compressed, dtype=np.float32))

            # Calculate metrics from ELA image
            mean_diff = float(np.mean(ela_image))
            max_diff = float(np.max(ela_image))
            std_diff = float(np.std(ela_image))

            # Look for local inconsistencies (potential manipulation)
            blocks = self._analyze_ela_blocks(ela_image)

            # Determine manipulation likelihood based on ELA metrics
            is_manipulated = (mean_diff > self.ela_threshold or
                              std_diff > self.ela_threshold * 2 or
                              blocks["inconsistent_ratio"] > 0.15)

            confidence = min(0.9, (
                    mean_diff / 20 * 0.4 +
                    std_diff / 30 * 0.3 +
                    blocks["inconsistent_ratio"] * 0.3
            ))

            return {
                "is_manipulated": is_manipulated,
                "confidence": confidence,
                "mean_difference": mean_diff,
                "std_difference": std_diff,
                "block_inconsistency": blocks["inconsistent_ratio"]
            }
        except Exception as e:
            logger.warning(f"ELA analysis failed: {e}")
            return {
                "is_manipulated": False,
                "confidence": 0.3,
                "mean_difference": 0.0,
                "std_difference": 0.0,
                "block_inconsistency": 0.0
            }
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception as e:
                    logger.warning(f"Failed to remove temp file: {e}")

    def _analyze_ela_blocks(self, ela_image: np.ndarray) -> Dict[str, float]:
        """Analyze ELA image in blocks to detect local inconsistencies"""
        h, w = ela_image.shape[:2]
        block_size = 16
        blocks_h, blocks_w = h // block_size, w // block_size

        block_means = []
        for i in range(blocks_h):
            for j in range(blocks_w):
                block = ela_image[i * block_size:(i + 1) * block_size,
                        j * block_size:(j + 1) * block_size]
                block_means.append(np.mean(block))

        # Calculate statistics about block differences
        block_means = np.array(block_means)
        median = np.median(block_means)
        mad = np.median(np.abs(block_means - median))  # Median absolute deviation

        # Count blocks that deviate significantly (potential manipulation)
        if mad > 0:
            z_scores = 0.6745 * (block_means - median) / mad  # Robust Z-score
            inconsistent_blocks = np.sum(np.abs(z_scores) > 3.0)
            inconsistent_ratio = inconsistent_blocks / len(block_means)
        else:
            inconsistent_ratio = 0.0

        return {
            "inconsistent_ratio": float(inconsistent_ratio),
            "block_variance": float(np.var(block_means))
        }

    def _hash_analysis(self, image_path: str) -> Dict[str, Any]:
        """Perceptual hash analysis with multiple hash types"""
        try:
            img = Image.open(image_path).convert('RGB')

            # Generate multiple hash types for more robust matching
            phash = str(imagehash.phash(img))
            dhash = str(imagehash.dhash(img))
            whash = str(imagehash.whash(img))

            # In production, compare against database of known fakes
            # For now, just return the hashes

            return {
                "hash": phash,
                "dhash": dhash,
                "whash": whash,
                "match_known_fake": False,
                "confidence": 0.5
            }
        except Exception as e:
            logger.warning(f"Hash analysis failed: {e}")
            return {
                "hash": None,
                "dhash": None,
                "whash": None,
                "match_known_fake": False,
                "confidence": 0.3
            }

    def _analyze_noise(self, image_path: str) -> Dict[str, Any]:
        """Analyze image noise patterns to detect inconsistencies"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Could not read image")

            # Convert to grayscale for noise analysis
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Extract noise using a high-pass filter
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            noise = cv2.subtract(gray, blur)

            # Calculate noise statistics
            noise_std = float(np.std(noise))
            noise_mean = float(np.mean(noise))
            noise_entropy = float(cv2.calcHist([noise], [0], None, [256], [0, 256]).flatten().std())

            # Check for suspicious noise patterns
            suspicious_noise = noise_std < 5.0 or noise_std > 30.0 or noise_entropy < 2.0
            confidence = min(0.8, max(0.3, abs(noise_std - 15) / 15))

            return {
                "is_suspicious": suspicious_noise,
                "confidence": confidence,
                "noise_std": noise_std,
                "noise_mean": noise_mean,
                "noise_entropy": noise_entropy
            }
        except Exception as e:
            logger.warning(f"Noise analysis failed: {e}")
            return {
                "is_suspicious": False,
                "confidence": 0.3,
                "noise_std": 0.0,
                "noise_mean": 0.0,
                "noise_entropy": 0.0
            }

    async def analyze_video(self, video_path: str) -> Dict[str, Any]:
        """Analyze video by processing key frames"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {"error": "Could not open video file"}

            # Get video properties
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = frame_count / fps if fps > 0 else 0

            # Determine how many frames to sample
            if duration > 60:  # Long video
                sample_interval = int(fps * 5)  # Sample every 5 seconds
            elif duration > 10:  # Medium video
                sample_interval = int(fps * 2)  # Sample every 2 seconds
            else:  # Short video
                sample_interval = max(1, int(fps))  # Sample every second

            # Calculate total frames to sample
            sampled_frames = min(30, max(10, frame_count // sample_interval))

            results = []
            temp_frames = []
            for i in range(sampled_frames):
                # Calculate position for evenly distributed sampling
                frame_pos = int(i * frame_count / sampled_frames)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = cap.read()

                if ret:
                    frame_path = os.path.join(
                        settings.MEDIA_STORAGE_PATH,
                        f"frame_{os.path.basename(video_path)}_{i}.jpg"
                    )
                    cv2.imwrite(frame_path, frame)
                    temp_frames.append(frame_path)
                    results.append(await self.analyze_image(frame_path))

            cap.release()

            # Clean up temporary files
            for frame_path in temp_frames:
                try:
                    os.remove(frame_path)
                except Exception as e:
                    logger.warning(f"Failed to remove temp frame: {e}")

            # Aggregate frame results
            if not results:
                return {"error": "No valid frames processed"}

            # Calculate weighted confidence (later frames have higher weight)
            weights = np.linspace(0.7, 1.0, len(results))
            weighted_sum = sum(r.get('confidence', 0) * w for r, w in zip(results, weights))
            avg_confidence = weighted_sum / sum(weights)

            # Determine if fake based on consensus and consistency
            fake_frames = sum(1 for r in results if r.get('is_fake', False))
            fake_ratio = fake_frames / len(results)
            is_fake = fake_ratio > 0.4  # If 40% or more frames are detected as fake

            # Look for inconsistency between frames (a sign of manipulation)
            face_counts = [r.get('details', {}).get('faces_detected', 0) for r in results]
            face_consistency = np.std(face_counts) if face_counts else 0

            return {
                "is_fake": is_fake,
                "confidence": avg_confidence,
                "model_used": "Video CNN",
                "frames_analyzed": len(results),
                "fake_frame_ratio": fake_ratio,
                "face_consistency": float(face_consistency),
                "frame_results": results[:3]  # Just include first 3 frames for brevity
            }
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            return {
                "error": str(e),
                "is_fake": False,
                "confidence": 0.3
            }


deepfake_detector = DeepfakeDetector()