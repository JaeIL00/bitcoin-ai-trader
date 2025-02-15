import requests
import logging
import time
from datetime import datetime, timedelta
from news_parser import NewsParser
from playwright.sync_api import Playwright

logger = logging.getLogger(__name__)


def run(playwright: Playwright):
    chromium = playwright.chromium  # or "firefox" or "webkit".
    browser = chromium.launch()
    page = browser.new_page()
    page.set_default_navigation_timeout(60000)
    try:
        page.goto(url="https://coinness.com/article", wait_until="networkidle")

        category_btn = page.query_selector(".hKZRXc")
        logger.info("Get category_btn in https://coinness.com/article")

        category_btn.click()
        page.wait_for_load_state("networkidle")
        logger.info("Clicked category_btn")

        filtered_news_list = []
        is_load_news = True

        while is_load_news:
            logger.info("Start search news")
            news_list = page.query_selector_all(".ArticleWrapper-sc-42qvi5-0")
            logger.info("Get news_list")

            for news in news_list:
                date = news.query_selector(".TimeWrap-sc-42qvi5-1")
                logger.info("Get news upload date")
                date_text = date.inner_text()
                lines = date_text.split("\n")
                date_str = lines[1]

                date_str = " ".join(date_str.split()[:-1])

                article_date = datetime.strptime(date_str, "%Y년 %m월 %d일")

                today = datetime.now()

                is_today = (
                    article_date.year == today.year
                    and article_date.month == today.month
                    and article_date.day == today.day
                )

                # 어제 기사 데이터가 서비스에 없을 시 최초에만 수행
                # yesterday = today - timedelta(days=1)  # 어제 날짜 계산
                # is_yesterday = (
                #     article_date.year == yesterday.year and
                #     article_date.month == yesterday.month and
                #     article_date.day == yesterday.day
                # )

                if is_today:
                    filtered_news_list.append(news)
                    # 빠른 디버깅 하기위해 길이 제한
                    # if len(filtered_news_list) > 3:
                    #     is_load_news = False
                    #     break
                    continue
                # elif(is_yesterday):
                #     # 어제 기사 데이터가 서비스에 없을 시 최초에만 수행
                #     filtered_news_list.append(news)
                #     continue
                else:
                    is_load_news = False
                    break

            if is_load_news:
                filtered_news_list.clear()
                page.get_by_role("button", name="더보기").click()
                page.wait_for_load_state("networkidle")

        logger.info("Start get title and content in news")

        parser = NewsParser()

        for news in filtered_news_list:
            new_page = browser.new_page()
            news_url = news.get_attribute("href")
            new_page.goto(url=news_url, wait_until="domcontentloaded")
            result = parser.parse(news_url, new_page)
            if result:
                title, content = result["title"], result["content"]
                # print(f"title: {title}")
                # print(f"content: {len(content)}")
                logger.info(f"title: {title}")
                logger.info(f"content: {len(content)}")

            # AI에게 분석 요청 / 응답 형식 제공
            # created_at과 어떤 종목에 영향을 주는지 칼럼 추가해야함
            """
            다음 암호화폐 뉴스의 시장 영향을 분석해주세요:

            [뉴스 내용]

            다음 형식으로 응답해주세요:

            {
                "market_sentiment": {
                    "impact_type": "positive/negative/neutral",
                    "strength": 1~5,  // 시장 영향력 강도
                    "reasoning": ["시장 영향 분석 근거1", "시장 영향 분석 근거2"]
                }
            }

            분석 시 다음 사항을 고려해주세요:
            1. 시장 전체에 미치는 영향
            2. 영향력의 강도
            3. 구체적인 근거 제시
            """
            # 응답이 오면 db insert 및 매수/매도 프롬프트 재구성 (매수/매도 모듈 개발 시 정의)
            # requests.post()
            new_page.close()
            time.sleep(0.1)

        logger.error(f"err_url: {parser.err_url}")

    except Exception as e:
        logger.error(f"e: {e}")

    # print('브라우저 클로즈')
    # browser.close()
