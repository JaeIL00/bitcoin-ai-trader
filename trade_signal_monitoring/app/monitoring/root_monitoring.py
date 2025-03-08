from datetime import datetime
import time

from init_setting_data.init_data import start_get_candle_process
from api.api import get_candle_api_call, get_moving_average, put_moving_average
from .ma_monitoring import start_moving_average_update_monitoring
from .calculation.moving_average import update_moving_average
from log_generator import set_logger

logger = set_logger()


def init_data():
    start_get_candle_process()


def start_update_monitoring():
    init_data()
    start_moving_average_update_monitoring()
