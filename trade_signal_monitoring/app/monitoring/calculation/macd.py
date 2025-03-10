from datetime import datetime, timezone
import pandas as pd
from log_generator import set_logger
from api.api import get_macd

logger = set_logger()


def macd(type, ma_values_data):
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

    last_updated = datetime.now(timezone.utc).isoformat()

    # 결과 반환
    result = {
        "type": type,
        "dates": iso_dates,
        "macd_line": merged_df["macd"].tolist(),
        "signal_line": merged_df["signal"].tolist(),
        "histogram": merged_df["histogram"].tolist(),
        "last_updated": last_updated,
    }

    logger.info(f"MACD 계산 완료.")

    return result


def macd_calc():
    macd_data = get_macd("hour4")
    latest_macd = (
        macd_data["macd_line"][-1]
        if isinstance(macd_data["macd_line"], list)
        else macd_data["macd_line"]
    )
    latest_signal = (
        macd_data["signal_line"][-1]
        if isinstance(macd_data["signal_line"], list)
        else macd_data["signal_line"]
    )
    latest_histogram = (
        macd_data["histogram"][-1]
        if isinstance(macd_data["histogram"], list)
        else macd_data["histogram"]
    )
    if latest_macd > latest_signal:
        trend = "상승"
        cross_type = (
            "골든크로스"
            if latest_macd - latest_signal < latest_histogram * 0.1
            else None
        )
    else:
        trend = "하락"
        cross_type = (
            "데드크로스"
            if latest_signal - latest_macd < abs(latest_histogram * 0.1)
            else None
        )

    # 히스토그램 변화 확인 (추세 강도)
    histogram_trend = "중립"
    if (
        isinstance(macd_data.get("histogram"), list)
        and len(macd_data["histogram"]) >= 3
    ):
        if (
            macd_data["histogram"][-3]
            < macd_data["histogram"][-2]
            < macd_data["histogram"][-1]
        ):
            histogram_trend = "강화"
        else:
            histogram_trend = "약화"

    if trend == "상승":
        score = 1.5  # "상승추세"

        if cross_type == "골든크로스":
            score += 1.5  # 골든크로스

        if histogram_trend == "강화":
            score += 1  # 모멘텀 강화
    else:
        score = 1.5  # 하락추세

        if cross_type == "데드크로스":
            score -= 1.5  # 데드크로스

        if histogram_trend == "강화":
            score -= 1  # 모멘텀 강화

    logger.info("macd============")
    logger.info(trend)
    logger.info(cross_type)
    logger.info(histogram_trend)

    return score
