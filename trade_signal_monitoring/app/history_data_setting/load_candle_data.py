import requests
from datetime import datetime
import requests
import multiprocessing

from .calc_ma import calculate_moving_average
from log_generator import set_logger

logger = set_logger()

day_url = "https://api.upbit.com/v1/candles/days"
week_url = "https://api.upbit.com/v1/candles/weeks"
hour_4_url = "https://api.upbit.com/v1/candles/minutes/240"
hour_1_url = "https://api.upbit.com/v1/candles/minutes/60"

now = datetime.now()
formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")


def insert_moving_average(body):
    try:
        response = requests.post(
            "http://backend:8000/api/moving-averages",
            json=body,
        )

        response.raise_for_status()
        logger.info(f"과거 이동평균선 인서트 완료")
        logger.info(body)
    except Exception as e:
        logger.error(f"과거 이동평균선 인서트 실패: {e}")


def get_candle_api_call(url, count):
    try:
        params = {"market": "KRW-BTC", "count": count, "to": formatted_date}
        headers = {"accept": "application/json"}

        response = requests.get(url, params=params, headers=headers)

        response.raise_for_status()

        return calculate_moving_average(candles=response.json(), period=count)
    except Exception as e:
        logger.error(f"캔들 조회 api({url}) 에러: {e}")


def get_day_candle():
    logger.info("일봉 캔들 조회 시작")
    result = get_candle_api_call(url=day_url, count=200)
    insert_moving_average(result)


def get_week_candle():
    logger.info("주봉 캔들 조회 시작")
    result = get_candle_api_call(url=week_url, count=52)
    insert_moving_average(result)


def get_hour_4_candle():
    logger.info("4시간봉 캔들 조회 시작")
    result = get_candle_api_call(url=hour_4_url, count=180)  # 30일치
    insert_moving_average(result)


def get_hour_1_candle():
    logger.info("1시간봉 캔들 조회 시작")
    result = get_candle_api_call(url=hour_1_url, count=168)  # 7일치
    insert_moving_average(result)


def get_candle_process():
    candle_day_p = multiprocessing.Process(target=get_day_candle)
    candle_week_p = multiprocessing.Process(target=get_week_candle)
    candle_hour_4_p = multiprocessing.Process(target=get_hour_4_candle)
    candle_hour_1_p = multiprocessing.Process(target=get_hour_1_candle)
    candle_day_p.start()
    candle_week_p.start()
    candle_hour_4_p.start()
    candle_hour_1_p.start()
