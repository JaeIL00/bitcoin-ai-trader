import sys
from log_generator import set_logger, handle_exception
from realtime_trade.monitoring import get_trade_ws
import websockets
import asyncio
import json
from datetime import datetime
import requests

if __name__ == "__main__":
    logger = set_logger()
    sys.excepthook = handle_exception

    # try:
    #     now = datetime.now()
    #     formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")

    #     url = "https://api.upbit.com/v1/candles/minutes/1"
    #     params = {"market": "KRW-BTC", "count": 1, "to": formatted_date}
    #     headers = {"accept": "application/json"}

    #     response = requests.get(url, params=params, headers=headers)
    #     """
    #     {
    #         "market":"KRW-BTC",
    #         "candle_date_time_utc":"2025-02-26T12:10:00",
    #         "candle_date_time_kst":"2025-02-26T21:10:00", 캔들 기준 시각(KST 기준)
    #         "opening_price":128500000.00000000, 시가
    #         "high_price":128500000.00000000, 고가
    #         "low_price":128436000.00000000, 저가
    #         "trade_price":128436000.00000000, 종가
    #         "timestamp":1740571808225,
    #         "candle_acc_trade_price":5003068.03009000, 누적 거래 금액
    #         "candle_acc_trade_volume":0.03894042, 누적 거래량
    #         "unit":1
    #     }
    #     """
    #     print(response.text)
    # except Exception as e:
    #     print(e)

    get_trade_ws()
