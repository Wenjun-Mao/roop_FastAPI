import datetime
import logging
import os
from logging.handlers import TimedRotatingFileHandler

from api_app_config import log_folder


def get_logger(name):
    # Get today's date as yyyy-mm-dd and construct the log file name
    log_file = os.path.join(
        log_folder, datetime.datetime.now().strftime("%Y-%m-%d") + ".txt"
    )

    # Check if the directory exists, if not, create it
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create a file handler that logs even debug messages and rotates the log file at midnight
    handler = TimedRotatingFileHandler(
        log_file, when="midnight", interval=1, backupCount=10
    )
    handler.suffix = "%Y-%m-%d.txt"  # The suffix sets the filename of the backup files
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
