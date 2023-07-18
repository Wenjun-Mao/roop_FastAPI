import os
os.environ['OMP_NUM_THREADS'] = '1'

def change_directory() -> None:
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")

    parent_dir = os.path.dirname(cwd)
    print(f"Parent directory: {parent_dir}")
    new_dir = os.path.join(parent_dir, "roop_backend")

    if os.path.exists(new_dir):
        os.chdir(new_dir)
    else:
        print(f"Directory {new_dir} does not exist")

    cwd = os.getcwd()
    print(f"New working directory: {cwd}")  

change_directory()

from roop.core import *

roop.globals.frame_processors = ["face_swapper"]
roop.globals.headless = True
roop.globals.keep_fps = True
roop.globals.keep_audio = True
roop.globals.keep_frames = False
roop.globals.many_faces = False
roop.globals.video_encoder = "libx264"
roop.globals.video_quality = 18
roop.globals.max_memory = suggest_max_memory()
roop.globals.execution_providers = decode_execution_providers(["cuda"])
roop.globals.execution_threads = suggest_execution_threads()


# Refactor some functions from roop.core
def update_status(message: str, scope: str = 'ROOP.CORE') -> None:
    print(f'[{scope}] {message}')
    print(message)
    print(scope)
    if message == 'No face in source path detected.' and scope == 'ROOP.FACE-SWAPPER':
        print('WOW WOW WOW')


def start() -> None:
    for frame_processor in get_frame_processors_modules(roop.globals.frame_processors):
        if not frame_processor.pre_start():
            return
    # process image to image
    if has_image_extension(roop.globals.target_path):
        shutil.copy2(roop.globals.target_path, roop.globals.output_path)
        for frame_processor in get_frame_processors_modules(roop.globals.frame_processors):
            update_status('Progressing...', frame_processor.NAME)
            frame_processor.process_image(roop.globals.source_path, roop.globals.output_path, roop.globals.output_path)
            frame_processor.post_process()
            release_resources()
        if is_image(roop.globals.target_path):
            update_status('Processing to image succeed!')
        else:
            update_status('Processing to image failed!')
        return
    # process image to videos
    update_status('Creating temp resources...')
    create_temp(roop.globals.target_path)
    update_status('Extracting frames...')
    extract_frames(roop.globals.target_path)
    temp_frame_paths = get_temp_frame_paths(roop.globals.target_path)
    for frame_processor in get_frame_processors_modules(roop.globals.frame_processors):
        update_status('Progressing...', frame_processor.NAME)
        frame_processor.process_video(roop.globals.source_path, temp_frame_paths)
        frame_processor.post_process()
        release_resources()
    # handles fps
    if roop.globals.keep_fps:
        update_status('Detecting fps...')
        fps = detect_fps(roop.globals.target_path)
        update_status(f'Creating video with {fps} fps...')
        create_video(roop.globals.target_path, fps)
    else:
        update_status('Creating video with 30.0 fps...')
        create_video(roop.globals.target_path)
    # handle audio
    if roop.globals.keep_audio:
        if roop.globals.keep_fps:
            update_status('Restoring audio...')
        else:
            update_status('Restoring audio might cause issues as fps are not kept...')
        restore_audio(roop.globals.target_path, roop.globals.output_path)
    else:
        move_temp(roop.globals.target_path, roop.globals.output_path)
    # clean and validate
    clean_temp(roop.globals.target_path)
    if is_video(roop.globals.target_path):
        update_status('Processing to video succeed!')
    else:
        update_status('Processing to video failed!')

def run(**kwargs) -> None:
    if not pre_check():
        print('pre-check failed')
        return
    for frame_processor in get_frame_processors_modules(roop.globals.frame_processors):
        if not frame_processor.pre_check():
            print(f'pre-check failed: {frame_processor.__name__}')
            return
    limit_resources()
    start()


def release_resources() -> None:
    torch.cuda.empty_cache()


def swap_pre_start() -> bool:
    print('------------------New swap_pre_start------------------')
    if not is_image(roop.globals.source_path):
        update_status('Select an image for source path.', NAME)
        return False
    elif not get_one_face(cv2.imread(roop.globals.source_path)):
        update_status('No face in source path detected.', NAME)
        return False
    if not is_image(roop.globals.target_path) and not is_video(roop.globals.target_path):
        update_status('Select an image or video for target path.', NAME)
        return False
    return True

roop.core.update_status = update_status
roop.core.release_resources = release_resources
import roop.processors.frame.face_swapper
roop.processors.frame.face_swapper.pre_start = swap_pre_start

from fastapi import FastAPI
from pydantic import BaseModel

class Body(BaseModel):
    source_path: str
    target_path: str
    output_path: str

app = FastAPI()

@app.post("/")
async def root(body: Body):
    roop.globals.source_path = body.source_path
    roop.globals.target_path = body.target_path
    roop.globals.output_path = body.output_path
    run()
    return {"message": "Alo Job finished"}
