# api_post.py

import asyncio

from api_logger_config import get_logger
from api_util_content_manager import user_picture_endpoint
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
