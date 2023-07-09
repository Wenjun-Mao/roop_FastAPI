# api_post.py

import asyncio
import logging

from api_util_content_manager import upload_user_picture
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %p",
)
logger = logging.getLogger(__name__)

app = FastAPI()
lock = asyncio.Lock()


@app.exception_handler(ConnectionResetError)
async def handle_connection_reset_error(request, exc):
    logging.error(f"ConnectionResetError occurred: {exc}")
    return JSONResponse(
        status_code=500, content={"message": "---Unexpected connection error---"}
    )


upload_user_picture(app, lock)
