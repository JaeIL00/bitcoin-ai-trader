import sys
from log_generator import set_logger, handle_exception
from realtime_trade.monitoring import get_trade_ws
from history_data_setting.load_candle_data import get_candle_process
import websockets


if __name__ == "__main__":
    logger = set_logger()
    sys.excepthook = handle_exception
    get_candle_process()
    # get_trade_ws()
