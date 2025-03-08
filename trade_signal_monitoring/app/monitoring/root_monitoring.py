from init_setting_data.init_data import start_get_candle_process
from .candle_monitoring import start_candle_monitoring
from log_generator import set_logger

logger = set_logger()


def init_data():
    start_get_candle_process()


def start_update_monitoring():
    init_data()
    start_candle_monitoring()
