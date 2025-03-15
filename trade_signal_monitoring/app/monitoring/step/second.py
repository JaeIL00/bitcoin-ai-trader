import time
from api.api import (
    get_macd,
    get_moving_average,
    get_rsi,
    get_trade_price_api_call,
    get_candle_api_call,
)
from ..calculation.atr import get_atr
from ..calculation.volume import volume_signal_calc
from log_generator import set_logger
from collections import defaultdict

logger = set_logger()

# 2단계 분석 진입을 위한 임계값
FINAL_THRESHOLD = 8.0  # 3단계로 진행하기 위한 최소 점수


class SecondStepAnalysis:
    def __init__(self, first_step_signal, current_price):
        """
        2단계 분석 초기화

        Args:
            first_step_signal: 1단계에서 전달된 신호 정보
            current_price: 현재 가격
        """
        self.first_step_signal = first_step_signal
        self.current_price = current_price
        self.expected_direction = (
            "bullish" if first_step_signal["normalized_score"] > 0 else "bearish"
        )
        self.scores = defaultdict(float)
        self.details = {}
        self.timeframes = ["hour1", "hour4", "day", "week"]

        self.candle_data = {
            "hour1": get_candle_api_call(
                "https://api.upbit.com/v1/candles/minutes/60", count=100
            ),
            "hour4": get_candle_api_call(
                "https://api.upbit.com/v1/candles/minutes/240", count=120
            ),
            "day": get_candle_api_call(
                "https://api.upbit.com/v1/candles/days", count=200
            ),
            "week": get_candle_api_call(
                "https://api.upbit.com/v1/candles/weeks", count=52
            ),
        }

        # 추가 데이터 로드
        self.atr_data = {tf: get_atr(tf) for tf in ["hour4", "day"]}
        self.volume_profile = volume_signal_calc()

    def run_complete_analysis(self):
        """전체 2단계 분석 실행"""
        logger.info("2단계 정밀 분석 시작...")

        # 각 분석 실행
        self.analyze_moving_averages()
        self.analyze_momentum_indicators()
        self.analyze_chart_patterns()
        self.analyze_volume_patterns()
        self.analyze_support_resistance()
        self.analyze_divergence()
        self.analyze_volatility()

        # 최종 점수 계산 및 판단
        final_decision = self.make_final_decision()

        logger.info(f"2단계 분석 완료: {final_decision}")
        return final_decision

    def analyze_moving_averages(self):
        """이동평균선 관계 상세 분석"""
        logger.info("이동평균선 상세 분석...")

        golden_crosses = 0
        death_crosses = 0
        ma_alignment_score = 0
        price_to_ma_score = 0
        try:
            for tf in self.timeframes:
                ma_data = get_moving_average(tf)

                # 골든/데드 크로스 감지 - 안전하게 개선
                ma_25 = ma_data.get("ma_25")
                ma_50 = ma_data.get("ma_50")

                # 두 값이 모두 존재할 때만 비교
                if ma_25 is not None and ma_50 is not None:
                    # recent_cross는 없으므로 다른 방식으로 크로스 판단
                    # 예: MA 값 비교만으로 판단하거나 별도 로직 구현
                    if ma_25 > ma_50:
                        # 골든 크로스 감지를 위해서는 이전 데이터도 필요합니다
                        # 단순화: 현재 MA25 > MA50이면 골든 크로스로 간주
                        golden_crosses += 1
                    elif ma_25 < ma_50:
                        death_crosses += 1

                # 이동평균선 정렬 상태 점수화 - 안전하게 개선
                alignment = 0
                ma_7 = ma_data.get("ma_7")
                ma_25 = ma_data.get("ma_25")
                ma_50 = ma_data.get("ma_50")
                ma_100 = ma_data.get("ma_100")
                ma_200 = ma_data.get("ma_200")

                # 모든 값이 존재할 때만 정렬 비교
                if all(x is not None for x in [ma_7, ma_25, ma_50, ma_100, ma_200]):
                    if ma_7 > ma_25 > ma_50 > ma_100 > ma_200:
                        alignment = 2 if tf in ["hour4", "day"] else 1
                    elif ma_7 < ma_25 < ma_50 < ma_100 < ma_200:
                        alignment = -2 if tf in ["hour4", "day"] else -1

                # 부분적으로 일부 값만 있는 경우도 처리 가능
                # 예: ma_7, ma_25만 있는 경우 부분 점수 부여
                elif ma_7 is not None and ma_25 is not None:
                    if ma_7 > ma_25:
                        alignment = 1 if tf in ["hour4", "day"] else 0.5
                    elif ma_7 < ma_25:
                        alignment = -1 if tf in ["hour4", "day"] else -0.5

                ma_alignment_score += alignment

                # 현재가와 이동평균선 관계 점수화 - 이미 안전하게 작성됨
                above_count = sum(
                    [
                        1
                        for ma_key in ["ma_7", "ma_25", "ma_50", "ma_100", "ma_200"]
                        if ma_data.get(ma_key) and self.current_price > ma_data[ma_key]
                    ]
                )

                # 타임프레임별 가중치
                weight = (
                    1.5
                    if tf == "hour4"
                    else 1.0 if tf == "day" else 0.75 if tf == "week" else 0.5
                )

                if above_count == 5:
                    price_to_ma_score += 2 * weight
                elif above_count >= 3:
                    price_to_ma_score += 1 * weight
                elif above_count <= 1:
                    price_to_ma_score -= 1 * weight
                elif above_count == 0:
                    price_to_ma_score -= 2 * weight
        except Exception as e:
            logger.error(f"안돼~~{e}")

        # 이동평균선 분석 결과 저장
        cross_score = (golden_crosses - death_crosses) * 1.5

        self.scores["ma_analysis"] = (
            ma_alignment_score + price_to_ma_score + cross_score
        )
        self.details["ma_analysis"] = {
            "golden_crosses": golden_crosses,
            "death_crosses": death_crosses,
            "alignment_score": ma_alignment_score,
            "price_to_ma_score": price_to_ma_score,
            "cross_score": cross_score,
        }

        logger.info(f"이동평균선 분석 점수: {self.scores['ma_analysis']}")

    def analyze_momentum_indicators(self):
        """모멘텀 지표 상세 분석 (RSI, MACD, 스토캐스틱)"""
        logger.info("모멘텀 지표 상세 분석...")

        momentum_score = 0

        # RSI 다중 타임프레임 분석
        rsi_score = 0
        rsi_details = {}

        for tf in self.timeframes:
            rsi_data = get_rsi(tf)
            rsi_value = rsi_data["current_rsi"]
            rsi_details[tf] = rsi_value

            # 타임프레임별 가중치
            weight = (
                1.5
                if tf == "hour4"
                else 1.0 if tf == "day" else 0.75 if tf == "week" else 0.5
            )

            # RSI 기반 점수
            if rsi_value <= 30:
                rsi_score += 2 * weight  # 과매도
            elif rsi_value <= 40:
                rsi_score += 1 * weight  # 약한 과매도
            elif rsi_value >= 70:
                rsi_score -= 2 * weight  # 과매수
            elif rsi_value >= 60:
                rsi_score -= 1 * weight  # 약한 과매수

        # MACD 분석 (4시간 및 일봉 타임프레임)
        macd_score = 0
        macd_details = {}

        for tf in ["hour4", "day"]:
            macd_data = get_macd(tf)

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

            # 히스토그램 분석 (추세 강도 및 방향)
            histogram_values = (
                macd_data["histogram"]
                if isinstance(macd_data["histogram"], list)
                else [macd_data["histogram"]]
            )
            if len(histogram_values) >= 5:
                histogram_trend = (
                    "rising"
                    if histogram_values[-1]
                    > histogram_values[-2]
                    > histogram_values[-3]
                    else (
                        "falling"
                        if histogram_values[-1]
                        < histogram_values[-2]
                        < histogram_values[-3]
                        else "mixed"
                    )
                )
            else:
                histogram_trend = "unknown"

            # MACD 신호 점수화
            weight = 1.5 if tf == "day" else 1.0

            if latest_macd > latest_signal:
                # 상승 추세
                macd_score += 1 * weight

                # 골든 크로스 체크
                if 0 < latest_macd - latest_signal < abs(latest_histogram * 0.2):
                    macd_score += 2 * weight  # 최근 골든 크로스

                # 히스토그램 추세 반영
                if histogram_trend == "rising":
                    macd_score += 1 * weight  # 강화되는 상승세
            else:
                # 하락 추세
                macd_score -= 1 * weight

                # 데드 크로스 체크
                if 0 < latest_signal - latest_macd < abs(latest_histogram * 0.2):
                    macd_score -= 2 * weight  # 최근 데드 크로스

                # 히스토그램 추세 반영
                if histogram_trend == "falling":
                    macd_score -= 1 * weight  # 강화되는 하락세

            macd_details[tf] = {
                "trend": "bullish" if latest_macd > latest_signal else "bearish",
                "histogram_trend": histogram_trend,
                "cross": (
                    "golden"
                    if 0 < latest_macd - latest_signal < abs(latest_histogram * 0.2)
                    else (
                        "death"
                        if 0 < latest_signal - latest_macd < abs(latest_histogram * 0.2)
                        else "none"
                    )
                ),
            }

        # 종합 모멘텀 점수 계산
        momentum_score = rsi_score + macd_score

        self.scores["momentum"] = momentum_score
        self.details["momentum"] = {
            "rsi": rsi_details,
            "macd": macd_details,
            "rsi_score": rsi_score,
            "macd_score": macd_score,
        }

        logger.info(f"모멘텀 지표 분석 점수: {self.scores['momentum']}")

    def analyze_chart_patterns(self):
        """차트 패턴 인식 및 분석"""
        logger.info("차트 패턴 분석...")

        patterns_score = 0
        patterns_found = []

        # 주요 타임프레임에 대해서만 패턴 분석
        for tf in ["hour4", "day"]:
            candles = self.candle_data[tf]
            if not candles or len(candles) < 30:
                continue

            # 기본 캔들 데이터 추출
            highs = [c["high_price"] for c in candles[-30:]]
            lows = [c["low_price"] for c in candles[-30:]]
            closes = [c["trade_price"] for c in candles[-30:]]

            # 1. 헤드앤숄더 패턴 탐지
            if self._detect_head_and_shoulders(highs, lows):
                patterns_found.append(
                    {"name": "head_and_shoulders", "timeframe": tf, "type": "bearish"}
                )
                if self.expected_direction == "bearish":
                    patterns_score -= 2
                else:
                    patterns_score -= 1

            # 2. 역 헤드앤숄더 패턴 탐지
            if self._detect_inverse_head_and_shoulders(highs, lows):
                patterns_found.append(
                    {
                        "name": "inverse_head_and_shoulders",
                        "timeframe": tf,
                        "type": "bullish",
                    }
                )
                if self.expected_direction == "bullish":
                    patterns_score += 2
                else:
                    patterns_score += 1

            # 3. 더블 탑/바텀 패턴 탐지
            double_top = self._detect_double_top(highs, lows)
            if double_top:
                patterns_found.append(
                    {"name": "double_top", "timeframe": tf, "type": "bearish"}
                )
                if self.expected_direction == "bearish":
                    patterns_score -= 1.5
                else:
                    patterns_score -= 0.75

            double_bottom = self._detect_double_bottom(highs, lows)
            if double_bottom:
                patterns_found.append(
                    {"name": "double_bottom", "timeframe": tf, "type": "bullish"}
                )
                if self.expected_direction == "bullish":
                    patterns_score += 1.5
                else:
                    patterns_score += 0.75

            # 4. 삼각형 패턴 탐지
            triangle_type = self._detect_triangle_pattern(highs, lows)
            if triangle_type:
                pattern_type = ""
                if triangle_type == "ascending":
                    pattern_type = "bullish"
                    pattern_score = (
                        1.5 if self.expected_direction == "bullish" else 0.75
                    )
                elif triangle_type == "descending":
                    pattern_type = "bearish"
                    pattern_score = (
                        -1.5 if self.expected_direction == "bearish" else -0.75
                    )
                else:  # symmetric
                    pattern_type = "neutral"
                    pattern_score = (
                        0.5 if self.expected_direction == "bullish" else -0.5
                    )

                patterns_found.append(
                    {
                        "name": f"{triangle_type}_triangle",
                        "timeframe": tf,
                        "type": pattern_type,
                    }
                )
                patterns_score += pattern_score

            # 5. 깃발/페넌트 패턴 탐지
            flag_type = self._detect_flag_pattern(highs, lows, closes)
            if flag_type:
                pattern_type = "bullish" if flag_type == "bull" else "bearish"
                pattern_score = 1.0 if flag_type == "bull" else -1.0

                patterns_found.append(
                    {"name": f"{flag_type}_flag", "timeframe": tf, "type": pattern_type}
                )
                patterns_score += pattern_score
            time.sleep(1)

        self.scores["patterns"] = patterns_score
        self.details["patterns"] = {
            "found": patterns_found,
            "count": len(patterns_found),
        }

        logger.info(
            f"차트 패턴 분석 점수: {self.scores['patterns']}, 발견된 패턴: {len(patterns_found)}"
        )

    def analyze_volume_patterns(self):
        """거래량 패턴 및 변화 분석"""
        logger.info("거래량 패턴 분석...")

        volume_score = 0
        volume_details = {}

        # 볼륨 프로파일이 없다면 생성
        if not self.volume_profile:
            self.volume_profile = volume_signal_calc()

        # 볼륨 프로파일이 숫자인 경우 (점수만 반환하는 경우)
        if isinstance(self.volume_profile, (int, float)):
            volume_score = self.volume_profile
            logger.info(f"볼륨 신호 점수 사용: {volume_score}")
        else:
            # 볼륨 분석 결과 객체인 경우 세부 처리
            try:
                # 볼륨 분석 데이터에서 필요한 정보 추출
                volume_signals = self.volume_profile.get("volume_signals", {})
                volume_metrics = self.volume_profile.get("volume_metrics", {})
                volume_patterns = self.volume_profile.get("volume_patterns", {})

                # 타임프레임별 데이터가 있다면 활용
                daily_metrics = volume_metrics.get("daily_metrics", {})

                for tf in ["hour4", "day"]:
                    # 캔들 데이터 확인 (trade_price는 필요함)
                    candles = self.candle_data.get(tf, [])
                    if not candles or len(candles) < 2:
                        continue

                    # 가격 방향 확인 (캔들 데이터의 종가 사용)
                    closes = [
                        c.get("trade_price", c.get("close_price", 0))
                        for c in candles[-2:]
                    ]
                    price_direction = (
                        closes[-1] > closes[-2] if len(closes) >= 2 else None
                    )

                    # 거래량 신호 활용
                    if tf.lower() == "day" and "day_ago_1" in daily_metrics:
                        day_data = daily_metrics["day_ago_1"]

                        # 거래량 변화율 계산
                        volume_change = day_data.get("volume_change", 0)
                        if not isinstance(volume_change, (int, float)):
                            try:
                                avg_volume = day_data.get("avg_volume", 0)
                                current_volume = day_data.get("current_volume", 0)
                                if avg_volume > 0:
                                    volume_change = (
                                        current_volume / avg_volume - 1
                                    ) * 100
                            except:
                                volume_change = 0

                        volume_details[tf] = {
                            "avg_volume": day_data.get("avg_volume", 0),
                            "current_volume": day_data.get("current_volume", 0),
                            "volume_change": volume_change,
                        }

                        # 거래량 신호 점수화
                        if volume_change > 100:  # 거래량 급증 (평균 대비 2배 이상)
                            if price_direction and self.expected_direction == "bullish":
                                volume_score += 2  # 상승 추세에서 거래량 급증
                            elif (
                                not price_direction
                                and self.expected_direction == "bearish"
                            ):
                                volume_score -= 2  # 하락 추세에서 거래량 급증
                            else:
                                # 예상 방향과 불일치 (추세 전환 가능성)
                                volume_score = -volume_score * 0.5

                        # 거래량 감소 분석
                        if volume_change < -50:  # 거래량 급감 (평균 대비 50% 이하)
                            volume_score -= 0.5  # 거래량 감소는 약한 부정 신호

                # 볼륨 프로파일에서 VPOC 확인
                vpoc = volume_patterns.get("vpoc")
                if vpoc and self.current_price:
                    vpoc_distance = (
                        abs(self.current_price - vpoc) / vpoc * 100 if vpoc else 100
                    )

                    if vpoc_distance < 1:  # 현재가가 주요 매물대 1% 이내
                        if (
                            self.expected_direction == "bullish"
                            and self.current_price > vpoc
                        ):
                            volume_score += 1.5  # 매물대 돌파 시 강한 신호
                        elif (
                            self.expected_direction == "bearish"
                            and self.current_price < vpoc
                        ):
                            volume_score -= 1.5  # 매물대 하향 돌파 시 강한 신호
                        else:
                            volume_score += 0  # 매물대에서 횡보 가능성

                    volume_details["vpoc"] = {
                        "value": vpoc,
                        "distance_pct": vpoc_distance,
                    }

            except Exception as e:
                # 오류 발생 시 기본 점수 사용하고 로깅
                logger.error(f"볼륨 데이터 처리 중 오류 발생: {str(e)}")
                # 기본 볼륨 점수 사용 (volume_signal_calc가 반환한 값)
                if isinstance(self.volume_profile, (int, float)):
                    volume_score = self.volume_profile
                elif (
                    isinstance(self.volume_profile, dict)
                    and "volume_score" in self.volume_profile
                ):
                    volume_score = self.volume_profile.get("volume_score", 0)

        # 최종 점수 및 세부 정보 저장
        self.scores["volume"] = volume_score
        self.details["volume"] = volume_details

        logger.info(f"거래량 패턴 분석 점수: {self.scores['volume']}")

    def analyze_support_resistance(self):
        """지지/저항선 분석"""
        logger.info("지지/저항선 분석...")

        sr_score = 0
        sr_details = {}

        # 1. 피봇 포인트 계산 (일봉 기준)
        day_candles = self.candle_data.get("day", [])
        if day_candles and len(day_candles) >= 3:
            yesterday = day_candles[-2]

            # 기본 피봇 포인트
            pivot = (
                yesterday["high_price"]
                + yesterday["low_price"]
                + yesterday["trade_price"]
            ) / 3

            # 지지선
            s1 = 2 * pivot - yesterday["high_price"]
            s2 = pivot - (yesterday["high_price"] - yesterday["low_price"])

            # 저항선
            r1 = 2 * pivot - yesterday["low_price"]
            r2 = pivot + (yesterday["high_price"] - yesterday["low_price"])

            sr_details["pivot_points"] = {
                "pivot": pivot,
                "s1": s1,
                "s2": s2,
                "r1": r1,
                "r2": r2,
            }

            # 현재가와 피봇 포인트 관계 분석
            pivot_distances = {
                "pivot": abs(self.current_price - pivot) / pivot * 100,
                "s1": abs(self.current_price - s1) / s1 * 100,
                "s2": abs(self.current_price - s2) / s2 * 100,
                "r1": abs(self.current_price - r1) / r1 * 100,
                "r2": abs(self.current_price - r2) / r2 * 100,
            }

            # 가장 가까운 지지/저항선 찾기
            closest_level = min(pivot_distances, key=pivot_distances.get)
            closest_distance = pivot_distances[closest_level]

            sr_details["closest_level"] = {
                "level": closest_level,
                "value": locals()[closest_level],
                "distance_pct": closest_distance,
            }

            # 지지/저항 파괴 점수화
            if closest_distance < 0.5:  # 0.5% 이내에 있는 경우
                if self.expected_direction == "bullish":
                    if (
                        closest_level in ["r1", "r2"]
                        and self.current_price > locals()[closest_level]
                    ):
                        sr_score += 2  # 저항선 돌파
                    elif (
                        closest_level in ["pivot", "s1", "s2"]
                        and self.current_price > locals()[closest_level]
                    ):
                        sr_score += 1  # 지지선 위에 있음
                elif self.expected_direction == "bearish":
                    if (
                        closest_level in ["s1", "s2"]
                        and self.current_price < locals()[closest_level]
                    ):
                        sr_score -= 2  # 지지선 하향 돌파
                    elif (
                        closest_level in ["pivot", "r1", "r2"]
                        and self.current_price < locals()[closest_level]
                    ):
                        sr_score -= 1  # 저항선 아래에 있음

        # 2. 주요 이동평균선 지지/저항 분석
        ma_data = get_moving_average("hour4")
        key_mas = [
            ma_data.get(f"ma_{period}")
            for period in [50, 100, 200]
            if ma_data.get(f"ma_{period}")
        ]

        ma_sr_details = []
        for ma in key_mas:
            if ma:
                ma_distance = abs(self.current_price - ma) / ma * 100
                if ma_distance < 1:  # 1% 이내의 이동평균선
                    ma_details = {
                        "value": ma,
                        "distance_pct": ma_distance,
                        "relation": "above" if self.current_price > ma else "below",
                    }
                    ma_sr_details.append(ma_details)

                    # 이동평균선 지지/저항 점수화
                    if self.expected_direction == "bullish" and self.current_price > ma:
                        sr_score += 1  # 이동평균선 위에서 상승
                    elif (
                        self.expected_direction == "bearish" and self.current_price < ma
                    ):
                        sr_score -= 1  # 이동평균선 아래에서 하락

        sr_details["ma_sr"] = ma_sr_details

        self.scores["support_resistance"] = sr_score
        self.details["support_resistance"] = sr_details

        logger.info(f"지지/저항선 분석 점수: {self.scores['support_resistance']}")

    def analyze_divergence(self):
        """다이버전스 분석 (가격과 지표 간 불일치)"""
        logger.info("다이버전스 분석...")

        divergence_score = 0
        divergence_details = {}

        # 주요 타임프레임에서만 다이버전스 확인
        for tf in ["hour4", "day"]:
            candles = self.candle_data[tf]
            if not candles or len(candles) < 20:
                continue

            # 가격 데이터 추출
            closes = [c["trade_price"] for c in candles[-20:]]

            # RSI 데이터 가져오기
            rsi_data = get_rsi(tf)
            rsi_values = rsi_data.get("rsi_values", [])

            # MACD 데이터 가져오기
            macd_data = get_macd(tf)
            macd_line = macd_data.get("macd_line", [])

            # 충분한 데이터가 있는지 확인
            if len(rsi_values) < 20 or len(macd_line) < 20:
                continue

            # 최근 고점/저점 찾기 (단순화된 방법)
            price_highs = []
            price_lows = []
            rsi_highs = []
            rsi_lows = []
            macd_highs = []
            macd_lows = []

            for i in range(2, len(closes) - 2):
                # 가격 고점/저점
                if (
                    closes[i] > closes[i - 1]
                    and closes[i] > closes[i - 2]
                    and closes[i] > closes[i + 1]
                    and closes[i] > closes[i + 2]
                ):
                    price_highs.append((i, closes[i]))
                elif (
                    closes[i] < closes[i - 1]
                    and closes[i] < closes[i - 2]
                    and closes[i] < closes[i + 1]
                    and closes[i] < closes[i + 2]
                ):
                    price_lows.append((i, closes[i]))

                # RSI 고점/저점
                if i < len(rsi_values) and i + 2 < len(rsi_values):
                    if (
                        rsi_values[i] > rsi_values[i - 1]
                        and rsi_values[i] > rsi_values[i - 2]
                        and rsi_values[i] > rsi_values[i + 1]
                        and rsi_values[i] > rsi_values[i + 2]
                    ):
                        rsi_highs.append((i, rsi_values[i]))
                    elif (
                        rsi_values[i] < rsi_values[i - 1]
                        and rsi_values[i] < rsi_values[i - 2]
                        and rsi_values[i] < rsi_values[i + 1]
                        and rsi_values[i] < rsi_values[i + 2]
                    ):
                        rsi_lows.append((i, rsi_values[i]))

                # MACD 고점/저점
                if i < len(macd_line) and i + 2 < len(macd_line):
                    if (
                        macd_line[i] > macd_line[i - 1]
                        and macd_line[i] > macd_line[i - 2]
                        and macd_line[i] > macd_line[i + 1]
                        and macd_line[i] > macd_line[i + 2]
                    ):
                        macd_highs.append((i, macd_line[i]))
                    elif (
                        macd_line[i] < macd_line[i - 1]
                        and macd_line[i] < macd_line[i - 2]
                        and macd_line[i] < macd_line[i + 1]
                        and macd_line[i] < macd_line[i + 2]
                    ):
                        macd_lows.append((i, macd_line[i]))

            # 충분한 고점/저점이 있는지 확인
            if (
                len(price_highs) < 2
                or len(price_lows) < 2
                or len(rsi_highs) < 2
                or len(rsi_lows) < 2
            ):
                continue

            # RSI 다이버전스 확인
            rsi_divergences = []

            # 1. 하락 다이버전스 (가격 고점 상승, RSI 고점 하락)
            if len(price_highs) >= 2 and len(rsi_highs) >= 2:
                price_high1, price_high2 = price_highs[-2][1], price_highs[-1][1]
                rsi_high1, rsi_high2 = rsi_highs[-2][1], rsi_highs[-1][1]

                if price_high2 > price_high1 and rsi_high2 < rsi_high1:
                    rsi_divergences.append(
                        {
                            "type": "bearish",
                            "description": "RSI 하락 다이버전스 (가격 ↑, RSI ↓)",
                        }
                    )
                    # 점수 조정
                    if self.expected_direction == "bearish":
                        divergence_score -= 2
                    else:
                        divergence_score -= 1

            # 2. 상승 다이버전스 (가격 저점 하락, RSI 저점 상승)
            if len(price_lows) >= 2 and len(rsi_lows) >= 2:
                price_low1, price_low2 = price_lows[-2][1], price_lows[-1][1]
                rsi_low1, rsi_low2 = rsi_lows[-2][1], rsi_lows[-1][1]

                if price_low2 < price_low1 and rsi_low2 > rsi_low1:
                    rsi_divergences.append(
                        {
                            "type": "bullish",
                            "description": "RSI 상승 다이버전스 (가격 ↓, RSI ↑)",
                        }
                    )
                    # 점수 조정
                    if self.expected_direction == "bullish":
                        divergence_score += 2
                    else:
                        divergence_score += 1

            # MACD 다이버전스도 유사하게 확인 가능
            # ...

            divergence_details[tf] = {
                "rsi_divergences": rsi_divergences,
                # "macd_divergences": macd_divergences (추가 가능)
            }

        self.scores["divergence"] = divergence_score
        self.details["divergence"] = divergence_details

        logger.info(f"다이버전스 분석 점수: {self.scores['divergence']}")

    def analyze_volatility(self):
        """ATR 기반 변동성 분석 및 리스크 관리 설정"""
        logger.info("변동성 분석 및 리스크 관리...")

        volatility_score = 0
        volatility_details = {}

        # 주요 타임프레임 ATR 분석
        for tf in ["hour4", "day"]:
            atr_value = self.atr_data.get(tf, {}).get("current_atr")
            if not atr_value:
                continue

            # ATR 비율 (현재가 대비 ATR 비율)
            atr_ratio = (atr_value / self.current_price) * 100

            volatility_details[tf] = {"atr": atr_value, "atr_ratio": atr_ratio}

            # 변동성 기반 점수 계산
            # 지나치게 높은 변동성은 위험 요소, 낮은 변동성은 돌파 확률 낮음
            if atr_ratio > 5:  # 매우 높은 변동성
                volatility_score -= 1
            elif atr_ratio < 0.5:  # 매우 낮은 변동성
                volatility_score -= 0.5

            # 리스크 관리 설정 계산
            if tf == "hour4":  # 4시간 차트 기준 리스크 관리
                # 기본 손절/익절 비율 계산
                stop_loss_pips = atr_value * 2
                take_profit_pips = atr_value * 4  # 기본 1:2 리스크 비율

                # 예상 방향에 따른 손익레벨 계산
                if self.expected_direction == "bullish":
                    stop_loss_level = self.current_price - stop_loss_pips
                    take_profit_level = self.current_price + take_profit_pips
                else:
                    stop_loss_level = self.current_price + stop_loss_pips
                    take_profit_level = self.current_price - take_profit_pips

                volatility_details["risk_management"] = {
                    "stop_loss_pips": int(stop_loss_pips),
                    "take_profit_pips": int(take_profit_pips),
                    "stop_loss_level": int(stop_loss_level),
                    "take_profit_level": int(take_profit_level),
                    "risk_reward_ratio": 2.0,
                }

        self.scores["volatility"] = volatility_score
        self.details["volatility"] = volatility_details

        logger.info(f"변동성 분석 점수: {self.scores['volatility']}")

    def make_final_decision(self):
        """모든 분석 결과를 종합하여 최종 결정"""
        # 각 점수 집계
        total_score = sum(self.scores.values())

        # 가중치 적용
        weights = {
            "ma_analysis": 0.25,
            "momentum": 0.20,
            "patterns": 0.15,
            "volume": 0.10,
            "support_resistance": 0.15,
            "divergence": 0.10,
            "volatility": 0.05,
        }

        weighted_score = sum(self.scores[key] * weights[key] for key in weights)
        normalized_score = min(max(weighted_score, -10), 10)  # -10 ~ 10 범위로 제한

        # 최종 결정
        result = {
            "raw_score": total_score,
            "weighted_score": weighted_score,
            "normalized_score": normalized_score,
            "individual_scores": dict(self.scores),
            "details": self.details,
            "proceed_to_stage3": normalized_score >= FINAL_THRESHOLD
            or normalized_score <= -FINAL_THRESHOLD,
            "recommended_position_size": self._calculate_position_size(
                normalized_score
            ),
            "risk_management": self.details.get("volatility", {}).get(
                "risk_management", {}
            ),
        }

        # 매매 방향 결정
        if normalized_score >= FINAL_THRESHOLD:
            result["action"] = "매수"
            result["confidence"] = (
                "높음" if normalized_score >= FINAL_THRESHOLD + 2 else "중간"
            )
        elif normalized_score <= -FINAL_THRESHOLD:
            result["action"] = "매도"
            result["confidence"] = (
                "높음" if normalized_score <= -FINAL_THRESHOLD - 2 else "중간"
            )
        else:
            result["action"] = "관망"
            result["confidence"] = "낮음"
            result["proceed_to_stage3"] = False

        return result

    def _calculate_position_size(self, score):
        """점수 기반 포지션 크기 계산"""
        abs_score = abs(score)

        if abs_score >= FINAL_THRESHOLD + 2:
            return 1.0  # 최대 포지션 크기 (계좌의 100%)
        elif abs_score >= FINAL_THRESHOLD:
            return 0.75  # 75% 포지션
        elif abs_score >= FINAL_THRESHOLD - 2:
            return 0.5  # 50% 포지션
        else:
            return 0.25  # 25% 포지션 (테스트용)

    # 차트 패턴 탐지 헬퍼 메서드들
    def _detect_head_and_shoulders(self, highs, lows):
        """헤드앤숄더 패턴 탐지"""
        # 단순화된 패턴 탐지 구현
        if len(highs) < 20:
            return False

        # 최근 구간에서 3개의 피크 찾기 (좌어깨, 헤드, 우어깨)
        return False  # 실제 구현 시 패턴 매칭 로직 추가

    def _detect_inverse_head_and_shoulders(self, highs, lows):
        """역 헤드앤숄더 패턴 탐지"""
        # 단순화된 패턴 탐지 구현
        if len(lows) < 20:
            return False

        # 최근 구간에서 3개의 저점 찾기 (좌어깨, 헤드, 우어깨)
        return False  # 실제 구현 시 패턴 매칭 로직 추가

    def _detect_double_top(self, highs, lows):
        """더블 탑 패턴 탐지"""
        # 단순화된 패턴 탐지 구현
        if len(highs) < 15:
            return False

        # 최근 구간에서 2개의 비슷한 고점 찾기
        return False  # 실제 구현 시 패턴 매칭 로직 추가

    def _detect_double_bottom(self, highs, lows):
        """더블 바텀 패턴 탐지"""
        # 단순화된 패턴 탐지 구현
        if len(lows) < 15:
            return False

        # 최근 구간에서 2개의 비슷한 저점 찾기
        return False  # 실제 구현 시 패턴 매칭 로직 추가

    def _detect_triangle_pattern(self, highs, lows):
        """삼각형 패턴 탐지 (상승/하락/대칭)"""
        # 단순화된 패턴 탐지 구현
        if len(highs) < 15 or len(lows) < 15:
            return None

        # 추세선 기울기 분석하여 삼각형 타입 판별
        return None  # 실제 구현 시 "ascending", "descending", "symmetric" 중 하나 반환

    def _detect_flag_pattern(self, highs, lows, closes):
        """깃발/페넌트 패턴 탐지"""
        # 단순화된 패턴 탐지 구현
        if len(highs) < 15:
            return None

        # 이전 추세 및 통합 패턴 확인
        return None  # 실제 구현 시 "bull" 또는 "bear" 반환


