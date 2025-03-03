import pandas as pd
from log_generator import set_logger

logger = set_logger()


def rsi(candles, type):
    """
    전체 캔들 데이터에 대해 RSI를 계산 (NaN 값 제거)
    """
    period = 14
    price_col = "trade_price"

    # 데이터프레임 변환 및 정렬
    candles_df = pd.DataFrame(candles)
    candles_df = candles_df.sort_values("candle_date_time_kst")

    # RSI 계산
    delta = candles_df[price_col].diff()
    gains = delta.copy()
    declines = delta.copy()
    gains[gains < 0] = 0
    declines[declines > 0] = 0

    gain = gains.ewm(com=(period - 1), min_periods=period).mean()
    loss = declines.abs().ewm(com=(period - 1), min_periods=period).mean()

    RS = gain / loss
    rsi_series = pd.Series(100 - (100 / (1 + RS)), name="RSI")

    # nan 값 위치 저장
    valid_indices = rsi_series.notna()

    # 유효한 RSI 값과 해당하는 타임스탬프만 추출
    valid_rsi = rsi_series[valid_indices].tolist()
    valid_timestamps = candles_df["candle_date_time_utc"][valid_indices].tolist()

    if len(valid_rsi) == 0:
        return None  # 충분한 데이터가 없음

    logger.info(f"RSI 계산 완료. type: {type}")
    # 반환 형식 (NaN 없는 값만 포함)
    return {
        "type": type,
        "rsi_values": valid_rsi,  # NaN이 제거된 RSI 값들
        "timestamps": valid_timestamps,  # 해당하는 타임스탬프 (길이 동일)
        "current_rsi": float(valid_rsi[-1]),  # 현재 RSI
        "last_updated": valid_timestamps[-1],  # 마지막 업데이트 시간
    }
