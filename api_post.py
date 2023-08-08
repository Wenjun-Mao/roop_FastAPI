# api_post_refactor.py

import asyncio
import os

os.environ["OMP_NUM_THREADS"] = "1"

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from api_logger_config import get_logger
from api_refactor_util import *

logger = get_logger(__name__)
app = FastAPI()
lock = asyncio.Lock()


@app.exception_handler(ConnectionResetError)
async def handle_connection_reset_error(request, exc):
    logger.error(f"ConnectionResetError occurred: {exc}")
    return JSONResponse(
        status_code=500, content={"message": "---Unexpected connection error---"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"An error occurred: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An error occurred. Please try again later."},
    )


user_picture_endpoint(app, lock)
