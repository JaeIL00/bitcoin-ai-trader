import re
import logging
import time
from datetime import datetime, timedelta
from news_parser import NewsParser
from playwright.sync_api import Playwright

logger = logging.getLogger(__name__)


def search_news_by_date(page):
    logger.info("Start search news by date")

    is_load_news = True
    filtered_news_list = []

    while is_load_news:
        news_list = page.query_selector_all(".ArticleWrapper-sc-42qvi5-0.hdjQhU")
        if len(news_list) == 0:
            logger.error("Not found news list element")
            break

        for news in news_list:
            date = news.query_selector(".TimeWrap-sc-42qvi5-1.gUbaPh")
            if date is None:
                logger.error("Not found date element")
                break

            date_text = date.inner_text()
            pattern = r"(\d{4}년\s\d{1,2}월\s\d{1,2}일)"
            result = re.search(pattern, date_text)
            if not result:
                logger.error(f"Date format is wrong: {date_text}")
                break

            article_date = datetime.strptime(result.group(), "%Y년 %m월 %d일")

            today = datetime.now()

            is_today = (
                article_date.year == today.year
                and article_date.month == today.month
                and article_date.day == today.day
            )

            # 어제 기사 데이터가 서비스에 없을 시 최초에만 수행
            yesterday = today - timedelta(days=1)  # 어제 날짜 계산
            is_yesterday = (
                article_date.year == yesterday.year
                and article_date.month == yesterday.month
                and article_date.day == yesterday.day
            )

            if is_today:
                filtered_news_list.append(news)
                # 빠른 디버깅 하기위해 길이 제한
                if len(filtered_news_list) > 3:
                    is_load_news = False
                    break
                continue
            elif is_yesterday:
                # 어제 기사 데이터가 서비스에 없을 시 최초에만 수행
                filtered_news_list.append(news)
                continue
            else:
                is_load_news = False
                break

        if is_load_news:
            filtered_news_list.clear()
            page.get_by_role("button", name="더보기").click()
            page.wait_for_load_state("networkidle")
            logger.info("Clicked more news button")

    return filtered_news_list


def scrape_content(browser, page):
    logger.info("Start scrape content")

    latest_title = None

    parser = NewsParser()
    for news in search_news_by_date(page):
        new_page = browser.new_page()
        news_url = news.get_attribute("href")
        new_page.goto(url=news_url, wait_until="domcontentloaded")
        result = parser.parse(news_url, new_page)
        if result:
            title, content = result["title"], result["content"]
            if latest_title is None:
                latest_title = title
            logger.info(f"title: {title}")
            logger.info(repr(content))

            # vectorstore post api

        new_page.close()
        time.sleep(0.1)

    logger.error(f"err_url: {parser.err_url}")
    return latest_title


def collect_yesterday_to_now(playwright: Playwright):
    chromium = playwright.chromium  # or "firefox" or "webkit".
    browser = chromium.launch()
    page = browser.new_page()
    page.set_default_navigation_timeout(60000)
    try:
        page.goto(url="https://coinness.com/article", wait_until="networkidle")

        page.get_by_role("button", name="암호화폐", exact=True).click()
        page.wait_for_load_state("networkidle")
        logger.info("Clicked category_btn")

        latest_title = scrape_content(browser, page)

        logger.info("First run completed: collected data from yesterday to now")
        browser.close()
        logger.info("Browser close")

        return latest_title

    except Exception as e:
        logger.error(f"e: {e}")
