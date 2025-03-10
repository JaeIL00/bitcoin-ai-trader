import time
from api.api import get_trade_price_api_call
from log_generator import set_logger
from .step.first import first_step

logger = set_logger()


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

            frist_analysis = first_step(current_price)

            if frist_analysis["proceed_to_stage2"]:
                print("스텝 투 시작")

            time.sleep(ONE_MINUTE / 2)
        except Exception as e:
            logger.error(f"현재가 모니터링 반복문 에러: {e}")
            break

    logger.info("현재가 모니터링 종료")


if __name__ == "__main__":
    trade_price_monitoring()
