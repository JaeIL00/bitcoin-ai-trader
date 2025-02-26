import sys
from log_generator import set_logger, handle_exception
from first_collector import collect_yesterday_to_now
from playwright.sync_api import sync_playwright
from monitoring_collector import monitoring


if __name__ == "__main__":
    logger = set_logger()
    sys.excepthook = handle_exception

    logger.info("Start Crawling Package")

    while True:
        with sync_playwright() as playwright:
            # 오늘 또는 오늘,어제를 기준으로 모든 목록 조회하여 뉴스 기사 db insert
            latest_title = collect_yesterday_to_now(playwright)

            if latest_title is None:
                logger.warning("Retruned None from collect_yesterday_to_now")
            else:
                monitoring(playwright, latest_title)
            # monitoring(
            #     playwright,
            #     "[이드덴버 2025] 프랙스 “RWA·규제 준수로 지속 가능한 스테이블코인 구축할 것",
            # )
