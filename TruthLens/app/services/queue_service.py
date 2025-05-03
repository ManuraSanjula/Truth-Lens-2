# import asyncio
#
# import aio_pika
# import json
# from app.utils.config import settings
# from app.utils.logger import logger
# from app.services.fake_news_detector import analyze_text
# from app.services.deepfake_detector import analyze_media
# from app.models.content import Content, ContentStatus, ContentType
# from app.models.results import Result
#
#
# async def start_consumers():
#     try:
#         connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
#
#         async with connection:
#             channel = await connection.channel()
#             await channel.set_qos(prefetch_count=1)
#
#             # Declare exchanges and queues
#             exchange = await channel.declare_exchange(
#                 "content_processing",
#                 type="direct",
#                 durable=True
#             )
#
#             # Text processing queue
#             text_queue = await channel.declare_queue(
#                 "text_processing",
#                 durable=True
#             )
#             await text_queue.bind(exchange, routing_key="text_processing")
#
#             # Media processing queue
#             media_queue = await channel.declare_queue(
#                 "media_processing",
#                 durable=True
#             )
#             await media_queue.bind(exchange, routing_key="media_processing")
#
#             # Start consumers
#             await text_queue.consume(process_text_message)
#             await media_queue.consume(process_media_message)
#
#             logger.info("Queue consumers started successfully")
#             while True:
#                 await asyncio.sleep(1)
#     except Exception as e:
#         logger.error(f"Error in queue consumer: {e}")
#         raise
#
#
# async def process_text_message(message: aio_pika.IncomingMessage):
#     async with message.process():
#         try:
#             data = json.loads(message.body.decode())
#             content_id = data["content_id"]
#
#             logger.info(f"Processing text content: {content_id}")
#
#             # Get content from DB
#             content = await Content.get(content_id)
#             if not content:
#                 logger.error(f"Content not found: {content_id}")
#                 return
#
#             if content.content_type not in [ContentType.TEXT, ContentType.URL]:
#                 logger.error(f"Invalid content type for text processing: {content.content_type}")
#                 return
#
#             # Analyze text
#             if content.raw_text:
#                 result = await analyze_text(content_id, content.raw_text)
#             elif content.source_url:
#                 # In a real system, you'd fetch the URL content here
#                 result = await analyze_text(content_id, f"Content from URL: {content.source_url}")
#             else:
#                 logger.error(f"No text content to analyze for {content_id}")
#                 return
#
#             if result:
#                 await Result.create(result)
#                 await Content.update_status(content_id, ContentStatus.COMPLETED)
#                 logger.info(f"Text analysis completed for {content_id}")
#             else:
#                 await Content.update_status(content_id, ContentStatus.FAILED)
#                 logger.error(f"Text analysis failed for {content_id}")
#         except Exception as e:
#             logger.error(f"Error processing text message: {e}")
#             if content_id:
#                 await Content.update_status(content_id, ContentStatus.FAILED)
#
#
# async def process_media_message(message: aio_pika.IncomingMessage):
#     async with message.process():
#         try:
#             data = json.loads(message.body.decode())
#             content_id = data["content_id"]
#
#             logger.info(f"Processing media content: {content_id}")
#
#             # Get content from DB
#             content = await Content.get(content_id)
#             if not content:
#                 logger.error(f"Content not found: {content_id}")
#                 return
#
#             if content.content_type not in [ContentType.IMAGE, ContentType.VIDEO]:
#                 logger.error(f"Invalid content type for media processing: {content.content_type}")
#                 return
#
#             if not content.file_path:
#                 logger.error(f"No file path for media content {content_id}")
#                 await Content.update_status(content_id, ContentStatus.FAILED)
#                 return
#
#             # Analyze media
#             media_type = "image" if content.content_type == ContentType.IMAGE else "video"
#             result = await analyze_media(content_id, content.file_path, media_type)
#
#             if result:
#                 await Result.create(result)
#                 await Content.update_status(content_id, ContentStatus.COMPLETED)
#                 logger.info(f"Media analysis completed for {content_id}")
#             else:
#                 await Content.update_status(content_id, ContentStatus.FAILED)
#                 logger.error(f"Media analysis failed for {content_id}")
#         except Exception as e:
#             logger.error(f"Error processing media message: {e}")
#             if content_id:
#                 await Content.update_status(content_id, ContentStatus.FAILED)