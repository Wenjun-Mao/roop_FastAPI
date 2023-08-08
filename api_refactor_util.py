# api_refactor_util.py

import os

from api_refactor_roop_func2 import *
from api_util_content_manager import *


def run_media_processing_script(
    content_type: str, incoming_file_path: str, content_name: str, face_restore: bool
):
    current_mmdd = datetime.datetime.now().strftime("%m-%d")
    current_ymdhms = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    targert_path, output_filename, outgoing_file_path = create_outgoing_paths(
        content_type, content_name, current_mmdd, current_ymdhms
    )

    file_path4subprocess = os.path.normpath(incoming_file_path)
    if DEBUG:
        logger.info(f"file_path4subprocess: {file_path4subprocess}")
        logger.info(f"targert_path: {targert_path}")
        logger.info(f"outgoing_file_path: {outgoing_file_path}")

    start_time = time.time()
    try:
        roop.globals.source_path = file_path4subprocess
        roop.globals.target_path = targert_path
        roop.globals.output_path = outgoing_file_path
        run()
        print("noface: ", os.environ.get("NO_FACE"))
    except Exception as e:
        logger.error(f"Something went wrong with the algorithm. Error is {e}")

    if os.environ.get("NO_FACE") == "1":
        if content_type == "video":
            # return f"{server_address}/download_video/{default_video_path}"
            return "1"
        elif content_type == "picture":
            # return f"{server_address}/download_pic/{default_picture_path}"
            return "1"

    logger.info("Script finished in %s seconds.", round(time.time() - start_time, 2))

    # face restore
    if content_type == "picture" and face_restore != 111:
        if DEBUG:
            logger.info(f"Send for face_restore: {outgoing_file_path}")
        apply_face_restoration_to_picture(outgoing_file_path)
        return f"{server_address}/download_pic/{current_mmdd}/{output_filename}"
    elif content_type == "picture" and face_restore == 111:
        return f"{server_address}/download_pic/{current_mmdd}/{output_filename}"

    return f"{server_address}/download_video/{current_mmdd}/{output_filename}"


def user_picture_endpoint(app, lock):
    @app.post("/")
    async def process_user_picture(
        background_tasks: BackgroundTasks,
        content_type: str = Form(...),
        content_name: str = Form(...),
        face_restore: Optional[int] = Form(0),
        file: Optional[UploadFile] = File(None),
        url: Optional[str] = Form(None),
        id: str = Form(...),
    ):
        os.environ["NO_FACE"] = "0"
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
        incoming_file_path = create_incoming_file_path(file, url)
        save_incoming_file(file, url, incoming_file_path)

        async with lock:
            download_link = run_media_processing_script(
                content_type, incoming_file_path, content_name, face_restore
            )
            logger.info(f"face swap successful for id: {id_value}")
            logger.info(f"download_link: {download_link}")
        schedule_data_send_task(background_tasks, id_value, download_link)

        return {"download_link": download_link}
