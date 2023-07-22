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
        content={"message": "Error. Please try again later."},
    )


@app.get("/download_video/{date}/{video_name}")
async def download_video(date: str, video_name: str):
    file_path = f"{media_path}/api_outgoing/video/{date}/{video_name}"
    logger.info(f"Downloading video: {file_path}")
    return FileResponse(file_path, headers={"Cache-Control": "public, max-age=3600"})


@app.get("/download_pic/{date}/{pic_name}")
async def download_pic(date: str, pic_name: str):
    file_path = f"{media_path}/api_outgoing/pic/{date}/{pic_name}"
    logger.info(f"Downloading picture: {file_path}")
    return FileResponse(file_path, headers={"Cache-Control": "public, max-age=3600"})
