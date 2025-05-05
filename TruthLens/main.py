from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from TruthLens.app.api.endpoints import content, results, users
from TruthLens.app.utils.database import init_db
from TruthLens.app.utils.config import settings
import logging
from TruthLens.app.api.endpoints import video
from TruthLens.app.api.endpoints import detection
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    await init_db()
    logger.info("Application startup complete")
    yield
    # Shutdown code
    logger.info("Application shutdown")

app = FastAPI(
    title="Fake Content Detection API",
    description="API for detecting fake news and deepfake media",
    version="1.0.0",
    lifespan = lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(content.router, prefix="/api/v1/content", tags=["content"])
app.include_router(results.router, prefix="/api/v1/results", tags=["results"])
app.include_router(video.router)
app.include_router(detection.router)

# @app.on_event("startup")
# async def startup_event():
#     await init_db()
#     logger.info("Application startup complete")


@app.get("/")
async def root():
    return {"message": "Fake Content Detection API"}