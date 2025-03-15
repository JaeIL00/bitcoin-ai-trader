import time
from datetime import datetime, timezone
from log_generator import set_logger
import statistics
from api.api import get_trade_ticks_api_call

logger = set_logger()


def analyze_volume_from_daily_ticks(daily_ticks_dict):
    """
    일별 체결 데이터를 분석하여 1단계 트레이딩 로직에 활용할 볼륨 분석 데이터 생성

    Args:
        daily_ticks_dict: 일별 체결 데이터 딕셔너리
            {
                'day_ago_1': [체결 데이터 리스트],
                'day_ago_2': [체결 데이터 리스트],
                ...
                'day_ago_7': [체결 데이터 리스트]
            }

    Returns:
        dict: 볼륨 분석 결과와 종합 점수를 포함한 데이터 인터페이스
    """

    # 결과 저장용 딕셔너리
    result = {
        "volume_score": 0,  # 최종 볼륨 점수 (-4 ~ +4 범위)
        "volume_signals": {},  # 감지된 볼륨 신호들
        "volume_metrics": {},  # 주요 볼륨 지표
        "volume_patterns": {},  # 식별된 볼륨 패턴
        "data_quality": {  # 분석에 사용된 데이터 품질 정보
            "days_count": len(daily_ticks_dict),
            "total_ticks": sum(len(ticks) for ticks in daily_ticks_dict.values()),
        },
    }

    # 충분한 데이터가 없으면 기본값 반환
    if (
        not daily_ticks_dict
        or sum(len(ticks) for ticks in daily_ticks_dict.values()) < 100
    ):
        result["volume_signals"]["insufficient_data"] = True
        return result

    # 1. 일별 기본 볼륨 지표 계산
    daily_metrics = {}
    for day_key, ticks in daily_ticks_dict.items():
        if not ticks:
            continue

        # 날짜 추출 (day_ago_1 → 1로 변환)
        day_num = int(day_key.split("_")[-1])

        # 볼륨 데이터 추출
        volumes = [tick["trade_volume"] for tick in ticks]

        # 매수 거래량만 추출 (매도 거래량은 사용되지 않음)
        buy_volumes = [
            tick["trade_volume"] for tick in ticks if tick["ask_bid"] == "BID"
        ]

        # 기본 통계 계산
        total_volume = sum(volumes)
        avg_volume = total_volume / len(volumes) if volumes else 0
        median_volume = statistics.median(volumes) if volumes else 0
        max_volume = max(volumes) if volumes else 0
        volume_std = statistics.stdev(volumes) if len(volumes) > 1 else 0

        # 대량 거래 식별 (평균의 3배 이상)
        large_trades = [vol for vol in volumes if vol > avg_volume * 3]
        large_trade_ratio = len(large_trades) / len(volumes) if volumes else 0

        # 시간대별 볼륨 (1시간 단위로 집계)
        hourly_volumes = {}
        for tick in ticks:
            tick_time = datetime.fromtimestamp(
                tick["timestamp"] / 1000, tz=timezone.utc
            )
            hour = tick_time.hour

            if hour not in hourly_volumes:
                hourly_volumes[hour] = []

            hourly_volumes[hour].append(tick["trade_volume"])

        hourly_stats = {
            hour: {
                "total": sum(vols),
                "count": len(vols),
                "avg": sum(vols) / len(vols) if vols else 0,
            }
            for hour, vols in hourly_volumes.items()
        }

        # 가격-볼륨 상관관계 (연속적인 틱 간의 가격 변화와 볼륨 관계)
        price_changes = []
        sorted_ticks = sorted(ticks, key=lambda x: x["timestamp"])
        for i in range(1, len(sorted_ticks)):
            prev_tick = sorted_ticks[i - 1]
            curr_tick = sorted_ticks[i]

            price_change = curr_tick["trade_price"] - prev_tick["trade_price"]
            price_change_pct = (
                price_change / prev_tick["trade_price"] * 100
                if prev_tick["trade_price"]
                else 0
            )

            price_changes.append(
                {
                    "change": price_change,
                    "change_pct": price_change_pct,
                    "volume": curr_tick["trade_volume"],
                    "direction": (
                        "up"
                        if price_change > 0
                        else "down" if price_change < 0 else "stable"
                    ),
                }
            )

        # 가격 상승/하락 시 볼륨 분석
        up_volumes = [pc["volume"] for pc in price_changes if pc["direction"] == "up"]
        down_volumes = [
            pc["volume"] for pc in price_changes if pc["direction"] == "down"
        ]

        up_avg = sum(up_volumes) / len(up_volumes) if up_volumes else 0
        down_avg = sum(down_volumes) / len(down_volumes) if down_volumes else 0
        volume_ratio = up_avg / down_avg if down_avg else float("inf")

        # 결과 저장
        daily_metrics[day_key] = {
            "day_num": day_num,
            "total_volume": total_volume,
            "avg_volume": avg_volume,
            "median_volume": median_volume,
            "max_volume": max_volume,
            "volume_std": volume_std,
            "large_trade_ratio": large_trade_ratio,
            "large_trade_count": len(large_trades),
            "buy_volume_ratio": sum(buy_volumes) / total_volume if total_volume else 0,
            "hourly_stats": hourly_stats,
            "up_down_volume_ratio": volume_ratio,
            "data_points": len(ticks),
        }

    # 2. 일간 추세 및 패턴 분석
    # 날짜 순으로 정렬된 지표
    sorted_days = sorted(daily_metrics.items(), key=lambda x: x[1]["day_num"])
    daily_volumes = [day_data["avg_volume"] for _, day_data in sorted_days]

    # 볼륨 추세 파악
    volume_trend = "stable"
    trend_score = 0

    if len(daily_volumes) >= 3:
        recent_avg = daily_volumes[-1]
        prev_3day_avg = (
            sum(daily_volumes[-4:-1]) / 3
            if len(daily_volumes) >= 4
            else daily_volumes[-2]
        )

        volume_change_pct = (
            (recent_avg / prev_3day_avg - 1) * 100 if prev_3day_avg else 0
        )

        if volume_change_pct > 30:
            volume_trend = "strong_increase"
            trend_score = 2.0
        elif volume_change_pct > 15:
            volume_trend = "moderate_increase"
            trend_score = 1.0
        elif volume_change_pct < -30:
            volume_trend = "strong_decrease"
            trend_score = -2.0
        elif volume_change_pct < -15:
            volume_trend = "moderate_decrease"
            trend_score = -1.0

    # 3. 매수/매도 불균형 분석
    buy_sell_imbalance = "balanced"
    imbalance_score = 0

    if len(sorted_days) > 0:
        most_recent = sorted_days[-1][1]
        buy_ratio = most_recent["buy_volume_ratio"]

        if buy_ratio > 0.65:
            buy_sell_imbalance = "strong_buying"
            imbalance_score = 1.5
        elif buy_ratio > 0.55:
            buy_sell_imbalance = "moderate_buying"
            imbalance_score = 0.8
        elif buy_ratio < 0.35:
            buy_sell_imbalance = "strong_selling"
            imbalance_score = -1.5
        elif buy_ratio < 0.45:
            buy_sell_imbalance = "moderate_selling"
            imbalance_score = -0.8

    # 4. 가격 변동과 볼륨 관계 분석
    price_volume_relation = "neutral"
    pv_relation_score = 0

    if len(sorted_days) > 0:
        most_recent = sorted_days[-1][1]
        up_down_ratio = most_recent["up_down_volume_ratio"]

        if up_down_ratio > 1.5:
            price_volume_relation = "bullish_confirmation"
            pv_relation_score = 1.5
        elif up_down_ratio > 1.2:
            price_volume_relation = "bullish_hint"
            pv_relation_score = 0.8
        elif up_down_ratio < 0.67:
            price_volume_relation = "bearish_confirmation"
            pv_relation_score = -1.5
        elif up_down_ratio < 0.83:
            price_volume_relation = "bearish_hint"
            pv_relation_score = -0.8

    # 5. 시간대별 볼륨 패턴 분석
    hour_patterns = {}

    if len(sorted_days) > 0:
        most_recent = sorted_days[-1][1]
        hourly_stats = most_recent["hourly_stats"]

        if hourly_stats:
            total_hourly_volume = sum(stats["total"] for stats in hourly_stats.values())
            avg_hourly_volume = (
                total_hourly_volume / len(hourly_stats) if hourly_stats else 0
            )

            active_hours = []
            quiet_hours = []

            for hour, stats in hourly_stats.items():
                ratio = stats["total"] / avg_hourly_volume if avg_hourly_volume else 1

                if ratio > 1.3:
                    active_hours.append((hour, ratio))
                elif ratio < 0.7:
                    quiet_hours.append((hour, ratio))

            hour_patterns = {
                "active_hours": sorted(active_hours, key=lambda x: x[1], reverse=True),
                "quiet_hours": sorted(quiet_hours, key=lambda x: x[1]),
                "hour_variance": (
                    statistics.variance(
                        [stats["total"] for stats in hourly_stats.values()]
                    )
                    if len(hourly_stats) > 1
                    else 0
                ),
            }

    # 6. 대량 거래 특성 분석
    large_trade_pattern = "normal"
    large_trade_score = 0

    if len(sorted_days) >= 2:
        recent = sorted_days[-1][1]
        prev = sorted_days[-2][1]

        recent_large_ratio = recent["large_trade_ratio"]
        prev_large_ratio = prev["large_trade_ratio"]

        change = recent_large_ratio - prev_large_ratio

        if change > 0.05:
            large_trade_pattern = "increasing_large_trades"
            large_trade_score = 1.0
        elif change < -0.05:
            large_trade_pattern = "decreasing_large_trades"
            large_trade_score = -0.5

    # 7. 최종 볼륨 점수 계산 (가중치 적용)
    final_score = (
        trend_score * 1.2  # 볼륨 추세 (가중치 1.2)
        + imbalance_score * 1.0  # 매수/매도 불균형 (가중치 1.0)
        + pv_relation_score * 1.5  # 가격-볼륨 관계 (가중치 1.5)
        + large_trade_score * 0.8  # 대량 거래 패턴 (가중치 0.8)
    ) / 4.5  # 정규화 (최대 +/- 4 범위로)

    # 결과 인터페이스 구성
    result["volume_score"] = round(final_score, 2)

    result["volume_signals"] = {
        "volume_trend": volume_trend,
        "buy_sell_imbalance": buy_sell_imbalance,
        "price_volume_relation": price_volume_relation,
        "large_trade_pattern": large_trade_pattern,
    }

    result["volume_metrics"] = {
        "daily_metrics": daily_metrics,
        "trend_score": trend_score,
        "imbalance_score": imbalance_score,
        "relation_score": pv_relation_score,
        "large_trade_score": large_trade_score,
    }

    result["volume_patterns"] = {
        "hour_patterns": hour_patterns,
        "volume_trend_data": daily_volumes,
        "recent_buy_ratio": (
            sorted_days[-1][1]["buy_volume_ratio"] if sorted_days else 0.5
        ),
        "recent_up_down_ratio": (
            sorted_days[-1][1]["up_down_volume_ratio"] if sorted_days else 1.0
        ),
    }

    # 1단계 트레이딩 로직에 필요한 현재 데이터 (가장 최근 날짜 기준)
    if sorted_days:
        most_recent_day = sorted_days[-1][0]
        most_recent_ticks = daily_ticks_dict[most_recent_day]

        if most_recent_ticks:
            # 가장 최근 체결 데이터
            latest_tick = sorted(
                most_recent_ticks, key=lambda x: x["timestamp"], reverse=True
            )[0]

            result["current_data"] = {
                "trade_price": latest_tick["trade_price"],
                "trade_volume": latest_tick["trade_volume"],
                "acc_trade_volume_24h": sum(
                    tick["trade_volume"] for tick in most_recent_ticks
                ),
                "acc_trade_price_24h": sum(
                    tick["trade_price"] * tick["trade_volume"]
                    for tick in most_recent_ticks
                ),
                "timestamp": latest_tick["timestamp"],
                "change": (
                    "RISE"
                    if latest_tick["change_price"] > 0
                    else "FALL" if latest_tick["change_price"] < 0 else "EVEN"
                ),
            }

    return result


