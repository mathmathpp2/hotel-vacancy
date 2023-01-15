import logging
import os

level = logging.getLevelName(os.environ.get("LOG_LEVEL", "INFO"))

logging.basicConfig(
    level=level,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
logger.setLevel(level)
