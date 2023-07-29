# api_destination_handler.py

import requests
import time
from api_app_config import destination_url, sync_max_retries
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

    try:
        response_E = requests.post(destination_url, json=data, timeout=20)
        logger.info(f"Response from destination API: {response_E.status_code} {response_E.json()} id: {id_value}")
        response_E.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed request to destination API: {e}")
    
    # for attempt in range(sync_max_retries):
    #     try:
    #         response_E = requests.post(destination_url, json=data, timeout=20)
    #         logger.info(f"Response from destination API: {response_E.status_code} {response_E.json()} id: {id_value}")
    #         response_E.raise_for_status()
    #         break
    #     except requests.RequestException as e:
    #         logger.error(f"Failed request to destination API on attempt {attempt+1}: {e}")
    #         if attempt < sync_max_retries - 1:
    #             time.sleep(5) 
    #         else:
    #             logger.error("All attempts failed.")
    #             raise
