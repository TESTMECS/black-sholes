from logging import Logger


import logging
import logging.config
import os
from .constants import LOGS_DIR

LOG_FILE_NAME = "app.log"

LOG_FILE = os.path.join(LOGS_DIR, LOG_FILE_NAME)


def _setup_logging(log_file=LOG_FILE, log_level=logging.DEBUG):
    """
    Sets up logging configuration with both console and file handlers.

    :param log_file: The file to write logs to.
    :param log_level: The logging level (default: DEBUG).
    """
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
            },
            "simple": {"format": "%(levelname)s: %(message)s"},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": log_level,
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": log_file,
                "formatter": "detailed",
                "level": log_level,
            },
        },
        "root": {"handlers": ["console", "file"], "level": log_level},
    }

    logging.config.dictConfig(log_config)


def get_logger(name) -> Logger:
    """
    Get a configured logger instance with the specified name.

    Parameters:
    -----------
    name : str
        The name for the logger instance

    Returns:
    --------
    Logger
        A configured logger instance with both console and file handlers
    """
    _setup_logging()
    return logging.getLogger(name)
