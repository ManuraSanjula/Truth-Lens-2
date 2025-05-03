# import asyncio
# import aio_pika
# import json
# from app.services.deepfake_detector import DeepfakeDetector
# from app.models import Content, Result
# from app.utils import logger, settings
#
#
# async def process_media_message(message: aio_pika.IncomingMessage):
#     async with message.process():
#         try:
#             data = json.loads(message.body.decode())
#             content_id = data["content_id"]
#
#             logger.info(f"Processing media content: {content_id}")
#             content = await Content.get(content_id)
#
#             if not content or not content.file_path:
#                 logger.error(f"Invalid media content: {content_id}")
#                 return
#
#             detector = DeepfakeDetector()
#
#             if content.content_type == "image":
#                 analysis = await detector.analyze_image(content.file_path)
#             else:  # video
#                 analysis = await detector.analyze_video(content.file_path)
#
#             result = Result(
#                 content_id=content_id,
#                 detection_type="deepfake" if content.content_type == "video" else "image_manipulation",
#                 is_fake=analysis["is_fake"],
#                 confidence=analysis["confidence"],
#                 explanation=str(analysis.get("details", "")),
#                 model_used=analysis["model_used"],
#                 model_version="1.0"
#             )
#
#             await result.create()
#             await Content.update_status(content_id, "completed")
#
#         except Exception as e:
#             logger.error(f"Media processing failed: {e}")
#             if content_id:
#                 await Content.update_status(content_id, "failed")
#
#
# async def main():
#     connection = await aio_pika.connect(settings.RABBITMQ_URL)
#     channel = await connection.channel()
#     queue = await channel.declare_queue("media_queue", durable=True)
#
#     logger.info("Media worker started, waiting for messages...")
#     await queue.consume(process_media_message)
#
#     while True:
#         await asyncio.sleep(1)
#
#
# if __name__ == "__main__":
#     asyncio.run(main())