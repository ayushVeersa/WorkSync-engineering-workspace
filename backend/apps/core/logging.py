import logging
import sys
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
)

formatter = logging.Formatter(LOG_FORMAT)

# Console handler
# console_handler = logging.StreamHandler(sys.stdout)
# console_handler.setFormatter(formatter)

# File handler
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(formatter)

# Root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Avoid duplicate handlers if this module is reloaded
if not logger.handlers:
    # logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Return a module-level logger named after the calling module.

    This ensures consistent formatting and that all child loggers
    propagate to the configured root logging handler.
    """
    return logging.getLogger(name)
