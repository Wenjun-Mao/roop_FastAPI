# api_get.py

import logging

from api_app_config import media_path
from fastapi import FastAPI
from fastapi.responses import FileResponse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %p",
)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/download_video/{date}/{video_name}")
async def download_video(date: str, video_name: str):
    file_path = f"{media_path}/api_outgoing/video/{date}/{video_name}"
    logger.info(f"Downloading video: {file_path}")
    return FileResponse(file_path)


@app.get("/download_pic/{date}/{pic_name}")
async def download_pic(date: str, pic_name: str):
    file_path = f"{media_path}/api_outgoing/pic/{date}/{pic_name}"
    logger.info(f"Downloading picture: {file_path}")
    return FileResponse(file_path)