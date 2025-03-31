import os

UTIL_DIR = os.path.dirname(__file__)
LOGS_DIR = os.path.join(os.path.dirname(UTIL_DIR), "logs")

assert os.path.dirname(UTIL_DIR) == os.path.dirname(
    LOGS_DIR
), "UTIL_DIR and LOGS_DIR must have the same parent directory"