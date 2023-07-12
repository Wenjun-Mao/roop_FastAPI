# api_util_content_manager.py

import datetime
import logging
import os
import subprocess
import sys
import time
from typing import Optional
from urllib.parse import unquote

import requests
from api_app_config import (DEBUG, default_picture_path, default_video_path,
                            media_path, script_path, server_address)
from api_destination_handler import send_to_destination
from api_face_restore import pic_face_restore
from fastapi import BackgroundTasks, File, Form, HTTPException, UploadFile

logger = logging.getLogger(__name__)


def validate_inputs(
    content_type: str, content_name: str, file: Optional[UploadFile], url: Optional[str]
):
    video_template_folder = f"{media_path}/api_video_templates"
    mp4_files = [f for f in os.listdir(video_template_folder) if f.endswith(".mp4")]

    picture_template_folder = f"{media_path}/api_pic_templates"
    jpg_files = [f for f in os.listdir(picture_template_folder) if f.endswith(".jpg")]

    # Check if the content_name exists in the templates
    if content_type == "video" and f"{content_name}.mp4" not in mp4_files:
        raise HTTPException(
            status_code=400,
            detail="video not found in the video_template_folder folder.",
        )
    if content_type == "picture" and f"{content_name}.jpg" not in jpg_files:
        raise HTTPException(
            status_code=400,
            detail="Picture not found in the picture_template_folder folder.",
        )
    if not file and not url:
        raise HTTPException(
            status_code=400, detail="You must provide either a file or a URL."
        )


def get_url_with_retry(url: str, timeout: int = 15, max_attempts: int = 3):
    attempts = 0
    while attempts < max_attempts:
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()  # Raise exception if status code is not 200
            return response
        except (requests.Timeout, requests.HTTPError):
            attempts += 1
            time.sleep(2)  # Wait for 2 seconds before next attempt
    raise requests.Timeout(f"Failed to retrieve {url} after {max_attempts} attempts")


def save_incoming_file(file: Optional[UploadFile], url: Optional[str]):
    incoming_folder = f"{media_path}/api_incoming"
    os.makedirs(incoming_folder, exist_ok=True)
    incoming_file_path = os.path.normpath(
        os.path.join(incoming_folder, file.filename if file else os.path.basename(url))
    )

    if file:
        with open(incoming_file_path, "wb") as buffer:
            buffer.write(file.file.read())
    elif url:
        response = get_url_with_retry(url)
        with open(incoming_file_path, "wb") as buffer:
            buffer.write(response.content)

    return incoming_file_path


def run_script(
    content_type: str, incoming_file_path: str, content_name: str, face_restore: bool
):
    current_mmdd = datetime.datetime.now().strftime("%m-%d")
    current_ymdhms = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if content_type == "video":
        targert_path = os.path.normpath(
            f"{media_path}/api_video_templates/{content_name}.mp4"
        )
        output_dir = f"{media_path}/api_outgoing/video/{current_mmdd}"
        output_filename = f"{current_ymdhms}.mp4"
    elif content_type == "picture":
        targert_path = os.path.normpath(
            f"{media_path}/api_pic_templates/{content_name}.jpg"
        )
        output_dir = f"{media_path}/api_outgoing/pic/{current_mmdd}"
        output_filename = f"{current_ymdhms}.png"

    os.makedirs(output_dir, exist_ok=True)
    outgoing_file_path = os.path.join(output_dir, output_filename)
    file_path4subprocess = os.path.normpath(incoming_file_path)

    logger.info(f"file_path4subprocess: {file_path4subprocess}")
    logger.info(f"targert_path: {targert_path}")
    logger.info(f"outgoing_file_path: {outgoing_file_path}")

    try:
        proc = subprocess.Popen(
            [
                sys.executable,
                script_path,
                "--execution-provider",
                "cuda",
                "--source",
                file_path4subprocess,
                "--target",
                targert_path,
                "--output",
                outgoing_file_path,
                "--keep-fps",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = proc.communicate()
        return_code = proc.wait()

        if DEBUG:
            logger.info(f"stdout: {stdout.decode()}")

        if return_code != 0 or "No face in source path detected" in stdout.decode():
            logger.error(f"Script exited with return code: {return_code}")
            logger.error(f"stdout: {stdout.decode()}")
            logger.error(f"stderr: {stderr.decode()}")
            raise subprocess.CalledProcessError(return_code, proc.args, output=stdout)

    except subprocess.CalledProcessError as e:
        logger.error(f"Something went wrong with the algorithm. Error is {e}")
        if content_type == "video":
            return f"{server_address}/download_video/{default_video_path}"
        elif content_type == "picture":
            return f"{server_address}/download_video/{default_picture_path}"

    # Face restore and return the picture download link
    logger.info(f"face_restore: {face_restore}\n")
    if content_type == "picture" and face_restore != 111:
        logger.info(f"Send for face_restore: {outgoing_file_path}")
        output_filename = pic_face_restore(
            outgoing_file_path, current_mmdd, current_ymdhms
        )
        return f"{server_address}/download_pic/{current_mmdd}/{output_filename}"
    elif content_type == "picture" and face_restore == 111:
        return f"{server_address}/download_pic/{current_mmdd}/{output_filename}"

    return f"{server_address}/download_video/{current_mmdd}/{output_filename}"


def schedule_background_task(
    background_tasks: BackgroundTasks, id_value: str, download_link: str
):
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
            url = unquote(url) if url else None
            logger.info(
                "content_name: %s, face_restore: %s, file: %s, url: %s",
                content_name,
                face_restore,
                file,
                url,
            )

            id_value = id
            logger.info(f"Processing request for id: {id_value}")

            validate_inputs(content_type, content_name, file, url)
            incoming_file_path = save_incoming_file(file, url)
            download_link = run_script(
                content_type, incoming_file_path, content_name, face_restore
            )
            schedule_background_task(background_tasks, id_value, download_link)

            return {"download_link": download_link}
