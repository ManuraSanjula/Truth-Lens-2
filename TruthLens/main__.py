# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.api.endpoints import content, results, users
# from app.utils.database import init_db
# from app.utils.config import settings
# import logging
# import asyncio
# from workers.text_worker import main as text_worker
# from workers.media_worker import main as media_worker
# from multiprocessing import Process
#
# logger = logging.getLogger(__name__)
#
#
# def run_worker(target):
#     """Run a worker in a separate process"""
#
#     def wrapper():
#         asyncio.run(target())
#
#     Process(target=wrapper).start()
#
#
# app = FastAPI(
#     title="Fake Content Detection API",
#     description="Self-contained system for detecting fake news and deepfakes",
#     version="2.0"
# )
#
# # CORS setup
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.CORS_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Include routers
# app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
# app.include_router(content.router, prefix="/api/v1/content", tags=["content"])
# app.include_router(results.router, prefix="/api/v1/results", tags=["results"])
#
#
# @app.on_event("startup")
# async def startup_event():
#     await init_db()
#
#     # Start worker processes
#     run_worker(text_worker)
#     run_worker(media_worker)
#
#     logger.info("Application and workers started successfully")
#
#
# @app.get("/")
# async def root():
#     return {
#         "message": "Fake Content Detection System",
#         "version": "2.0",
#         "features": [
#             "Text/URL fake news detection",
#             "Image manipulation detection",
#             "Deepfake video analysis",
#             "Self-contained AI models",
#             "Local processing only"
#         ]
#     }