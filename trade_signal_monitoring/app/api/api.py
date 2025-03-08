import requests
from datetime import datetime

from log_generator import set_logger

logger = set_logger()


def get_moving_average(type):
    try:
        response = requests.get(f"http://backend:8000/api/moving-averages/{type}")

        response.raise_for_status()
        logger.info(f"이동평균선 조회 완료")
        return response.json()
    except Exception as e:
        logger.error(f"이동평균선 조회 실패: {e}")
        return None


def create_moving_average(body):
    try:
        response = requests.post(
            "http://backend:8000/api/moving-averages",
            json=body,
        )

        response.raise_for_status()
        logger.info(f"이동평균선 생성 완료")
    except Exception as e:
        logger.error(f"이동평균선 생성 실패: {e}")
        logger.error(body)


def put_moving_average(type, body):
    try:
        response = requests.put(
            f"http://backend:8000/api/moving-averages/{type}",
            json=body,
        )

        response.raise_for_status()
        logger.info(f"이동평균선 수정 완료")
    except Exception as e:
        logger.error(f"이동평균선 수정 실패: {e}")
        logger.error(body)


def create_rsi(body):
    try:
        response = requests.post(
            "http://backend:8000/api/rsi",
            json=body,
        )

        response.raise_for_status()
        logger.info(f"과거 RSI 인서트 완료")
    except Exception as e:
        logger.error(f"과거 RSI 인서트 실패: {e}")
        logger.error(body)


def create_macd(body):
    try:
        response = requests.post(
            "http://backend:8000/api/macd",
            json=body,
        )

        response.raise_for_status()
        logger.info(f"과거 MACD 인서트 완료")
    except Exception as e:
        logger.error(f"과거 MACD 인서트 실패: {e}")
        logger.error(body)


def get_candle_api_call(url, count):
    try:
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")

        params = {"market": "KRW-BTC", "count": count, "to": formatted_date}
        headers = {"accept": "application/json"}

        response = requests.get(url, params=params, headers=headers)

        response.raise_for_status()

        return response.json()
    except Exception as e:
        logger.error(f"캔들 조회 api({url}) 실패: {e}")
        return None
