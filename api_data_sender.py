# api_destination_handler.py

import asyncio

import httpx

from api_app_config import destination_url, sync_max_retries
from api_logger_config import get_logger

logger = get_logger(__name__)


async def send_return_data_to_api(id_value, download_url):
    data = {
        "url": download_url,
        "id": id_value,
    }
    logger.info(f"Sending data to destination API: {data}")

    # Number of attempts to try sending the request
    max_attempts = sync_max_retries
    for attempt in range(max_attempts):
        try:
            async with httpx.AsyncClient() as client:
                response_E = await client.post(destination_url, json=data, timeout=5)
                logger.info(
                    f"Response from destination API: {response_E.status_code} {response_E.json()} id: {id_value}"
                )
                response_E.raise_for_status()
                break  # If successful, exit the loop
        except httpx.RequestError as e:
            logger.warning(
                f"Attempt {attempt + 1} failed to send request to destination API: {e}"
            )
            if attempt == max_attempts - 1:  # If it's the last attempt, log as an error
                await asyncio.sleep(5)
                logger.error(
                    f"Failed request to destination API after {max_attempts} attempts: {e}"
                )
