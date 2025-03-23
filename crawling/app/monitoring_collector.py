import time
import requests
from datetime import datetime, timezone
from log_generator import set_logger
from news_parser import NewsParser

logger = set_logger()


def scrape_content(browser, url):
    logger.info("Start scrape content")

    parser = NewsParser()

    with browser.new_page() as new_page:
        new_page.set_default_navigation_timeout(60000)
        new_page.goto(url=url, wait_until="domcontentloaded")
        result = parser.parse(url, new_page)
        if result:
            return result["title"], result["content"]

        logger.error(f"err_url: {parser.err_url}")


def monitoring(playwright, latest_title):
    fresh_latest_title = latest_title
    logger.info("Start monitoring crawling")
    logger.info(f"latest_title: {latest_title}")

    browser = playwright.chromium.connect("ws://playwright:3000")

    start_date = datetime.now().date()

    is_stop = False

    while not is_stop:
        now = datetime.now()
        current_date = now.date()
        current_hour = now.hour

        days_difference = (current_date - start_date).days

        logger.info(f"start_date: {start_date}")
        logger.info(f"current_date: {current_date}")
        logger.info(f"current_date > start_date: {current_date > start_date}")
        logger.info(f"current_hour: {current_hour} >= 5")

        if days_difference >= 1 and current_hour >= 5:
            logger.info(f"하루가 지나고 새벽 5시 이후입니다. 크롤링 작업 종료합니다.")
            logger.info(
                f"시작 날짜: {start_date}, 현재 날짜: {current_date}, 현재 시간: {current_hour}시"
            )
            is_stop = True
            break

        with browser.new_page() as page:
            try:
                page.set_default_navigation_timeout(60000)
                page.goto(url="https://coinness.com/article", wait_until="networkidle")

                page.get_by_role("button", name="암호화폐", exact=True).click()
                page.wait_for_load_state("networkidle")
                logger.info("Clicked category_btn")

                news_list = page.query_selector_all(
                    ".ArticleWrapper-sc-42qvi5-0.hdjQhU"
                )

                if len(news_list) == 0:
                    is_stop = True
                    logger.error("news_list is empty")
                    break

                temp_title = None

                for index, news in enumerate(news_list):
                    url = news.get_attribute("href")
                    title, content = scrape_content(browser, url)

                    if title == fresh_latest_title:
                        logger.info(f"Same lastest title and current title")
                        logger.info(f"Break")
                        break

                    logger.info(f"Catch new content!!")
                    logger.info(f"fresh_latest_title: {fresh_latest_title}")
                    logger.info(f"title: {title}")

                    try:
                        response = requests.post(
                            "http://vector_rag:8000/vector-store/add-content",
                            json={
                                "content": content,
                            },
                        )

                        response.raise_for_status()

                        response_realtime_log = requests.post(
                            "http://backend:8000/api/logs",
                            json={
                                "message": f"새로운 기사를 수집했어요! {title}",
                                "module": "crawling",
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            },
                        )

                        response_realtime_log.raise_for_status()

                        if index == 0:
                            temp_title = title
                        logger.info("Success save content")
                    except Exception as e:
                        logger.error(f"Failed Save Content: {e}")
                        break

                    # fresh_latest_title 갱신
                if temp_title is not None:
                    logger.info(f"temp_title 새로 할당: latest_title: {latest_title}")
                    logger.info(f"temp_title: {temp_title}")
                    fresh_latest_title = temp_title
                    temp_title = None

                logger.info("monitor....")
                time.sleep(120)

            except Exception as e:
                logger.error(f"e: {e}")
                time.sleep(300)
            finally:
                page.close()

    try:
        response = requests.delete(
            "http://vector_rag:8000/vector-store",
        )
        response.raise_for_status()
        logger.info("Success delete store")
    except Exception as e:
        logger.error(f"Failed delete store: {e}")
    finally:
        browser.close()
        now = datetime.now()
        logger.info(f"Browser close. {now.strftime("%Y년 %m월 %d일 %H:%M:%S")}")
