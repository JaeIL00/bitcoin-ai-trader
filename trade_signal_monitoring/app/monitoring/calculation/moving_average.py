from datetime import datetime, timezone


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
        },
        "week": {
            "long_term": 52,
            "macd_long": 26,
            "macd_short": 12,
            "signal": 9,
        },
        "hour4": {
            "long_term": 90,
            "macd_long": 26,
            "macd_short": 12,
            "signal": 9,
        },
        "hour1": {
            "long_term": 84,
            "macd_long": 26,
            "macd_short": 12,
            "signal": 9,
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
