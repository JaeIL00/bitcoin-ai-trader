import multiprocessing

from .calculation.rsi import rsi
from .calculation.macd import macd
from .calculation.moving_average import moving_average
from log_generator import set_logger
from api.api import (
    get_candle_api_call,
    create_macd,
    create_moving_average,
    create_rsi,
)

logger = set_logger()

day_url = "https://api.upbit.com/v1/candles/days"
week_url = "https://api.upbit.com/v1/candles/weeks"
hour_4_url = "https://api.upbit.com/v1/candles/minutes/240"
hour_1_url = "https://api.upbit.com/v1/candles/minutes/60"


def get_day_candle():
    logger.info("일봉 캔들 조회 시작")
    type = "day"
    candles = get_candle_api_call(url=day_url, count=200)
    if candles is None:
        return
    moving_average_result = moving_average(candles=candles, type=type)
    create_moving_average(moving_average_result)
    macd_result = macd(moving_average_result["ma_values"])
    macd_result["type"] = type
    create_macd(macd_result)

    rsi_result = rsi(candles, type)
    create_rsi(rsi_result)


def get_week_candle():
    logger.info("주봉 캔들 조회 시작")
    type = "week"
    candles = get_candle_api_call(url=week_url, count=52)
    if candles is None:
        return
    moving_average_result = moving_average(candles=candles, type=type)
    create_moving_average(moving_average_result)
    macd_result = macd(moving_average_result["ma_values"])
    macd_result["type"] = type
    create_macd(macd_result)

    rsi_result = rsi(candles, type)
    create_rsi(rsi_result)


def get_hour_4_candle():
    logger.info("4시간봉 캔들 조회 시작")
    type = "hour4"
    candles = get_candle_api_call(url=hour_4_url, count=180)  # 30일치
    if candles is None:
        return
    moving_average_result = moving_average(candles=candles, type=type)
    create_moving_average(moving_average_result)
    macd_result = macd(moving_average_result["ma_values"])
    macd_result["type"] = type
    create_macd(macd_result)

    rsi_result = rsi(candles, type)
    create_rsi(rsi_result)


def get_hour_1_candle():
    logger.info("1시간봉 캔들 조회 시작")
    type = "hour1"
    candles = get_candle_api_call(url=hour_1_url, count=168)  # 7일치
    if candles is None:
        return
    moving_average_result = moving_average(candles=candles, type=type)
    create_moving_average(moving_average_result)
    macd_result = macd(moving_average_result["ma_values"])
    macd_result["type"] = type
    create_macd(macd_result)

    rsi_result = rsi(candles, type)
    create_rsi(rsi_result)


def start_get_candle_process():
    candle_day_p = multiprocessing.Process(target=get_day_candle)
    candle_week_p = multiprocessing.Process(target=get_week_candle)
    candle_hour_4_p = multiprocessing.Process(target=get_hour_4_candle)
    candle_hour_1_p = multiprocessing.Process(target=get_hour_1_candle)
    candle_day_p.start()
    candle_week_p.start()
    candle_hour_4_p.start()
    candle_hour_1_p.start()

    candle_day_p.join()
    candle_week_p.join()
    candle_hour_4_p.join()
    candle_hour_1_p.join()


# if __name__ == "__main__":
#     get_day_candle()
