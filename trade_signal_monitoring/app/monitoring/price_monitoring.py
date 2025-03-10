from api.api import get_trade_price_api_call
from log_generator import set_logger
from .calculation.volume import volume_signal_calc
from .calculation.macd import macd_calc
from .calculation.moving_average import (
    analyze_multi_timeframes,
    calculate_trend_strength,
    ma_25_calc,
)
from .calculation.rsi import rsi_calc

logger = set_logger()

import time

STRONG_BUY_THRESHOLD = 7
BUY_THRESHOLD = 4
STRONG_SELL_THRESHOLD = -7
SELL_THRESHOLD = -4


def normalize_scores(
    ts_score, mtf_score, ma_score, rsi_score, macd_score, volume_score=0
):
    """
    각 점수를 정규화하여 합산 (-10 ~ +10 범위로 변환)

    Args:
        ts_score: 추세 강도 점수
        mtf_score: 다중 타임프레임 점수
        ma_score: MA_25 점수
        rsi_score: RSI 점수
        macd_score: MACD 점수
        volume_score: 볼륨 분석 점수 (기본값=0)

    Returns:
        float: -10 ~ +10 범위의 정규화된 점수
    """
    # 각 지표별 가중치 설정 (합이 1이 되도록)
    weights = {
        "trend_strength": 0.20,  # 추세 강도 (0.25 → 0.20)
        "multi_timeframe": 0.15,  # 다중 타임프레임 (0.20 → 0.15)
        "ma_25": 0.20,  # MA_25 (유지)
        "rsi": 0.15,  # RSI (유지)
        "macd": 0.15,  # MACD (0.20 → 0.15)
        "volume": 0.15,  # 볼륨 (신규)
    }

    # 각 지표의 최대 가능 점수 예상치 (절대값)
    max_scores = {
        "trend_strength": 7,  # 추세 강도 최대 점수
        "multi_timeframe": 4.5,  # 다중 타임프레임 최대 점수 (3 * 1.5)
        "ma_25": 4,  # MA_25 최대 점수
        "rsi": 3,  # RSI 최대 점수
        "macd": 4,  # MACD 최대 점수
        "volume": 4,  # 볼륨 최대 점수
    }

    # 각 점수를 -1 ~ +1 범위로 정규화
    normalized_ts = ts_score / max_scores["trend_strength"]
    normalized_mtf = mtf_score / max_scores["multi_timeframe"]
    normalized_ma = ma_score / max_scores["ma_25"]
    normalized_rsi = rsi_score / max_scores["rsi"]
    normalized_macd = macd_score / max_scores["macd"]
    normalized_volume = volume_score / max_scores["volume"]

    # 가중 평균 계산
    weighted_score = (
        normalized_ts * weights["trend_strength"]
        + normalized_mtf * weights["multi_timeframe"]
        + normalized_ma * weights["ma_25"]
        + normalized_rsi * weights["rsi"]
        + normalized_macd * weights["macd"]
        + normalized_volume * weights["volume"]  # 볼륨 점수 추가
    )

    # -1 ~ +1 범위를 -10 ~ +10 범위로 확장
    return weighted_score * 10


def trade_price_monitoring():
    logger.info("현재가 모니터링 시작")
    """
    리스크 관리 부재
    손절/익절 전략 미구현
    """
    ONE_MINUTE = 60
    while True:
        try:
            trade_price = get_trade_price_api_call()
            current_price = trade_price[0]["trade_price"]

            ts_score = calculate_trend_strength(current_price)

            mtf_score = analyze_multi_timeframes(current_price)

            ma_25_score = ma_25_calc(current_price)

            rsi_score = rsi_calc()

            macd_score = macd_calc()

            volume_score = volume_signal_calc()

            score = normalize_scores(
                ts_score=ts_score,
                mtf_score=mtf_score,
                ma_score=ma_25_score,
                rsi_score=rsi_score,
                macd_score=macd_score,
            )

            combined_signal = {
                "individual_scores": {
                    "trend_strength": ts_score,
                    "multi_timeframe": mtf_score,
                    "ma_25": ma_25_score,
                    "rsi": rsi_score,
                    "macd": macd_score,
                    "volume": volume_score,  # 볼륨 점수 추가
                },
                "normalized_score": round(score, 2),
            }

            # 정규화된 점수에 맞는 조건식 (임계값은 동일하게 유지)
            if score >= BUY_THRESHOLD:
                combined_signal["action"] = "매수_신호"
                combined_signal["strength"] = (
                    "강함" if score >= STRONG_BUY_THRESHOLD else "중간"
                )
                combined_signal["proceed_to_stage2"] = True
            elif score <= SELL_THRESHOLD:
                combined_signal["action"] = "매도_신호"
                combined_signal["strength"] = (
                    "강함" if score <= STRONG_SELL_THRESHOLD else "중간"
                )
                combined_signal["proceed_to_stage2"] = True
            else:
                combined_signal["action"] = "관망"
                combined_signal["strength"] = "약함"
                combined_signal["proceed_to_stage2"] = False

            logger.info(combined_signal)
            time.sleep(ONE_MINUTE / 2)
        except Exception as e:
            logger.error(f"현재가 모니터링 반복문 에러: {e}")
            break

    logger.info("현재가 모니터링 종료")


if __name__ == "__main__":
    trade_price_monitoring()
