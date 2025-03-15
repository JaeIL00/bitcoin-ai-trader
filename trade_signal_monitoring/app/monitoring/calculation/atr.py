from api.api import get_candle_api_call
from log_generator import set_logger

logger = set_logger()


def get_atr(timeframe, period=14):
    """
    지정된 타임프레임에 대한 ATR(Average True Range) 계산

    Args:
        timeframe (str): 'hour1', 'hour4', 'day', 'week' 등의 타임프레임
        period (int, optional): ATR 계산 기간, 기본값 14

    Returns:
        dict: ATR 관련 데이터를 포함하는 딕셔너리
    """
    # 필요한 캔들 수 = 기간 + 추가 여유
    required_candles = period + 30  # 충분한 데이터 확보

    # 캔들 데이터 가져오기
    try:
        timeframes = {
            "hour1": "https://api.upbit.com/v1/candles/minutes/60",
            "hour4": "https://api.upbit.com/v1/candles/minutes/240",
            "day": "https://api.upbit.com/v1/candles/days",
            "week": "https://api.upbit.com/v1/candles/weeks",
        }

        candles = get_candle_api_call(timeframes[timeframe], count=required_candles)

        if not candles or len(candles) < period + 1:
            logger.warning(f"{timeframe} 타임프레임의 캔들 데이터가 충분하지 않습니다.")
            return {"current_atr": None, "atr_values": [], "timestamps": []}

        # True Range 계산
        true_ranges = []
        timestamps = []

        for i in range(1, len(candles)):
            high = candles[i]["high_price"]
            low = candles[i]["low_price"]
            prev_close = candles[i - 1]["trade_price"]

            # True Range 계산 (3가지 방법 중 최대값)
            tr1 = high - low  # 현재 고가 - 현재 저가
            tr2 = abs(high - prev_close)  # |현재 고가 - 이전 종가|
            tr3 = abs(low - prev_close)  # |현재 저가 - 이전 종가|

            true_range = max(tr1, tr2, tr3)
            true_ranges.append(true_range)

            # 타임스탬프 저장
            if "candle_date_time_utc" in candles[i]:
                timestamps.append(candles[i]["candle_date_time_utc"])
            elif "timestamp" in candles[i]:
                timestamps.append(candles[i]["timestamp"])
            else:
                timestamps.append(None)

        # ATR 계산 (단순 이동평균 방식)
        atr_values = []

        for i in range(len(true_ranges) - period + 1):
            atr = sum(true_ranges[i : i + period]) / period
            atr_values.append(atr)

        # 최신 ATR 값
        current_atr = atr_values[-1] if atr_values else None

        # ATR의 변화 추이 (상승/하락/횡보)
        atr_trend = "stable"
        if len(atr_values) >= 3:
            if atr_values[-1] > atr_values[-2] > atr_values[-3]:
                atr_trend = "rising"  # 변동성 증가 추세
            elif atr_values[-1] < atr_values[-2] < atr_values[-3]:
                atr_trend = "falling"  # 변동성 감소 추세

        result = {
            "current_atr": current_atr,
            "atr_values": atr_values,
            "timestamps": timestamps[period - 1 :] if len(timestamps) >= period else [],
            "atr_trend": atr_trend,
            "period": period,
            "timeframe": timeframe,
            # 변동성 수준 분류 (상대적 변동성)
            "volatility_level": _classify_volatility(
                current_atr, candles[-1]["trade_price"]
            ),
        }

        logger.info(f"{timeframe} ATR({period}) 계산 완료: {current_atr}")
        return result

    except Exception as e:
        logger.error(f"ATR 계산 중 오류 발생: {e}")
        return {
            "current_atr": None,
            "atr_values": [],
            "timestamps": [],
            "error": str(e),
        }


def _classify_volatility(atr_value, current_price):
    """
    ATR 값과 현재 가격을 기반으로 변동성 수준 분류

    Args:
        atr_value: 현재 ATR 값
        current_price: 현재 가격

    Returns:
        str: 변동성 수준 ('low', 'normal', 'high', 'extreme')
    """
    if not atr_value or not current_price:
        return "unknown"

    # ATR 비율 = (ATR / 현재가) * 100
    atr_ratio = (atr_value / current_price) * 100

    if atr_ratio < 1.0:
        return "low"  # 낮은 변동성
    elif atr_ratio < 3.0:
        return "normal"  # 정상 변동성
    elif atr_ratio < 5.0:
        return "high"  # 높은 변동성
    else:
        return "extreme"  # 극단적 변동성
