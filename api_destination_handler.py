# api_destination_handler.py

import requests
import logging
from api_app_config import destination_url

logger = logging.getLogger(__name__)

async def send_to_destination(id_value, download_url):
    # Prepare data for the final destination
    data = {
        'url': download_url,  # URL encode is not needed here as requests.post will handle this
        'id': id_value,
    }
    logger.info(f"Sending data to destination API: {data}")
    # Send the file and id to the final destination (point E)
    try:
        response_E = requests.post(destination_url, json=data, timeout=20)
        response_E.raise_for_status()  # Raise an exception if the response contains a HTTP error status code
    except requests.RequestException as e:
        logger.error(f"Failed request to destination API: {e}")
