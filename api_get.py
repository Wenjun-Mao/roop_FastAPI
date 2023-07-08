# api_get.py

from fastapi import FastAPI
from fastapi.responses import FileResponse
from api_app_config import media_path


get_file_app = FastAPI()


@get_file_app.get("/download_video/{date}/{video_name}")
async def download_video(date: str, video_name: str):
    file_path = f"{media_path}/api_outgoing/video/{date}/{video_name}"
    return FileResponse(file_path)
