from datetime import datetime
import time

from init_setting_data.init_data import start_get_candle_process
from api.api import get_candle_api_call, get_moving_average, put_moving_average
from .calculation.moving_average import update_moving_average
from log_generator import set_logger

logger = set_logger()

day_url = "https://api.upbit.com/v1/candles/days"
week_url = "https://api.upbit.com/v1/candles/weeks"
hour_4_url = "https://api.upbit.com/v1/candles/minutes/240"
hour_1_url = "https://api.upbit.com/v1/candles/minutes/60"


def hour_1():
    logger.info("hour1 모니터링 시작")
    now = datetime.now()
    current_minute = now.minute
    left_time = (60 - current_minute) * 60 + 60
    logger.info(f"반복문 시작 전 {left_time / 60}분 대기중..")
    time.sleep(left_time)
    while True:
        try:
            # 현재 시간 가져오기
            now = datetime.now()

            # 분만 추출하기
            current_minute = now.minute

            if current_minute > 5:
                left_time = (60 - current_minute) * 60 + 60
                logger.info(
                    f"현재 {current_minute}분 입니다. {left_time / 60}분 대기하겠습니다."
                )
                time.sleep(left_time)
                continue

            candle = get_candle_api_call(url=hour_1_url, count=1)
            past_ma = get_moving_average("hour1")
            if past_ma is None:
                logger.error(
                    "저장된 hour1 이동평균 데이터가 없어서 hour1 모니터링 종료"
                )
                break
            fresh = update_moving_average(
                prev_ma_data=past_ma, new_candle=candle[0], type="hour1"
            )
            put_moving_average(type="hour1", body=fresh)

            hour_1 = 60 * 60
            time.sleep(hour_1)

        except Exception as e:
            break

    logger.error(f"hour1 모니터링 종료: {e}")


def init_data():
    start_get_candle_process()


def start_monitoring():
    init_data()
    hour_1()
