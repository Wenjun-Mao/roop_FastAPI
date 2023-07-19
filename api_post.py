# api_post_refactor.py

import asyncio
import os
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['NO_FACE'] = '0'

from api_logger_config import get_logger
from api_refactor_util import *
from fastapi import FastAPI
from fastapi.responses import JSONResponse

logger = get_logger(__name__)
app = FastAPI()
lock = asyncio.Lock()


@app.exception_handler(ConnectionResetError)
async def handle_connection_reset_error(request, exc):
    logger.error(f"ConnectionResetError occurred: {exc}")
    return JSONResponse(
        status_code=500, content={"message": "---Unexpected connection error---"}
    )


user_picture_endpoint(app, lock)
