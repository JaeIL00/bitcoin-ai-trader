import sys
from log_generator import set_logger, handle_exception
from realtime_trade.monitoring import get_trade_ws
from history_data_setting.load_candle_data import (
    get_day_candle,
    get_week_candle,
    get_hour_4_candle,
    get_hour_1_candle,
)
import websockets
import asyncio
import json
from datetime import datetime
import requests
import multiprocessing

if __name__ == "__main__":
    logger = set_logger()
    sys.excepthook = handle_exception

    # get_trade_ws()

    candle_day_p = multiprocessing.Process(target=get_day_candle)
    candle_week_p = multiprocessing.Process(target=get_week_candle)
    candle_hour_4_p = multiprocessing.Process(target=get_hour_4_candle)
    candle_hour_1_p = multiprocessing.Process(target=get_hour_1_candle)
    candle_day_p.start()
    candle_week_p.start()
    candle_hour_4_p.start()
    candle_hour_1_p.start()
