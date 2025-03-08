import sys
from log_generator import set_logger, handle_exception
from monitoring import monitoring


if __name__ == "__main__":
    logger = set_logger()
    sys.excepthook = handle_exception

    monitoring()
