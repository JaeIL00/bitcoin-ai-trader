import sys
from log_generator import set_logger, handle_exception
from monitoring.root_monitoring import start_update_monitoring


if __name__ == "__main__":
    logger = set_logger()
    sys.excepthook = handle_exception

    start_update_monitoring()
