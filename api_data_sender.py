# api_destination_handler.py

import requests
from api_app_config import destination_url
from api_logger_config import get_logger

logger = get_logger(__name__)


async def send_return_data_to_api(id_value, download_url):
    # Prepare data for the final destination
    data = {
        "url": download_url,
        # URL encode is not needed here as requests.post will handle this
        "id": id_value,
    }
    logger.info(f"Sending data to destination API: {data}")
    # Send the file and id to the final destination (point E)
    try:
        response_E = requests.post(destination_url, json=data, timeout=20)
        # Raise an exception if the response contains a HTTP error status code
        response_E.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed request to destination API: {e}")
