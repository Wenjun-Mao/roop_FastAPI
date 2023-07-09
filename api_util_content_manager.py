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
from api_app_config import media_path, server_address, script_path, DEBUG, sd_webui_host, sd_webui_port
from api_face_restore import pic_face_restore

logger = logging.getLogger(__name__)

def validate_inputs(content_type: str, content_name: str, file: Optional[UploadFile], url: Optional[str]):
    video_template_folder = f"{media_path}/api_video_templates"
    mp4_files = [f for f in os.listdir(video_template_folder) if f.endswith('.mp4')]

    picture_template_folder = f"{media_path}/api_pic_templates"
    jpg_files = [f for f in os.listdir(picture_template_folder) if f.endswith('.jpg')]

    # Check if the content_name exists in the templates, raise an error if not found
    if content_type == "video" and f"{content_name}.mp4" not in mp4_files:
        raise HTTPException(status_code=400, detail="The requested content_name was not found in the video_template_folder folder.")
    if content_type == "picture" and f"{content_name}.jpg" not in jpg_files:
        raise HTTPException(status_code=400, detail="The requested content_name was not found in the picture_template_folder folder.")
    if not file and not url:
        raise HTTPException(status_code=400, detail="You must provide either a file or a URL.")

def save_incoming_file(file: Optional[UploadFile], url: Optional[str]):
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

    return incoming_file_path

def run_script(content_type: str, incoming_file_path: str, content_name: str, face_restore: bool):
    current_mmdd = datetime.datetime.now().strftime('%m-%d')
    current_ymdhms = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    if content_type == "video":
        targert_path = os.path.normpath(f"{media_path}/api_video_templates/{content_name}.mp4")
        output_dir = f"{media_path}/api_outgoing/video/{current_mmdd}"
        output_filename = f"{current_ymdhms}.mp4"
    elif content_type == "picture":
        targert_path = os.path.normpath(f"{media_path}/api_pic_templates/{content_name}.jpg")
        output_dir = f"{media_path}/api_outgoing/pic/{current_mmdd}"
        output_filename = f"{current_ymdhms}.png"

    os.makedirs(output_dir, exist_ok=True)
    outgoing_file_path = os.path.join(output_dir, output_filename)
    incoming_file_path4subprocess = os.path.normpath(incoming_file_path)

    logger.info(f"incoming_file_path4subprocess: {incoming_file_path4subprocess}")
    logger.info(f"targert_path: {targert_path}")
    logger.info(f"outgoing_file_path: {outgoing_file_path}")

    try:
        proc = subprocess.Popen([
            sys.executable,
            script_path,
            "--execution-provider", "cuda",
            "--source", incoming_file_path4subprocess,
            "--target", targert_path,
            "--output", outgoing_file_path,
            "--keep-fps",
        ], stdout=None if DEBUG else subprocess.DEVNULL, stderr=None if DEBUG else subprocess.DEVNULL) # only show subprocess logs if DEBUG is True

        return_code = proc.wait()  # This will get the return code

        if return_code != 0:
            logger.error(f"Script exited with return code: {return_code}")
            raise subprocess.CalledProcessError(return_code, proc.args)

    except subprocess.CalledProcessError as e:
        logger.error(f"Sorry, something went wrong with the face algorithm. The error is {e}")
        raise HTTPException(status_code=500, detail=f"Sorry, something went wrong with the face algorithm. The error is {e}")
    
    # Face restore and return the picture download link
    logger.info(f"face_restore: {face_restore}\n")
    if content_type == "picture" and face_restore != 111:
        logger.info(f"Send for face_restore: {outgoing_file_path}")
        output_filename = pic_face_restore(outgoing_file_path, current_mmdd, current_ymdhms)
        return f"{server_address}/download_pic/{current_mmdd}/{output_filename}"
    elif content_type == "picture" and face_restore == 111:
        return f"{server_address}/download_pic/{current_mmdd}/{output_filename}"

    # Return the video download link
    return f"{server_address}/download_video/{current_mmdd}/{output_filename}"

def schedule_background_task(background_tasks: BackgroundTasks, id_value: str, download_link: str):
    background_tasks.add_task(send_to_destination, id_value, download_link)

def upload_user_picture(app, lock):
    @app.post("/")
    async def upload_picture(
        background_tasks: BackgroundTasks,
        content_type: str = Form(...),
        content_name: str = Form(...),
        face_restore: Optional[int] = Form(0),
        file: Optional[UploadFile] = File(None),
        url: Optional[str] = Form(None),
        id: str = Form(...),
    ):
        async with lock:
            logger.info(f"content_name: {content_name}, face_restore: {face_restore}, file: {file}, url: {url}")

            id_value = id
            logger.info(f"Processing request for id: {id_value}")

            validate_inputs(content_type, content_name, file, url)
            incoming_file_path = save_incoming_file(file, url)
            download_link = run_script(content_type, incoming_file_path, content_name, face_restore)
            schedule_background_task(background_tasks, id_value, download_link)

            return {"download_link": download_link}
