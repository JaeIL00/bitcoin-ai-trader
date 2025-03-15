import time
from api.api import get_trade_price_api_call
from log_generator import set_logger
from .step.second import process_signal
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
                logger.info("스텝 투 시작")
                # 2단계 분석 실행
                result = process_signal(frist_analysis)

                # 결과 출력
                logger.info("=" * 50)
                logger.info(result)
                logger.info("=" * 50)
                logger.info("2단계 분석 최종 결과:")
                logger.info(f"조치: {result.get('action')}")
                logger.info(f"신뢰도: {result.get('confidence')}")
                logger.info(f"정규화 점수: {result.get('normalized_score')}")
                logger.info(f"3단계 진행 여부: {result.get('proceed_to_stage3')}")
                logger.info("=" * 50)

            else:
                logger.info("1단계 신호가 2단계 분석 기준을 충족하지 않습니다.")

            time.sleep(ONE_MINUTE)
        except Exception as e:
            logger.error(f"현재가 모니터링 반복문 에러: {e}")
            break

    logger.info("현재가 모니터링 종료")


if __name__ == "__main__":
    trade_price_monitoring()
