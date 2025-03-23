import time
from api.api import get_trade_price_api_call, post_realtime_log
from log_generator import set_logger
from .step.third import ai_rag_news
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
                post_realtime_log("2단계 분석 시작!")
                logger.info("스텝 투 시작")
                # 2단계 분석 실행
                second_analysis = process_signal(frist_analysis)
                post_realtime_log(
                    f"2단계 분석 결과: {second_analysis['action']}하자! 관심도는 {second_analysis['confidence']}이야."
                )

                # 결과 출력
                logger.info("=" * 50)
                logger.info(second_analysis)
                logger.info("=" * 50)
                logger.info("2단계 분석 최종 결과:")
                logger.info(f"조치: {second_analysis.get('action')}")
                logger.info(f"신뢰도: {second_analysis.get('confidence')}")
                logger.info(f"정규화 점수: {second_analysis.get('normalized_score')}")
                logger.info(
                    f"3단계 진행 여부: {second_analysis.get('proceed_to_stage3')}"
                )
                logger.info("=" * 50)

                if second_analysis["proceed_to_stage3"]:
                    post_realtime_log("3단계 분석 시작!")
                    max_response, confidence = ai_rag_news()
                    """
                    YES: 시장 긍정 신호
                    NO: 시장 부정 신호
                    NEUTRAL: 관망 신호
                    """
                    if max_response == "YES":
                        logger.info(
                            "3단계 분석 결과: 매수 추천! 거래 지표가 이미 떡상이면 매수 늦음!"
                        )
                        post_realtime_log(
                            "3단계 분석 결과: 매수 추천! 거래 지표가 이미 떡상이면 매수 늦음!"
                        )
                    elif max_response == "NO":
                        logger.info(
                            "3단계 분석 결과: 매도 추천! 거래 지표가 이미 나락이면 매수 기회!"
                        )
                        post_realtime_log(
                            "3단계 분석 결과: 매도 추천! 거래 지표가 이미 나락이면 매수 기회!"
                        )
                    else:
                        logger.info(
                            "3단계 분석 결과: 긍정과 부정 의견이 대립하니까 패스!"
                        )
                        post_realtime_log(
                            "3단계 분석 결과: 긍정과 부정 의견이 대립하니까 패스!"
                        )
                else:
                    logger.info("2단계 신호가 3단계 분석 기준을 충족하지 않습니다.")
                    post_realtime_log("2단계 분석 결과: 3단계 분석 시작 기준 미달!")

            else:
                logger.info("1단계 신호가 2단계 분석 기준을 충족하지 않습니다.")
                post_realtime_log("1단계 분석 결과: 2단계 분석 시작 기준 미달!")

            time.sleep(ONE_MINUTE)
        except Exception as e:
            logger.error(f"현재가 모니터링 반복문 에러: {e}")
            break

    logger.info("현재가 모니터링 종료")


if __name__ == "__main__":
    trade_price_monitoring()
