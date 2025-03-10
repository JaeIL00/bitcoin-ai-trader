from datetime import datetime, timezone
from log_generator import set_logger
from api.api import get_moving_average

logger = set_logger()


def update_moving_average(prev_ma_data, new_candle, type):
    """
    기존 이동평균 데이터에 새로운 캔들 하나를 추가하여 이동평균 계산을 업데이트하는 함수

    Args:
        prev_ma_data (Dict): 이전에 저장된 이동평균 데이터
        new_candle (Dict): API에서 새로 받아온 캔들 데이터 하나
        type (str): 캔들 타입 (day, week, hour4, hour1), 기본값 'hour1'

    Returns:
        Dict: 업데이트된 이동평균 결과와 메타데이터를 포함한 딕셔너리
    """
    # 타임프레임별 기본 이동평균 기간 설정
    periods = {
        "day": {
            "long_term": 200,
            "macd_long": 26,
            "macd_short": 12,
            "signal": 9,
            "add_periods": [7, 25, 50, 100],
        },
        "week": {
            "long_term": 52,
            "macd_long": 26,
            "macd_short": 12,
            "signal": 9,
            "add_periods": [7, 25, 50],
        },
        "hour4": {
            "long_term": 90,  # 약 3개월로 조정
            "macd_long": 26,
            "macd_short": 12,
            "signal": 9,
            "add_periods": [7, 25, 50],
        },
        "hour1": {
            "long_term": 84,  # 약 3.5일로 조정
            "macd_long": 26,
            "macd_short": 12,
            "signal": 9,
            "add_periods": [3, 7, 25],
        },
    }

    # 결과 초기화 (기존 데이터 복사)
    result = prev_ma_data.copy()
    result["last_updated"] = datetime.now(timezone.utc).isoformat()

    # 모든 계산할 기간 추출
    all_periods = set()
    type_periods = periods.get(type, {})
    for key, value in type_periods.items():
        if isinstance(value, list):
            all_periods.update(value)
        else:
            all_periods.add(value)

    # 새 캔들 데이터
    new_timestamp = new_candle["candle_date_time_utc"]
    new_price = new_candle["trade_price"]

    # 각 이동평균 기간에 대해 업데이트
    for period in sorted(all_periods):
        ma_key = f"ma_{period}"

        # 해당 기간의 이동평균 값 목록 가져오기
        ma_values = result["ma_values"].get(ma_key, [])

        # 충분한 데이터가 있으면 이동평균 업데이트
        # 가장 오래된 데이터 제외하고 새 데이터 추가하는 방식으로 계산

        # 이전 period 개의 가격 데이터 수집 (맨 뒤 period-1개 + 새 데이터)
        prices = [item["price"] for item in ma_values[-(period - 1) :]]
        prices.append(new_price)

        # 새 이동평균 계산
        new_ma_value = round(sum(prices) / period, 2)

        # 새 이동평균 값 추가
        ma_values.append(
            {"timestamp": new_timestamp, "value": new_ma_value, "price": new_price}
        )

        # 최신 MA 값 업데이트
        result[ma_key] = new_ma_value

        # 결과 업데이트
        result["ma_values"][ma_key] = ma_values

    # 기존 호환성을 위해 장기 이동평균도 ma 키에 저장
    long_term_key = f"ma_{type_periods.get('long_term')}"
    if long_term_key in result:
        result["ma"] = result[long_term_key]

    result.pop("id", None)
    result.pop("created_at", None)

    return result