def second_step_analysis(first_step_signal, current_price):
    """
    1단계 시그널을 받아 2단계 정밀 분석 실행

    Args:
        first_step_signal: 1단계에서 전달된 신호 정보
        current_price: 현재 가격

    Returns:
        dict: 2단계 분석 결과 및 3단계 진행 여부
    """
    analyzer = SecondStepAnalysis(first_step_signal, current_price)
    return analyzer.run_complete_analysis()


# 메인 함수
def process_signal(first_step_signal):
    """
    1단계에서 전달된 신호 처리 및 2단계 분석 실행

    Args:
        first_step_signal: 1단계에서 전달된 신호 정보

    Returns:
        dict: 2단계 분석 결과 및 3단계 진행 여부
    """
    # 현재가 가져오기
    try:
        trade_price = get_trade_price_api_call()
        current_price = trade_price[0]["trade_price"]

        # 2단계 분석 실행
        result = second_step_analysis(first_step_signal, current_price)

        # 결과 로깅
        logger.info(
            f"2단계 분석 결과: {result['action']} (점수: {result['normalized_score']})"
        )
        logger.info(f"3단계 진행 여부: {result['proceed_to_stage3']}")

        return result

    except Exception as e:
        logger.error(f"2단계 분석 중 오류 발생: {e}")
        return {"proceed_to_stage3": False, "reason": f"오류: {str(e)}"}


# 테스트용 코드
# if __name__ == "__main__":
#     # 테스트 신호 생성
#     test_signal = {
#         "action": "매수_신호",
#         "strength": "중간",
#         "normalized_score": 5.7,
#         "proceed_to_stage2": True,
#         "individual_scores": {
#             "trend_strength": 4.5,
#             "multi_timeframe": 2.8,
#             "ma_25": 2.0,
#             "rsi": 1.5,
#             "macd": 1.2,
#         },
#     }
