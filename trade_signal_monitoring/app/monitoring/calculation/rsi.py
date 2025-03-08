from log_generator import set_logger

logger = set_logger()


def update_rsi(prev_rsi_data, new_candle, type):
    """
    기존 RSI 데이터에 새로운 캔들 하나를 추가하여 RSI 계산을 업데이트하는 함수

    Args:
        prev_rsi_data (Dict): 이전에 저장된 RSI 데이터
        new_candle (Dict): API에서 새로 받아온 캔들 데이터 하나
        type (str): 캔들 타입 (day, week, hour4, hour1)

    Returns:
        Dict: 업데이트된 RSI 결과와 메타데이터를 포함한 딕셔너리
    """
    period = 14  # RSI 기본 기간

    # 결과 초기화 (기존 데이터 복사)
    result = prev_rsi_data.copy()

    # 새 캔들 데이터
    new_timestamp = new_candle["candle_date_time_utc"]
    new_price = new_candle["trade_price"]
    prev_closing_price = new_candle.get("prev_closing_price", new_price * 0.99)

    # RSI 계산에 필요한 최소 데이터 수 확인
    if len(result["rsi_values"]) < period:
        logger.warning(f"RSI 업데이트를 위한 충분한 데이터가 없습니다. type: {type}")
        return result

    # 중복 데이터 처리
    is_duplicate = (
        len(result["timestamps"]) > 0 and result["timestamps"][-1] == new_timestamp
    )
    if is_duplicate:
        # 마지막 데이터 제거
        result["timestamps"].pop()
        result["rsi_values"].pop()

    # 데이터가 있는 경우만 업데이트 진행
    if len(result["timestamps"]) > 0:
        # 이전 RSI로부터 계산 시작
        prev_rsi = result["rsi_values"][-1]

        # 새로운 delta 계산
        delta = new_price - prev_closing_price

        # 새로운 gain/loss 계산
        gain = max(0, delta)
        loss = abs(min(0, delta))

        # Wilder의 지수 이동 평균(EMA) 방식으로 RSI 계산
        # 이전 RSI로부터 RS(Relative Strength) 역산
        if prev_rsi < 100:
            prev_rs = prev_rsi / (100 - prev_rsi)
        else:
            prev_rs = float("inf")

        # 이전 평균 gain/loss 역산 (RSI 공식을 활용한 역계산)
        # RS = avg_gain / avg_loss 공식 활용
        # RS를 알고 있으면 avg_gain과 avg_loss의 비율은 알 수 있지만
        # 정확한 값은 알 수 없으므로 새로운 gain/loss 값을 기준으로 역추산
        if loss > 0:
            prev_avg_loss = loss
            prev_avg_gain = prev_rs * prev_avg_loss
        elif gain > 0:
            prev_avg_gain = gain
            prev_avg_loss = prev_avg_gain / prev_rs if prev_rs > 0 else 0
        else:
            # delta가 0인 경우 이전 RSI 값 그대로 유지
            new_rsi = prev_rsi
            result["rsi_values"].append(new_rsi)
            result["timestamps"].append(new_timestamp)
            result["current_rsi"] = new_rsi
            result["last_updated"] = new_timestamp

            # 불필요한 필드 제거
            result.pop("id", None)
            result.pop("created_at", None)

            logger.info(
                f"RSI 업데이트 완료 (가격 변동 없음). type: {type}, 현재 RSI: {new_rsi}"
            )
            return result

        # 새로운 평균 gain/loss 계산 (EMA 방식)
        avg_gain = (prev_avg_gain * (period - 1) + gain) / period
        avg_loss = (prev_avg_loss * (period - 1) + loss) / period

        # 새로운 RS와 RSI 계산
        if avg_loss == 0:
            new_rsi = 100
        else:
            rs = avg_gain / avg_loss
            new_rsi = 100 - (100 / (1 + rs))

        # 소수점 둘째 자리까지 반올림
        new_rsi = round(new_rsi, 2)

    # 새 RSI 값 추가
    result["rsi_values"].append(new_rsi)
    result["timestamps"].append(new_timestamp)

    # 최신 RSI 값 업데이트
    result["current_rsi"] = new_rsi
    result["last_updated"] = new_timestamp

    # 불필요한 필드 제거
    result.pop("id", None)
    result.pop("created_at", None)

    logger.info(f"RSI 업데이트 완료. type: {type}, 현재 RSI: {new_rsi}")

    return result
