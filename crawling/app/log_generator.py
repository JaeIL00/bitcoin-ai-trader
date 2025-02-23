import logging
import logging.handlers
from rich.logging import RichHandler
from rich.console import Console

LOG_PATH = "./log.log"
RICH_FORMAT = "[%(filename)s:%(lineno)s] >> %(message)s"
FILE_HANDLER_FORMAT = "%(levelname)s\t[%(filename)s:%(funcName)s:%(lineno)s]\t>> %(message)s"  # asctime 제거


def set_logger() -> logging.Logger:
    console = Console(width=400)
    rich_handler = RichHandler(console=console, rich_tracebacks=True, show_time=False)

    logging.basicConfig(level="NOTSET", format=RICH_FORMAT, handlers=[rich_handler])
    logger = logging.getLogger("rich")

    file_handler = logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(FILE_HANDLER_FORMAT))
    logger.addHandler(file_handler)

    return logger


def handle_exception(exc_type, exc_value, exc_traceback):
    logger = logging.getLogger("rich")
    logger.error("Unexpected exception", exc_info=(exc_type, exc_value, exc_traceback))
