# import asyncio
# import aio_pika
# import json
# from app.services.deepfake_detector import DeepfakeDetector
# from app.models import Content, Result
# from app.utils import logger, settings
#
# async def process_message(message: aio_pika.IncomingMessage):
#     async with message.process():
#         data = json.loads(message.body.decode())
#         content_id = data["content_id"]
#
#         # Get content from DB
#         content = await Content.get(content_id)
#
#         # Connect to FakeNewsDetector service
#         result = await fake_news_detector.analyze_text(content.raw_text)
#
#         # Save results
#         await Result.create(
#             content_id=content_id,
#             detection_type="fake_news",
#             is_fake=result["is_fake"],
#             confidence=result["confidence"],
#             explanation=result["details"]
#         )
#
#         await Content.update_status(content_id, "completed")