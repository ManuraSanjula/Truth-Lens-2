from motor.motor_asyncio import AsyncIOMotorClient
from redis import asyncio as aioredis
from TruthLens.app.utils.config import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    client: AsyncIOMotorClient = None
    redis: aioredis.Redis = None


db = Database()


async def init_db():
    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URL)
        logger.info("Connected to MongoDB")

        db.redis = aioredis.from_url(settings.REDIS_URL)
        logger.info("Connected to Redis")
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise


async def close_db():
    try:
        if db.client:
            db.client.close()
            logger.info("Closed MongoDB connection")

        if db.redis:
            await db.redis.close()
            logger.info("Closed Redis connection")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")