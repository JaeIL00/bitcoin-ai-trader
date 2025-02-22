import time
import logging
from datetime import datetime
from news_parser import NewsParser

logger = logging.getLogger(__name__)


def scrape_content(browser, url):
    logger.info("Start scrape content")

    parser = NewsParser()
    new_page = browser.new_page()

    new_page.goto(url=url, wait_until="domcontentloaded")
    result = parser.parse(url, new_page)
    if result:
        return result["title"], result["content"]

    logger.error(f"err_url: {parser.err_url}")


def monitoring(playwright, latest_title):
    logger.info("Start monitoring crawling")

    chromium = playwright.chromium  # or "firefox" or "webkit".
    browser = chromium.launch()

    is_stop = False

    while not is_stop:
        page = browser.new_page()
        try:
            page.set_default_navigation_timeout(60000)
            page.goto(url="https://coinness.com/article", wait_until="networkidle")

            page.get_by_role("button", name="암호화폐", exact=True).click()
            page.wait_for_load_state("networkidle")
            logger.info("Clicked category_btn")

            news_list = page.query_selector_all(".ArticleWrapper-sc-42qvi5-0.hdjQhU")

            if len(news_list) == 0:
                is_stop = True
                logger.error("news_list is empty")
                break

            for news in news_list:
                url = news.get_attribute("href")
                title, content = scrape_content(browser, url)
                logger.info(f"title: {title}")
                logger.info(repr(content))

                if title == latest_title:
                    break

                # break안되면 vectorstore post api

            time.sleep(60)

        except Exception as e:
            page.close()
            logger.error(f"e: {e}")
            time.sleep(300)

    browser.close()
    now = datetime.now()
    logger.info(f"Browser close. {now.strftime("%Y년 %m월 %d일 %H:%M:%S")}")