def calculate_trend_strength(current_price):
    """
    여러 이동평균선을 활용한 추세 강도 측정

    Args:
        current_price: 현재 가격
        ma_data: 이동평균 데이터

    Returns:
        dict: 추세 강도 분석 결과와 점수
    """
    # 필요한 이동평균선 데이터 추출
    hour4_ma = get_moving_average("hour4")
    ma_7 = hour4_ma["ma_7"]
    ma_25 = hour4_ma["ma_25"]
    ma_50 = hour4_ma["ma_50"]
    ma_90 = hour4_ma["ma_90"]

    # 결과 저장용 딕셔너리
    result = {
        "score": 0,  # 최종 점수
        "ma_alignment": None,  # 이동평균선 정렬 상태
        "price_relation": None,  # 가격과 이평선 관계
        "details": {},  # 세부 정보
    }

    # 1. 이동평균선 정렬 상태 확인 (최대 3점)
    alignment_score = 0
    if ma_7 > ma_25 > ma_50 > ma_90:
        alignment_score = 3
        result["ma_alignment"] = "매우_강한_상승"
    elif ma_7 > ma_25 > ma_50:
        alignment_score = 2
        result["ma_alignment"] = "강한_상승"
    elif ma_7 > ma_25:
        alignment_score = 1
        result["ma_alignment"] = "약한_상승"
    elif ma_7 < ma_25 < ma_50 < ma_90:
        alignment_score = -3
        result["ma_alignment"] = "매우_강한_하락"
    elif ma_7 < ma_25 < ma_50:
        alignment_score = -2
        result["ma_alignment"] = "강한_하락"
    elif ma_7 < ma_25:
        alignment_score = -1
        result["ma_alignment"] = "약한_하락"
    else:
        alignment_score = 0
        result["ma_alignment"] = "혼합_또는_횡보"

    # 2. 현재가와 이동평균선 관계 확인 (최대 2점)
    price_score = 0
    above_count = sum(
        [
            1 if current_price > ma_7 else 0,
            1 if current_price > ma_25 else 0,
            1 if current_price > ma_50 else 0,
            1 if current_price > ma_90 else 0,
        ]
    )

    if above_count == 4:
        price_score = 2
        result["price_relation"] = "모든_이평선_위"
    elif above_count == 3:
        price_score = 1
        result["price_relation"] = "대부분_이평선_위"
    elif above_count == 1:
        price_score = -1
        result["price_relation"] = "대부분_이평선_아래"
    elif above_count == 0:
        price_score = -2
        result["price_relation"] = "모든_이평선_아래"
    else:
        price_score = 0
        result["price_relation"] = "혼합"

    # 3. 이격도 분석 (최대 1점)
    # 이격도 = (현재가 - 이동평균선) / 이동평균선 * 100
    deviation_score = 0
    deviation_25 = 0
    if ma_25 and ma_25 != 0:  # None이 아니고 0이 아닌 경우만
        deviation_25 = (current_price - ma_25) / ma_25 * 100

    if deviation_25 > 5:
        deviation_score = 1
        result["details"]["deviation"] = "크게_이격됨_상승"
    elif deviation_25 < -5:
        deviation_score = -1
        result["details"]["deviation"] = "크게_이격됨_하락"
    else:
        result["details"]["deviation"] = "적정_이격도"

    # 최종 점수 계산 (가중치 적용)
    score = (alignment_score * 1.5) + (price_score * 1.0) + (deviation_score * 0.5)

    # 추세 강도 판정
    if score >= 5:
        result["strength"] = "매우_강한_상승추세"
    elif score >= 3:
        result["strength"] = "강한_상승추세"
    elif score >= 1:
        result["strength"] = "약한_상승추세"
    elif score > -1:
        result["strength"] = "중립_또는_횡보"
    elif score >= -3:
        result["strength"] = "약한_하락추세"
    elif score >= -5:
        result["strength"] = "강한_하락추세"
    else:
        result["strength"] = "매우_강한_하락추세"

    logger.info("ts============")
    logger.info(result["ma_alignment"])
    logger.info(result["price_relation"])
    logger.info(result["details"]["deviation"])
    logger.info(result["strength"])

    return score


def analyze_multi_timeframes(current_price):
    hour4_ma = get_moving_average("hour4")
    hour1_ma = get_moving_average("hour1")
    day_ma = get_moving_average("day")

    signals = {
        "hour1": {
            "above_ma": current_price > hour1_ma["ma_25"],
            "deviation": round(
                (current_price - hour1_ma["ma_25"]) / hour1_ma["ma_25"] * 100,
                2,
            ),
        },
        "hour4": {
            "above_ma": current_price > hour4_ma["ma_25"],
            "deviation": round(
                (current_price - hour4_ma["ma_25"]) / hour4_ma["ma_25"] * 100,
                2,
            ),
        },
        "day": {
            "above_ma": current_price > day_ma["ma_25"],
            "deviation": round(
                (current_price - day_ma["ma_25"]) / day_ma["ma_25"] * 100,
                2,
            ),
        },
    }

    bullish_count = sum(1 for tf in signals.values() if tf["above_ma"])
    bearish_count = sum(1 for tf in signals.values() if not tf["above_ma"])
    alignment_score = bullish_count - bearish_count

    # -3 ~ 3 범위
    # alignment_score

    return alignment_score * 1.5  # 가중치 적용 (예: 1.5배)


def ma_25_calc(current_price):
    ma = get_moving_average("hour4")
    ma_25 = ma["ma_25"]

    price_above_ma = current_price > ma_25
    deviation_pct = round((current_price - ma_25) / ma_25 * 100, 2)

    if price_above_ma and deviation_pct > 1.5:
        action = "강한_매수_신호"
    elif price_above_ma and deviation_pct <= 1.5:
        action = "약한_매수_신호"
    elif not price_above_ma and deviation_pct > -1.5:
        action = "약한_매도_신호"
    elif not price_above_ma and deviation_pct <= -1.5:
        action = "강한_매도_신호"
    else:
        action = "관망"

    trend = "상승세" if price_above_ma else "하락세"

    # 기본 위/아래 여부 확인
    if price_above_ma:
        score = 2  # 기본 점수

        # 이격도에 따른 추가 점수
        deviation = deviation_pct
        if deviation > 3:
            score += 0.5  # 크게 이격된 경우 추가 점수

        # 추세 전환 감지 (신규 상승 전환)
        if action == "강한_매수_신호":
            score += 1.5  # 신규 전환 신호는 가중치 부여
    else:
        score = -2  # 기본 점수

        # 이격도에 따른 추가 감점
        deviation = deviation_pct
        if deviation < -3:
            score -= 0.5  # 크게 하락한 경우

        # 추세 전환 감지 (신규 하락 전환)
        if action == "강한_매도_신호":
            score -= 1.5  # 신규 전환 신호는 가중치 부여

    logger.info("ma_25============")
    logger.info(action)
    logger.info(trend)

    return score
