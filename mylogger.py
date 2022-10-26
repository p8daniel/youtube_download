import logging
import sys

logger = logging.getLogger("mylogger")
logger.setLevel(logging.DEBUG)


my_handler = logging.StreamHandler(sys.stdout)
my_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(message)s", "%Y-%m-%d %H:%M:%S")
my_handler.setFormatter(formatter)
logger.addHandler(my_handler)