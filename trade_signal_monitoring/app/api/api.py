import requests
from datetime import datetime

from log_generator import set_logger

logger = set_logger()


def get_moving_average(type):
    try:
        response = requests.get(f"http://backend:8000/api/moving-averages/{type}")

        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"이동평균선 조회 호출 중 오류 발생: {e}") from e


def get_rsi(type):
    try:
        response = requests.get(f"http://backend:8000/api/rsi/{type}")

        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"RSI 조회 호출 중 오류 발생: {e}") from e


def put_rsi(type, body):
    try:
        response = requests.put(
            f"http://backend:8000/api/rsi/{type}",
            json=body,
        )

        response.raise_for_status()
    except Exception as e:
        logger.error(body)
        raise Exception(f"RSI 수정 호출 중 오류 발생: {e}") from e


def create_moving_average(body):
    try:
        response = requests.post(
            "http://backend:8000/api/moving-averages",
            json=body,
        )

        response.raise_for_status()
    except Exception as e:
        logger.error(body)
        raise Exception(f"이동평균선 생성 호출 중 오류 발생: {e}") from e


def put_moving_average(type, body):
    try:
        response = requests.put(
            f"http://backend:8000/api/moving-averages/{type}",
            json=body,
        )

        response.raise_for_status()
    except Exception as e:
        logger.error(body)
        raise Exception(f"이동평균선 수정 호출 중 오류 발생: {e}") from e


def create_rsi(body):
    try:
        response = requests.post(
            "http://backend:8000/api/rsi",
            json=body,
        )

        response.raise_for_status()
    except Exception as e:
        logger.error(f"RSI 생성 실패: {e}")
        logger.error(body)
        raise Exception(f"RSI 생성 호출 중 오류 발생: {e}") from e


def get_macd(type):
    try:
        response = requests.get(f"http://backend:8000/api/macd/{type}")

        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"macd 조회 호출 중 오류 발생: {e}") from e


def create_macd(body):
    try:
        response = requests.post(
            "http://backend:8000/api/macd",
            json=body,
        )

        response.raise_for_status()
    except Exception as e:
        logger.error(body)
        raise Exception(f"MACD 생성 호출 중 오류 발생: {e}") from e


def put_macd(type, body):
    try:
        response = requests.put(
            f"http://backend:8000/api/macd/{type}",
            json=body,
        )

        response.raise_for_status()
    except Exception as e:
        logger.error(body)
        raise Exception(f"macd 수정 호출 중 오류 발생: {e}") from e


def get_vector_store_similar_ai():
    try:
        # 최근 비트코인 시장에서 긍정적 요소가 부정적 요소보다 더 많습니까?
        prompt = """
            You are a Bitcoin market expert. You must analyze recent Bitcoin news and market trends to evaluate the current situation.System instruction: You MUST search and refer to the stored recent Bitcoin news and market data to answer this question.

            Question: Are there more positive factors than negative ones in the recent Bitcoin market?

            Response requirements:
            1. Answer with EXACTLY ONE of these three words only: YES / NO / NEUTRAL
            2. Do NOT include any other words or sentences
            3. Access the stored market data to inform your answer

            Response format: [YES/NO/NEUTRAL]
        """
        response = requests.post(
            f"http://vector_rag:8000/vector-store/get-similar",
            json={"question": prompt},
        )

        response.raise_for_status()

        return response.json()
    except Exception as e:
        raise Exception(f"AI New Rag 호출 중 오류 발생: {e}") from e


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
        raise Exception(f"업비트 캔들 조회({url}) 호출 중 오류 발생: {e}") from e


def get_trade_price_api_call():
    try:
        params = {"markets": "KRW-BTC"}

        response = requests.get("https://api.upbit.com/v1/ticker", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"업비트 현재가 호출 중 오류 발생: {e}") from e


def get_trade_ticks_api_call(days_ago=0):
    try:
        headers = {"accept": "application/json"}

        response = requests.get(
            f"https://api.upbit.com/v1/trades/ticks?market=KRW-BTC&count=500&days_ago={days_ago}",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"업비트 체결가 호출 중 오류 발생: {e}") from e
