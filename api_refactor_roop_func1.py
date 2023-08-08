# api_refactor_roop_func1.py

import os

import torch


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


def update_status(message: str, scope: str = "ROOP.CORE") -> None:
    print(f"[{scope}] {message}")
    print(message)
    print(scope)
    if message == "No face in source path detected." and scope == "ROOP.FACE-SWAPPER":
        print("WOW WOW WOW")
        noface = 1


def release_resources() -> None:
    torch.cuda.empty_cache()
