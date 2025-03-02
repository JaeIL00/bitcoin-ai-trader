from datetime import datetime, timezone

from log_generator import set_logger

logger = set_logger()

# 초기 셋업 이후 이동평균선 업데이트 할때 필요한 함수
# def update_daily_ma(candles, current_ma_info):
#     """
#     일일 이동평균선을 업데이트하는 함수

#     Args:
#         candles (list): 최신 날짜순으로 정렬된 200개의 일봉 캔들 데이터
#         current_ma_info (dict): 현재 MA 정보 {'type': 'day', 'oldest_price': 가격, 'ma': MA값}

#     Returns:
#         dict: 업데이트된 MA 정보
#     """
#     # 캔들이 충분한지 확인
#     if len(candles) < 200:
#         print(f"경고: 캔들 데이터가 부족합니다. (현재: {len(candles)}, 필요: 200)")
#         return current_ma_info

#     # 캔들을 날짜순으로 정렬 (오래된 순 → 최신 순)
#     # API 응답이 최신 순으로 되어 있다면 뒤집어줍니다
#     sorted_candles = sorted(candles, key=lambda x: x['candle_date_time_utc'])

#     # 가장 최근 캔들(인덱스 -1)의 종가
#     newest_price = sorted_candles[-1]['trade_price']

#     # 이전 MA 값과 oldest_price 가져오기
#     previous_ma = current_ma_info['ma']
#     oldest_price = current_ma_info['oldest_price']

#     # 증분 계산으로 새 MA 계산 (period는 day 타입이면 200으로 고정)
#     new_ma = previous_ma + (newest_price - oldest_price) / 200

#     # 다음에 제거될 가격 업데이트 (지금 199번째 데이터가 다음에 oldest가 됨)
#     next_oldest_price = sorted_candles[1]['trade_price']  # 인덱스 0이 현재 oldest이므로 1이 다음 oldest

#     # 업데이트된 MA 정보 반환
#     updated_ma_info = {
#         'type': 'day',
#         'oldest_price': next_oldest_price,
#         'ma': new_ma
#     }


def calculate_moving_average(candles, period):
    """
    캔들 데이터를 이용해 이동평균선을 계산하는 함수

    Args:
        candles (list): API에서 받아온 캔들 데이터 리스트 (최신 데이터가 앞에 있는 형태)
        period (int): 이동평균 기간

    Returns:
        dict: 원본 캔들 데이터에 ma_{period} 필드가 추가된 결과
    """

    # 캔들 기준 시각(UTC 기준) 포맷: yyyy-MM-dd'T'HH:mm:ss
    CANDLE_DATETIME_UTC = "candle_date_time_utc"

    type = None

    if period == 200:
        type = "day"
    if period == 52:
        type = "week"
    if period == 180:
        type = "hour4"
    if period == 168:
        type = "hour1"

    result = {"type": type}

    # 캔들 데이터 역순 정렬 (과거→현재 순서로 변경)
    candles_chronological = sorted(candles, key=lambda x: x[CANDLE_DATETIME_UTC])

    # 이동평균 계산
    for i in range(len(candles_chronological)):
        if i == 0:
            result["oldest_price"] = candles_chronological[0]["trade_price"]

        # 이동평균 계산에 필요한 데이터가 충분한지 확인
        if i >= period - 1:
            # 지정한 기간 동안의 가격 합계 계산
            price_sum = sum(
                candles_chronological[j]["trade_price"]
                for j in range(i - period + 1, i + 1)
            )
            # 이동평균 계산
            ma_200 = round(price_sum / period, 2)

            """
                200일 동안의 비트코인 종가 평균
                단기 가격 변동(노이즈)을 걸러내고 장기적인 추세를 파악하는 데 도움을 줍니다.
                - 가격 > 이동평균선: 상승 추세 가능성 ↗️
                - 가격 < 이동평균선: 하락 추세 가능성 ↘️
                가격이 떨어질 때 이동평균선이 지지대 역할을 하거나,
                상승할 때 저항대 역할을 하는 경우가 많습니다.
            """
            result["ma"] = ma_200
            result["last_updated"] = datetime.now(timezone.utc).isoformat()

    logger.info(f"이동평균선 계산 완료. type: {type}")
    """
    {
        'type': 'hour4', 
        'oldest_price': 155800000.0, 
        'ma': 146933033.33, 
        'last_updated': '2025-03-02T14:05:57.681533+00:00'
    }
    """
    return result
