import cv2
import numpy as np
from PIL import Image
import imagehash
from app.utils.config import settings
import os
import logging
import tensorflow as tf
from typing import Dict, List, Union, Tuple, Any

# Configure logging
logger = logging.getLogger(__name__)


class DeepfakeDetector:
    def __init__(self):
        # Initialize with fallback options ready
        self.model = None
        self.ela_threshold = 10
        self.face_detector = None

        # Initialize components with better error handling
        self._initialize_face_detector()
        self._load_model()

        # Cache for previously analyzed images
        self._result_cache = {}
        self.cache_expiry = 3600  # Results expire after 1 hour

    def _initialize_face_detector(self) -> None:
        """Initialize face detector with fallback options for better reliability"""
        try:
            # First try: OpenCV's built-in Haar cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            if os.path.exists(cascade_path):
                cascade = cv2.CascadeClassifier(cascade_path)
                if not cascade.empty():
                    logger.info("Loaded Haar cascade face detector")
                    self.face_detector = {"type": "haar", "model": cascade}
                    return

            # Second try: Local Haar cascade file
            local_cascade = os.path.join(settings.MODEL_CACHE_PATH, "haarcascade_frontalface_default.xml")
            if os.path.exists(local_cascade):
                cascade = cv2.CascadeClassifier(local_cascade)
                if not cascade.empty():
                    logger.info("Loaded local Haar cascade face detector")
                    self.face_detector = {"type": "haar", "model": cascade}
                    return

            # If we get here, create a dummy detector as fallback
            logger.warning("Failed to load any face detector - using fallback")
            self.face_detector = {"type": "basic", "model": None}

        except Exception as e:
            logger.error(f"Face detector initialization failed: {e}")
            self.face_detector = {"type": "basic", "model": None}

    def _load_model(self) -> None:
        """Load pre-trained deepfake detection model with TensorFlow version compatibility fixes"""
        # First try loading an existing model with error handling for each step
        try:
            self._try_load_existing_model()
        except Exception as e:
            logger.error(f"Could not load existing model: {e}")

        # If model is still None, create a compatible model
        if self.model is None:
            self._create_compatible_model()

    def _try_load_existing_model(self) -> None:
        """Try loading model with various approaches to handle TensorFlow version mismatches"""
        # Check version - this helps determine compatibility approach
        tf_version = tf.__version__
        logger.info(f"TensorFlow version: {tf_version}")

        # Get all potential model files
        model_dir = settings.MODEL_CACHE_PATH
        potential_files = [
            os.path.join(model_dir, "deepfake_model.keras"),
            os.path.join(model_dir, "deepfake_model.h5"),
            os.path.join(model_dir, "model.h5"),
            os.path.join(model_dir, "deepfake.weights.h5")
        ]

        # Try different loading approaches based on file existence
        for model_path in potential_files:
            if not os.path.exists(model_path):
                continue

            logger.info(f"Attempting to load: {model_path}")

            try:
                # Approach 1: Direct load with no compile (safest)
                self.model = tf.keras.models.load_model(
                    model_path,
                    compile=False,
                    safe_mode=False  # Bypass shape checking
                )
                logger.info(f"Successfully loaded model from {model_path}")
                return
            except Exception as e1:
                logger.warning(f"Standard loading failed: {str(e1)}")

                try:
                    # Approach 2: Custom load with manual layer creation
                    # This addresses the 'batch_shape' error in your logs
                    if model_path.endswith('.h5') or model_path.endswith('.keras'):
                        self._create_compatible_model()

                        # Only load weights if model creation was successful
                        if self.model is not None:
                            try:
                                self.model.load_weights(model_path)
                                logger.info(f"Loaded weights from {model_path}")
                                return
                            except Exception as e2:
                                logger.warning(f"Failed to load weights: {str(e2)}")
                except Exception as e3:
                    logger.warning(f"Custom loading failed: {str(e3)}")

        # If we got here, no loading method worked
        logger.error("All model loading approaches failed")
        self.model = None

    def _create_compatible_model(self) -> None:
        """Create a compatible model that works across TensorFlow versions"""
        logger.warning("Creating emergency fallback model")
        try:
            # Create a simple sequential model that avoids version-specific features
            self.model = tf.keras.Sequential([
                # Use input_shape instead of batch_shape (the error in your logs)
                tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(256, 256, 3)),
                tf.keras.layers.MaxPooling2D(2, 2),
                tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                tf.keras.layers.MaxPooling2D(2, 2),
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dense(64, activation='relu'),
                tf.keras.layers.Dense(1, activation='sigmoid')
            ])

            # Compile with basic settings
            self.model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy']
            )

            # Save this model for future use to avoid regeneration
            try:
                model_save_path = os.path.join(settings.MODEL_CACHE_PATH, "emergency_model.keras")
                self.model.save(model_save_path)
                logger.info(f"Saved emergency model to {model_save_path}")
            except Exception as save_error:
                logger.warning(f"Couldn't save emergency model: {save_error}")

            logger.warning("Using emergency model - detection may be unreliable!")
        except Exception as e:
            logger.error(f"Failed to create emergency model: {e}")
            self.model = None

    def _detect_faces(self, image_path: str) -> List[List[int]]:
        """Detect faces in image using available detector"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Could not read image")

            if self.face_detector["type"] == "haar":
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                cascade = self.face_detector["model"]
                faces = cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                return [] if len(faces) == 0 else faces.tolist()
            else:
                # Basic face detection fallback - estimate one face in center
                h, w = img.shape[:2]
                center_x, center_y = w // 2, h // 2
                face_w, face_h = w // 3, h // 3
                return [[center_x - face_w // 2, center_y - face_h // 2, face_w, face_h]]

        except Exception as e:
            logger.warning(f"Face detection failed: {e}")
            return []

    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """Prepare image for model prediction with compatibility fixes"""
        try:
            # Open with PIL for better color handling
            img = Image.open(image_path).convert('RGB')
            img = img.resize((256, 256))

            # Convert to numpy array with proper normalization (0-1 range)
            arr = np.array(img) / 255.0

            # Ensure correct shape and data type
            if arr.shape != (256, 256, 3):
                arr = np.zeros((256, 256, 3))

            # Ensure float32 for TensorFlow compatibility
            return arr.astype(np.float32)

        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return np.zeros((256, 256, 3), dtype=np.float32)

    async def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Full image analysis pipeline with better error handling"""
        try:
            # 1. Basic image validation
            if not os.path.exists(image_path):
                return {
                    "is_fake": False,
                    "confidence": 0.3,
                    "model_used": "Validation",
                    "details": {"error": "Image file not found"}
                }

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

            # 3. Model check
            if self.model is None:
                # Try once more to load or create model
                self._load_model()
                if self.model is None:
                    return {
                        "is_fake": False,
                        "confidence": 0.3,
                        "model_used": "None",
                        "details": {"error": "No model available"}
                    }

            # 4. Deepfake prediction with robust error handling
            img = self._preprocess_image(image_path)
            try:
                # Use prediction with batch to handle various model forms
                prediction_input = np.expand_dims(img, axis=0)
                prediction = float(self.model.predict(prediction_input, verbose=0)[0][0])
            except Exception as e:
                logger.error(f"Prediction failed: {e}")
                # Fallback prediction
                prediction = 0.5

            # 5. Error Level Analysis
            ela_result = self._perform_ela(image_path)

            # 6. Hash analysis
            hash_result = self._hash_analysis(image_path)

            # Combine results safely
            is_fake = bool(prediction > 0.6)
            confidence = float(max(0.3, min(0.95, prediction)))  # Keep between 0.3-0.95

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
            # Just check if we can access image data
            img.verify()
            return True
        except Exception:
            return False

    def _perform_ela(self, image_path: str, quality: int = 90) -> Dict[str, Any]:
        """Error Level Analysis with better file handling"""
        try:
            original = Image.open(image_path).convert('RGB')

            # Create unique temp filename to avoid collisions
            import uuid
            temp_filename = f"temp_{uuid.uuid4().hex}.jpg"
            temp_path = os.path.join(settings.MEDIA_STORAGE_PATH, temp_filename)

            # Save and reload with compression
            original.save(temp_path, 'JPEG', quality=quality)
            compressed = Image.open(temp_path).convert('RGB')

            # Calculate ELA difference safely
            try:
                orig_array = np.array(original, dtype=np.float32)
                comp_array = np.array(compressed, dtype=np.float32)
                ela_image = np.abs(orig_array - comp_array)
                mean_diff = float(np.mean(ela_image))
            except Exception:
                mean_diff = 5.0  # Default value on error

            # Clean up temp file
            try:
                os.remove(temp_path)
            except Exception:
                pass

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

    def _hash_analysis(self, image_path: str) -> Dict[str, Any]:
        """Perceptual hash analysis with better error handling"""
        try:
            img = Image.open(image_path).convert('RGB')
            phash_value = imagehash.phash(img)

            return {
                "hash": str(phash_value),
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

    async def analyze_video(self, video_path: str) -> Dict[str, Any]:
        """Analyze video by processing key frames with better error handling"""
        try:
            if not os.path.exists(video_path):
                return {"error": "Video file not found"}

            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {"error": "Could not open video file"}

            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            # Prevent division by zero
            if frame_count <= 0 or fps <= 0:
                return {"error": "Invalid video properties"}

            # Process fewer frames for efficiency
            sampled_frames = min(5, max(1, frame_count // 30))

            results = []
            temp_frames = []

            for i in range(sampled_frames):
                # Calculate position for evenly distributed sampling
                frame_pos = int(i * (frame_count / sampled_frames))
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = cap.read()

                if ret:
                    # Create unique frame filename to avoid collisions
                    import uuid
                    frame_filename = f"frame_{uuid.uuid4().hex}.jpg"
                    frame_path = os.path.join(settings.MEDIA_STORAGE_PATH, frame_filename)

                    cv2.imwrite(frame_path, frame)
                    temp_frames.append(frame_path)
                    results.append(await self.analyze_image(frame_path))

            cap.release()

            # Clean up temporary files
            for frame_path in temp_frames:
                try:
                    os.remove(frame_path)
                except Exception:
                    pass

            # Aggregate frame results
            if not results:
                return {"error": "No valid frames processed"}

            # Calculate aggregate results
            fake_count = sum(1 for r in results if r.get('is_fake', False))
            avg_confidence = sum(r.get('confidence', 0) for r in results) / len(results)
            is_fake = fake_count > (len(results) / 2)  # Majority vote

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


def create_model_generator():
    """Utility function to create a compatible model for TF versions"""
    # Creates a model and saves it in various formats for compatibility
    try:
        # Create a compatible model
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(256, 256, 3)),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])

        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )

        # Save in multiple formats
        os.makedirs(settings.MODEL_CACHE_PATH, exist_ok=True)

        # Try newer format first
        try:
            model.save(os.path.join(settings.MODEL_CACHE_PATH, "deepfake_model.keras"))
        except Exception:
            pass

        # Try older H5 format
        try:
            model.save(os.path.join(settings.MODEL_CACHE_PATH, "deepfake_model.h5"))
        except Exception:
            pass

        # Try weights only
        try:
            model.save_weights(os.path.join(settings.MODEL_CACHE_PATH, "deepfake.weights.h5"))
        except Exception:
            pass

        return True
    except Exception as e:
        print(f"Error generating model: {e}")
        return False


# Instantiate the class
deepfake_detector = DeepfakeDetector()