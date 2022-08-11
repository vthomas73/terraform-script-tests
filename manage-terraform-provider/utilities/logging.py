import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
FORMAT = '%(levelname)s: %(asctime)s -  l.%(lineno)d - %(message)s' if LOG_LEVEL.upper() == "DEBUG" else '%(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT, level=LOG_LEVEL)

def get_logger(name):
    return logging.getLogger(name)