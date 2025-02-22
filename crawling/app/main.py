import logging
from first_collector import collect_yesterday_to_now
from playwright.sync_api import sync_playwright
from monitoring_collector import monitoring

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Start Crawling Package")
    with sync_playwright() as playwright:
        # 오늘 또는 오늘,어제를 기준으로 모든 목록 조회하여 뉴스 기사 db insert
        latest_title = collect_yesterday_to_now(playwright)

        monitoring(playwright, latest_title)

        # 암호화폐 카테고리를 정말 클릭해서 해당 기사만 보이는건지 점검해야함
