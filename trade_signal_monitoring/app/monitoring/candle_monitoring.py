from datetime import datetime
import time
import schedule
from multiprocessing import Process, Event

from api.api import (
    get_candle_api_call,
    get_moving_average,
    get_rsi,
    put_macd,
    put_moving_average,
    put_rsi,
)
from .calculation.rsi import update_rsi
from .calculation.macd import macd
from .calculation.moving_average import update_moving_average
from log_generator import set_logger

logger = set_logger()

day_url = "https://api.upbit.com/v1/candles/days"
week_url = "https://api.upbit.com/v1/candles/weeks"
hour_4_url = "https://api.upbit.com/v1/candles/minutes/240"
hour_1_url = "https://api.upbit.com/v1/candles/minutes/1"


def api_call_with_calc(type):
    logger.info(f"{type} 타입의 api call 시작")
    url = None
    if type == "hour1":
        url = hour_1_url
    if type == "hour4":
        url = hour_4_url
    if type == "day":
        url = day_url
    if type == "week":
        url = week_url
    candle = get_candle_api_call(url=url, count=1)
    past_ma = get_moving_average(type)
    if past_ma is None:
        logger.error(f"저장된 {type} 이동평균 데이터가 없어서 {type} 모니터링 종료")
        return
    fresh_ma = update_moving_average(
        prev_ma_data=past_ma, new_candle=candle[0], type=type
    )
    put_moving_average(type=type, body=fresh_ma)

    fresh_macd = macd(type=type, ma_values_data=fresh_ma["ma_values"])
    put_macd(type=type, body=fresh_macd)

    past_rsi = get_rsi(type=type)
    if past_rsi is None:
        logger.error(f"저장된 {type} RSI 데이터가 없어서 {type} 모니터링 종료")
        return
    fresh_rsi = update_rsi(prev_rsi_data=past_rsi, new_candle=candle[0], type=type)
    put_rsi(type=type, body=fresh_rsi)
    logger.info(f"{type} 타입의 api call 종료")


def update_ma(type, stop_event):
    logger.info(f"{type} 모니터링 시작")

    one_minute = 60
    one_hour = 60
    now = datetime.now()
    current_minute = now.minute

    if type == "hour1":
        minute_interval = one_hour
        left_time_sec = (minute_interval - current_minute) * 60 + one_minute
    if type == "hour4":
        minute_interval = one_hour * 4
        current_hour = now.hour
        next_target_hour = None
        target_hours = [1, 5, 9, 13, 17, 21]
        for hour in target_hours:
            if hour > current_hour:
                next_target_hour = hour
                break
            elif hour == current_hour:
                if hour == 21:
                    next_target_hour = 1
                    break
                next_target_hour = hour + 4
                break
            elif hour == 21:
                next_target_hour = 1
        if next_target_hour > current_hour:
            left_minute = (next_target_hour * 60) - (current_hour * 60 + current_minute)
            left_time_sec = left_minute * 60 + one_minute
        else:
            left_hour = 24 - current_hour
            left_minute = (next_target_hour * 60) + (left_hour * 60) - current_minute
            left_time_sec = left_minute * 60 + one_minute

    logger.info(f"{type} 반복문 시작 전 {left_time_sec / 60}분 대기중..")
    time.sleep(left_time_sec)
    while True:
        try:
            # 현재 시간 가져오기
            now = datetime.now()

            # 분만 추출하기
            current_minute = now.minute

            api_call_with_calc(type)

            logger.info(f"{type} 업데이트 후 {minute_interval}분 대기중..")
            time.sleep(minute_interval * 60)

        except Exception as e:
            stop_event.set()
            logger.error(f"{type} 모니터링 에러: {e}")
            break

    logger.error(f"{type} 모니터링 종료")


def start_week_day_schedule(stop_event):
    logger.info("week_day 모니터링 시작")
    schedule.every().day.at("09:01").do(api_call_with_calc, "day")
    schedule.every().monday.at("09:01").do(api_call_with_calc, "hour1")
    while not stop_event.is_set():
        schedule.run_pending()
        time.sleep(60)

    logger.info("week_day 모니터링 종료")


def start_candle_monitoring():
    stop_event = Event()
    hour1_p = Process(
        target=update_ma,
        args=(
            "hour1",
            stop_event,
        ),
    )
    hour4_p = Process(
        target=update_ma,
        args=(
            "hour4",
            stop_event,
        ),
    )
    week_day_p = Process(target=start_week_day_schedule, args=(stop_event,))
    hour1_p.start()
    hour4_p.start()
    week_day_p.start()
