import logging
import config as config

# Logging
# Setup logging
logger = logging.getLogger("rest_filesd")
logger.setLevel(logging.DEBUG)

# create a file handler
handler = logging.FileHandler(config.LOG_FILE)
handler.setLevel(logging.DEBUG)

# create a logging format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)