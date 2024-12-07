import logging
from logging.handlers import TimedRotatingFileHandler
import os
import datetime

log_dir = "logs"

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger = logging.getLogger(__name__)
format = '[%(asctime)s] [%(levelname)s] %(message)s'
formatter = logging.Formatter(format, datefmt='%Y-%m-%d %H:%M:%S')
logging.basicConfig(format=format, level=logging.INFO)
logger.propagate = False

info_filename = (
    "info_"
    + datetime.datetime.now().strftime('%Y-%m-%d')
    + ".log"
)
log_filename_format = os.path.join(log_dir, info_filename)

info_handler = TimedRotatingFileHandler(log_filename_format, when="midnight", interval=1)
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(formatter)
logger.addHandler(info_handler)

error_filename = (
    "error_"
    + datetime.datetime.now().strftime('%Y-%m-%d')
    + ".log"
)
error_filename_format = os.path.join(log_dir, error_filename)
error_handler = TimedRotatingFileHandler(error_filename_format, when="midnight", interval=1)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)
logger.addHandler(error_handler)

# logger.info("")
# logger.error("")
