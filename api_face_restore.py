# api_face_restore.py

import logging
import os

import cv2
import numpy as np
import webuiapi
from api_app_config import media_path, sd_webui_host, sd_webui_port
from PIL import Image

logger = logging.getLogger(__name__)


def save_output_picture_from_sd_return(opened_image, current_mmdd: str, current_ymdhms: str):
    output_dir = f"{media_path}/api_outgoing/pic/{current_mmdd}"
    # Convert the PIL img to a NumPy array and change the channel order to BGR
    img_np = np.array(opened_image)[:, :, ::-1]
    # Encode the image as a JPEG byte array
    img_bytes = cv2.imencode(".jpg", img_np)[1].tobytes()

    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"{current_ymdhms}.jpg"
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, "wb") as f:
        f.write(img_bytes)

    return output_filename


def apply_face_restoration_to_picture(outgoing_file_path: str, current_mmdd: str, current_ymdhms: str):
    img = Image.open(outgoing_file_path)
    api = webuiapi.WebUIApi(sd_webui_host, sd_webui_port)
    restored_img = api.extra_single_image(
        image=img,
        upscaling_resize=1,
        gfpgan_visibility=1,
    )
    logger.info("SD job done.")
    output_filename = save_output_picture_from_sd_return(
        restored_img.image, current_mmdd, current_ymdhms
    )
    logger.info(f"Face_restored file: {output_filename}")
    return output_filename
