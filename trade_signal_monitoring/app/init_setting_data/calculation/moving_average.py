import pandas as pd
from datetime import datetime, timezone
from log_generator import set_logger
from utils import convert_numpy_types

logger = set_logger()


def moving_average(candles, type):
    """
    pandas를 활용해 여러 기간의 이동평균선을 계산하는 함수

    Args:
        candles (list): API에서 받아온 캔들 데이터 리스트
        type (str): 캔들 타입 (day, week, hour4, hour1)

    Returns:
        dict: 여러 기간의 이동평균 결과와 메타데이터를 포함한 딕셔너리
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
            "long_term": 90,  # 약 3개월로 조정
            "macd_long": 26,
            "macd_short": 12,
            "signal": 9,
        },
        "hour1": {
            "long_term": 84,  # 약 3.5일로 조정
            "macd_long": 26,
            "macd_short": 12,
            "signal": 9,
        },
    }

    # 모든 계산할 기간 추출
    all_periods = set()
    """
    {100, 7, 200, 9, 12, 50, 25, 26}
    """
    type_periods = periods.get(type, {})
    """
    {'long_term': 200, 'macd_long': 26, 'macd_short': 12, 'signal': 9, 'add_periods': [7, 25, 50, 100]}
    """
    for key, value in type_periods.items():
        if isinstance(value, list):
            all_periods.update(value)
        else:
            all_periods.add(value)

    # 결과 초기화
    result = {
        "type": type,
        "ma_values": {},
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }

    # 캔들 데이터를 pandas DataFrame으로 변환
    df = pd.DataFrame(candles)

    # 시간순으로 정렬 (과거 → 현재)
    df = df.sort_values("candle_date_time_utc")

    # 모든 기간에 대해 이동평균 계산
    for period in sorted(all_periods):
        # pandas의 rolling 함수로 이동평균 계산
        df[f"ma_{period}"] = df["trade_price"].rolling(window=period).mean().round(2)

        # 결과를 딕셔너리 리스트로 변환
        ma_values = []
        for _, row in df[df[f"ma_{period}"].notna()].iterrows():
            ma_values.append(
                {
                    "timestamp": row["candle_date_time_utc"],
                    "value": row[f"ma_{period}"],
                    "price": row["trade_price"],
                }
            )

        # 결과 저장
        result["ma_values"][f"ma_{period}"] = ma_values

    # 메타데이터 추가
    result["macd_short_period"] = type_periods.get("macd_short")
    result["macd_long_period"] = type_periods.get("macd_long")
    result["signal_period"] = type_periods.get("signal")

    # 최신 데이터의 이동평균 값들 (호환성 유지)
    for period in sorted(all_periods):
        ma_key = f"ma_{period}"
        if not df.empty and pd.notna(df.iloc[-1].get(ma_key, None)):
            result[ma_key] = df.iloc[-1][ma_key]

    # 기존 호환성을 위해 장기 이동평균도 ma 키에 저장
    long_term_key = f"ma_{type_periods.get('long_term')}"
    if long_term_key in result:
        result["ma"] = result[long_term_key]

    result = convert_numpy_types(result)

    logger.info(f"이동평균선 계산 완료. type: {type}")

    return result
