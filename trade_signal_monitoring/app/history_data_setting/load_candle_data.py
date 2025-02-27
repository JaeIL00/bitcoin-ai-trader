import requests
from datetime import datetime
from .calc_ma import calculate_moving_average

from log_generator import set_logger

logger = set_logger()

day_url = "https://api.upbit.com/v1/candles/days"
week_url = "https://api.upbit.com/v1/candles/weeks"
hour_4_url = "https://api.upbit.com/v1/candles/minutes/240"
hour_1_url = "https://api.upbit.com/v1/candles/minutes/60"

now = datetime.now()
formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")


def get_candle_api_call(url, count):
    try:
        params = {"market": "KRW-BTC", "count": count, "to": formatted_date}
        headers = {"accept": "application/json"}

        response = requests.get(url, params=params, headers=headers)

        response.raise_for_status()

        calculate_moving_average(candles=response.json(), period=count)
    except Exception as e:
        logger.error(f"캔들 조회 api({url}) 에러: {e}")


def get_day_candle():
    logger.info("일봉 캔들 조회 시작")
    get_candle_api_call(url=day_url, count=200)


def get_week_candle():
    logger.info("주봉 캔들 조회 시작")
    get_candle_api_call(url=week_url, count=52)


def get_hour_4_candle():
    logger.info("4시간봉 캔들 조회 시작")
    get_candle_api_call(url=hour_4_url, count=180)  # 30일치


def get_hour_1_candle():
    logger.info("1시간봉 캔들 조회 시작")
    get_candle_api_call(url=hour_1_url, count=168)  # 7일치


# if __name__ == "__main__":
#     get_day_candle()
#     get_week_candle()
#     get_hour_4_candle()
#     get_hour_1_candle()
