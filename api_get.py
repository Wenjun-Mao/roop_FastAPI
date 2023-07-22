# api_get.py

import logging

from api_app_config import media_path, default_picture_path, default_video_path
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %p",
)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"An error occurred: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An error occurred. Please try again later."},
    )

@app.get("/download_video/{date}/{video_name}")
async def download_video(date: str, video_name: str):
    try:
        file_path = f"{media_path}/api_outgoing/video/{date}/{video_name}"
        logger.info(f"Downloading video: {file_path}")
        return FileResponse(file_path)
    except FileNotFoundError:
        logger.info(f"Video not found, returning default video")
        default_video_file = f"{media_path}/api_outgoing/video/{default_video_path}"
        return FileResponse(default_video_file)


@app.get("/download_pic/{date}/{pic_name}")
async def download_pic(date: str, pic_name: str):
    try:
        file_path = f"{media_path}/api_outgoing/pic/{date}/{pic_name}"
        logger.info(f"Downloading picture: {file_path}")
        return FileResponse(file_path)
    except FileNotFoundError:
        logger.info(f"Picture not found, returning default picture")
        default_pic_file = f"{media_path}/api_outgoing/pic/{default_picture_path}"
        return FileResponse(default_pic_file)
