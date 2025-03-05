from datetime import datetime
import pandas as pd
from log_generator import set_logger

logger = set_logger()


def macd(ma_values_data):
    """
    DB에 저장된 이동평균 데이터를 활용해 MACD를 계산하는 함수

    Args:
        ma_values_data (dict): 'ma_values' JSON 필드에서 가져온 이동평균 데이터
                               예: {'ma_12': [{timestamp, value, price}, ...], 'ma_26': [...]}

    Returns:
        dict: MACD 계산 결과 (macd_line, signal_line, histogram, dates)
    """

    # short_period (int): 단기 이동평균 기간 (기본값: 12)
    short_period = 12

    # long_period (int): 장기 이동평균 기간 (기본값: 26)
    long_period = 26

    # signal_period (int): 시그널 라인 계산 기간 (기본값: 9)
    signal_period = 9

    # 필요한 MA 키 지정
    short_key = f"ma_{short_period}"
    long_key = f"ma_{long_period}"

    # 필요한 데이터가 있는지 확인
    if short_key not in ma_values_data or long_key not in ma_values_data:
        raise ValueError(f"필요한 이동평균을 찾을 수 없습니다: {short_key}, {long_key}")

    # 데이터프레임 생성
    short_df = pd.DataFrame(ma_values_data[short_key])
    long_df = pd.DataFrame(ma_values_data[long_key])

    # 타임스탬프로 정렬
    short_df["timestamp"] = pd.to_datetime(short_df["timestamp"])
    long_df["timestamp"] = pd.to_datetime(long_df["timestamp"])
    short_df = short_df.sort_values("timestamp")
    long_df = long_df.sort_values("timestamp")

    # 공통 날짜만 유지하기 위해 데이터프레임 조인
    merged_df = pd.merge(
        short_df[["timestamp", "value"]],
        long_df[["timestamp", "value"]],
        on="timestamp",
        suffixes=("_short", "_long"),
    )

    # MACD 라인 계산 (단기 - 장기)
    merged_df["macd"] = merged_df["value_short"] - merged_df["value_long"]

    # 시그널 라인 계산 (MACD의 EMA)
    merged_df["signal"] = merged_df["macd"].ewm(span=signal_period, adjust=False).mean()

    # 히스토그램 계산
    merged_df["histogram"] = merged_df["macd"] - merged_df["signal"]

    str_dates = merged_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist()
    datetime_dates = [datetime.strptime(d, "%Y-%m-%d %H:%M:%S") for d in str_dates]

    iso_dates = [dt.isoformat() for dt in datetime_dates]

    # 결과 반환
    result = {
        "dates": iso_dates,
        "macd_line": merged_df["macd"].tolist(),
        "signal_line": merged_df["signal"].tolist(),
        "histogram": merged_df["histogram"].tolist(),
    }

    logger.info(f"MACD 계산 완료.")

    return result
