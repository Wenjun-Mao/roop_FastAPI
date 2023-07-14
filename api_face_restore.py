# api_face_restore.py

import logging
import time

import webuiapi
from api_app_config import sd_webui_host, sd_webui_port
from PIL import Image

logger = logging.getLogger(__name__)


def apply_face_restoration_to_picture(outgoing_file_path: str):
    start_time = time.time()
    img = Image.open(outgoing_file_path)
    api = webuiapi.WebUIApi(sd_webui_host, sd_webui_port)
    restored_img = api.extra_single_image(
        image=img,
        upscaling_resize=1,
        gfpgan_visibility=1,
    )
    logger.info("Face_restore done in %s seconds.", round(time.time() - start_time, 2))
    restored_img.image.save(outgoing_file_path)
