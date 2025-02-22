from first_collector import collect_yesterday_to_now
from playwright.sync_api import sync_playwright

if __name__ == "__main__":
    print("Start Crawling Package")
    with sync_playwright() as playwright:
        # 오늘 또는 오늘,어제를 기준으로 모든 목록 조회하여 뉴스 기사 db insert
        collect_yesterday_to_now(playwright)

        # 암호화폐 카테고리를 정말 클릭해서 해당 기사만 보이는건지 점검해야함
