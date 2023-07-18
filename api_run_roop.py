import os
os.environ['OMP_NUM_THREADS'] = '1'

def change_directory() -> None:
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")

    parent_dir = os.path.dirname(cwd)
    print(f"Parent directory: {parent_dir}")
    new_dir = os.path.join(parent_dir, "roop")

    if os.path.exists(new_dir):
        os.chdir(new_dir)
    else:
        print(f"Directory {new_dir} does not exist")

    cwd = os.getcwd()
    print(f"New working directory: {cwd}")  

change_directory()

from fastapi import FastAPI
from pydantic import BaseModel

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





def run(**kwargs) -> None:
    if not pre_check():
        print('pre-check failed')
        return
    for frame_processor in get_frame_processors_modules(roop.globals.frame_processors):
        if not frame_processor.pre_check():
            print(f'pre-check failed: {frame_processor.__name__}')
            return
    limit_resources()
    print('headless mode')
    start()


def release_resources() -> None:
    print('--------releasing resources--------')
    torch.cuda.empty_cache()


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
