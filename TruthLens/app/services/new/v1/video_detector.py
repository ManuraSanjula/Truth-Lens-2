import cv2
import os
import numpy as np
from typing import List, Dict, Optional, Tuple
from TruthLens.app.utils.config import settings
from TruthLens.app.utils.logger import logger
from TruthLens.app.services.deepfake_detector import DeepfakeDetector
from TruthLens.app.models.result import Result
import asyncio
from concurrent.futures import ThreadPoolExecutor


class VideoProcessor:
    def __init__(self):
        self.detector = DeepfakeDetector()
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def process_video(self, video_path: str, content_id: str) -> List[Result]:
        """Main video processing pipeline

        Args:
            video_path: Path to the video file to be processed
            content_id: Unique identifier for the content being analyzed

        Returns:
            List of Result objects with deepfake detection results
        """
        try:
            # Step 1: Extract key frames
            frames = await self._extract_key_frames(video_path)
            if not frames:
                logger.warning(f"No frames extracted from video {video_path}")
                return [self._create_error_result(content_id, "No frames could be extracted from the video")]

            # Step 2: Process frames in parallel
            frame_results = []
            for i, frame in enumerate(frames):
                try:
                    # Process each frame in the thread pool
                    result = await asyncio.get_event_loop().run_in_executor(
                        self.executor,
                        self._process_frame_sync,  # Using sync version
                        frame,
                        i,
                        len(frames))
                    frame_results.append(result)
                except Exception as e:
                    logger.error(f"Frame {i} processing failed: {e}")
                    frame_results.append({
                        "frame_num": i,
                        "error": str(e)
                    })

            # Step 3: Aggregate results
            return await self._generate_final_results(frame_results, content_id)

        except Exception as e:
            logger.error(f"Video processing failed: {e}")
            return [self._create_error_result(content_id, f"Video processing failed: {str(e)}")]

    async def _extract_key_frames(self, video_path: str, num_frames: int = 10) -> List[np.ndarray]:
        """Extract representative frames from video

        Args:
            video_path: Path to the video file
            num_frames: Number of frames to extract (default: 10)

        Returns:
            List of extracted frames as numpy arrays in RGB format
        """
        try:
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return []

            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Could not open video file: {video_path}")
                return []

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames == 0:
                logger.error(f"Video has no frames: {video_path}")
                cap.release()
                return []

            # Distribute frame selection evenly across the video
            frame_indices = np.linspace(0, total_frames - 1, min(num_frames, total_frames), dtype=int)

            frames = []
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                else:
                    logger.warning(f"Failed to read frame {idx} from video {video_path}")

            cap.release()

            if not frames:
                logger.error(f"No frames could be read from video {video_path}")

            return frames
        except Exception as e:
            logger.error(f"Frame extraction failed: {e}")
            return []

    def _process_frame_sync(self, frame: np.ndarray, frame_num: int, total_frames: int) -> Dict:
        """Synchronous version of frame processing for thread pool

        Args:
            frame: Frame to process as numpy array
            frame_num: Index of the frame
            total_frames: Total number of frames being processed

        Returns:
            Dictionary with frame analysis results
        """
        try:
            # Create temp directory if it doesn't exist
            os.makedirs(settings.MEDIA_STORAGE_PATH, exist_ok=True)

            # Save temporary frame for analysis
            frame_path = os.path.join(settings.MEDIA_STORAGE_PATH, f"frame_{frame_num}.jpg")
            cv2.imwrite(frame_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

            # Analyze frame - using synchronous version or running coroutine in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.detector.analyze_image(frame_path))
            finally:
                loop.close()

            # Clean up
            try:
                os.remove(frame_path)
            except Exception as e:
                logger.warning(f"Could not remove temp frame {frame_path}: {e}")

            return {
                "frame_num": frame_num,
                "total_frames": total_frames,
                "is_fake": result["is_fake"],
                "confidence": result["confidence"],
                "details": result.get("details", {})
            }
        except Exception as e:
            logger.error(f"Frame {frame_num} processing failed: {e}")
            return {
                "frame_num": frame_num,
                "error": str(e)
            }

    async def _generate_final_results(self, frame_results: List[Dict], content_id: str) -> List[Result]:
        """Generate final results from frame analyses

        Args:
            frame_results: List of dictionaries with frame analysis results
            content_id: Unique identifier for the content being analyzed

        Returns:
            List of Result objects with aggregated analysis results
        """
        valid_results = [r for r in frame_results if "error" not in r and isinstance(r, dict)]

        if not valid_results:
            logger.error("No valid frames processed - all frames failed analysis")
            return [self._create_error_result(content_id, "All frame analyses failed")]

        # Calculate aggregate confidence
        avg_confidence = sum(r["confidence"] for r in valid_results) / len(valid_results)

        # Determine if the video is fake based on configured threshold
        fake_frame_count = sum(r["is_fake"] for r in valid_results)
        fake_frame_percentage = fake_frame_count / len(valid_results) if valid_results else 0
        is_fake = fake_frame_percentage >= settings.FAKE_DETECTION_THRESHOLD if hasattr(settings,
                                                                                        'FAKE_DETECTION_THRESHOLD') else any(
            r["is_fake"] for r in valid_results)

        # Create main result
        main_result = Result(
            content_id=content_id,
            detection_type="deepfake",
            is_fake=is_fake,
            confidence=avg_confidence,
            explanation=f"Analyzed {len(valid_results)}/{len(frame_results)} frames. {fake_frame_count} frames detected as fake.",
            model_used="CNN+ELA",
            model_version="1.0"
        )

        return [main_result]

    def _create_error_result(self, content_id: str, error_msg: str) -> Result:
        """Create an error result for when processing fails

        Args:
            content_id: Unique identifier for the content
            error_msg: Error message to include in the result

        Returns:
            Result object with error information
        """
        return Result(
            content_id=content_id,
            detection_type="deepfake",
            is_fake=False,
            confidence=0.0,
            explanation=error_msg,
            model_used="error_handling",
            model_version="1.0"
        )


# Singleton instance
video_processor = VideoProcessor()