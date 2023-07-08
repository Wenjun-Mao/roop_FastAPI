# api_util_content_manager.py

from fastapi import BackgroundTasks, HTTPException, Form, File, UploadFile
from typing import Optional
import logging
from api_destination_handler import send_to_destination
import subprocess
import sys
import os
import datetime
import requests
from urllib.parse import unquote
from api_app_config import media_path, server_address, script_path

logger = logging.getLogger(__name__)

def upload_user_picture(app, lock):
    @app.post("/")
    async def upload_picture(
        background_tasks: BackgroundTasks,
        content_name: str = Form(...),
        face_restore: Optional[int] = Form(0),
        file: Optional[UploadFile] = File(None),
        url: Optional[str] = Form(None),
        id: str = Form(...),
    ):
        async with lock:
            current_mmdd = datetime.datetime.now().strftime('%m-%d')
            current_ymdhms = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            logger.info(f"content_name: {content_name}, face_restore: {face_restore}, file: {file}, url: {url}")

            # Extract the id from the data
            id_value = id

            logger.info(f"Processing request for id: {id_value}")

            video_template_folder = f"{media_path}/api_video_templates"
            mp4_files = [f for f in os.listdir(video_template_folder) if f.endswith('.mp4')]

            # Check if the content_name exists in the list of MP4 files, raise an error if not found
            if f"{content_name}.mp4" not in mp4_files:
                raise HTTPException(status_code=400, detail="The requested content_name was not found in the video_template_folder folder.")
            if not file and not url:
                raise HTTPException(status_code=400, detail="You must provide either a file or a URL.")
            
            # Save picture to a local hard drive folder
            incoming_folder = f"{media_path}/api_incoming"
            os.makedirs(incoming_folder, exist_ok=True)
            incoming_file_path = os.path.normpath(os.path.join(incoming_folder, file.filename if file else os.path.basename(url)))
            if file:
                with open(incoming_file_path, "wb") as buffer:
                    buffer.write(file.file.read())
            elif url:
                decoded_url = unquote(url)
                response = requests.get(decoded_url)
                response.raise_for_status()
                with open(incoming_file_path, "wb") as buffer:
                    buffer.write(response.content)

            # Call the Python script with command line arguments
            targert_video_path = os.path.normpath(f"{media_path}/api_video_templates/{content_name}.mp4")

            output_dir = f"{media_path}/api_outgoing/video/{current_mmdd}"
            os.makedirs(output_dir, exist_ok=True)
            output_filename = f"{current_ymdhms}.mp4"
            outgoing_file_path = os.path.join(output_dir, output_filename)

            if file:
                incoming_file_path4subprocess = os.path.normpath(os.path.join(f"{media_path}/api_incoming", file.filename))
            elif url:
                incoming_file_path4subprocess = os.path.normpath(os.path.join(f"{media_path}/api_incoming", os.path.basename(url)))

            logger.info(f"incoming_file_path4subprocess: {incoming_file_path4subprocess}")
            logger.info(f"targert_pic_path: {targert_video_path}")
            logger.info(f"outgoing_file_path: {outgoing_file_path}")

            try:
                subprocess.run([
                    sys.executable,
                    script_path,
                    "--execution-provider", "cuda",
                    "--source", incoming_file_path4subprocess,
                    "--target", targert_video_path,
                    "--output", outgoing_file_path,
                    "--keep-fps",
                ], check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

            except subprocess.CalledProcessError as e:
                print("subprocess output:", e.output.decode(errors='ignore'))
                print("subprocess error:", e.stderr.decode(errors='ignore'))
                raise HTTPException(status_code=500, detail=f"Sorry, we can't find a face in the picture.*************{e}*************")
            
            # Return a link to download the video file
            download_link = f"{server_address}/download_video/{current_mmdd}/{output_filename}"

            # Using FastAPI's BackgroundTasks
            background_tasks.add_task(send_to_destination, id_value, download_link)

            return {"download_link": download_link}