def enhanced_volume_signal(volume_analysis):
    """볼륨 데이터를 더 정교하게 분석하는 함수"""

    # 기본 볼륨 점수
    base_score = volume_analysis["volume_score"]

    # 추가 신호 확인
    signals = volume_analysis["volume_signals"]
    patterns = volume_analysis["volume_patterns"]

    message = ""

    # 추가 조정
    if (
        signals["volume_trend"] == "strong_increase"
        and patterns["recent_buy_ratio"] > 0.52
    ):
        message = "볼륨 증가 + 매수 우세 = 강화된 매수 신호"
        base_score *= 1.3

    elif (
        signals["volume_trend"] == "strong_decrease"
        and patterns["recent_buy_ratio"] < 0.48
    ):

        message = "볼륨 감소 + 매도 우세 = 강화된 매도 신호"
        base_score *= 1.3

    elif signals["price_volume_relation"] == "bullish_confirmation":
        message = "가격-볼륨 관계가 매수 확증 = 신호 강화"
        base_score += 0.5

    elif signals["price_volume_relation"] == "bearish_confirmation":
        message = "가격-볼륨 관계가 매도 확증 = 신호 강화"
        base_score -= 0.5

    logger.info("volume============")
    logger.info(message)

    return base_score


def volume_signal_calc():
    result = {}
    for i in range(7):
        response = get_trade_ticks_api_call(i + 1)
        result[f"day_ago_{i+1}"] = response
        time.sleep(1)

    voluem_analysis = analyze_volume_from_daily_ticks(result)
    score = enhanced_volume_signal(voluem_analysis)
    return score
