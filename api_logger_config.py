# api_logger_config.py

import datetime
import logging
import os

from api_app_config import log_folder


def get_logger(name):
    # Get today's date as yyyy-mm-dd and construct the log file name
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_folder, current_date + ".txt")

    # Check if the directory exists, if not, create it
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # If the logger has handlers, check if the current handler's log file is for today's date
    if logger.handlers:
        current_handler = logger.handlers[0]
        if not current_handler.baseFilename.startswith(log_file):
            # If the log file is not for today's date, remove the current handler
            logger.removeHandler(current_handler)
            # Also remove the console handler
            logger.removeHandler(logger.handlers[0])
        else:
            # If the log file is for today's date, return the existing logger
            return logger

    # Create a file handler that logs even debug messages
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.INFO)

    # Create a console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Create a logging format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(handler)
    logger.addHandler(ch)

    return logger
