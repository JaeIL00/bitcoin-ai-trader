import logging

logger = logging.getLogger(__name__)


class NewsParser:
    def __init__(self):
        self.err_url = []
        self.company = {
            "digitaltoday": "digitaltoday",
            "coinreaders": "coinreaders",
            "blockmedia": "blockmedia",
            "donga": "donga",
            "etoday": "etoday",
            "asiae": "asiae",
            "sedaily": "sedaily",
            "techm": "techm",
            "joongang": "joongang",
            "fnnews": "fnnews",
            "bonmedia": "bonmedia",
            "zdnet": "zdnet",
            "blockstreet": "blockstreet",
            "dailian": "dailian",
            "newspim": "newspim",
            "decenter": "decenter",
            "yna.co": "yna.co",
            "mt.co": "mt.co",
            "einfomax": "einfomax",
        }

    def parse(self, news_url, new_page):
        """뉴스 URL에 따라 적절한 파서 메서드를 호출하는 메서드"""
        try:
            for company_key in self.company:
                if company_key in news_url:
                    method_name = self.company[company_key].replace(
                        ".", ""
                    )  # yna.co -> yna 처리
                    parser_method = getattr(self, method_name)
                    return parser_method(new_page)

            logger.error(f"Not supported media company: {news_url}")
            self.err_url.append(news_url)
            return None
        except Exception as e:
            logger.error(f"Failed parsing: {str(e)}")
            logger.error(f"Failed parsing url: {news_url}")
            self.err_url.append(news_url)
            return None

    def digitaltoday(self, new_page):
        logger.info("Start parsing news - digitaltoday")
        title = new_page.query_selector("h3").inner_text()
        content = new_page.query_selector("#article-view-content-div").inner_text()
        return {"title": title.strip(), "content": content.strip()}

    def coinreaders(self, new_page):
        logger.info("Start parsing news - coinreaders")
        title = new_page.query_selector(".read_title").inner_text()
        content = new_page.query_selector("#textinput").inner_text()
        return {"title": title.strip(), "content": content.strip()}

    def blockmedia(self, new_page):
        logger.info("Start parsing news - blockmedia")
        title = new_page.query_selector("h1").inner_text()
        content = new_page.query_selector("#pavo_contents").inner_text()
        return {"title": title.strip(), "content": content.strip()}

    def donga(self, new_page):
        logger.info("Start parsing news - donga")
        title_list = new_page.query_selector_all("h1")
        title = title_list[1].inner_html()
        content = new_page.query_selector(".news_view").inner_text()
        return {"title": title.strip(), "content": content.strip()}

    def etoday(self, new_page):
        logger.info("Start parsing news - etoday")
        title = new_page.query_selector(".main_title").inner_text()
        content = new_page.query_selector(".articleView").inner_text()
        return {"title": title.strip(), "content": content.strip()}

    def asiae(self, new_page):
        logger.info("Start parsing news - asiae")
        title = new_page.query_selector("h1").inner_text()
        content_container = new_page.query_selector(".article")
        contents = content_container.query_selector_all("p")
        content = None
        for content_elem in contents:
            if content is None:
                content = content_elem.inner_text()
            else:
                content += content_elem.inner_text()
        return {"title": title.strip(), "content": content.strip()}

    def sedaily(self, new_page):
        logger.info("Start parsing news - sedaily")
        title = new_page.query_selector("h1").inner_text()
        content = new_page.query_selector(".article").inner_text()
        return {"title": title.strip(), "content": content.strip()}

    def techm(self, new_page):
        logger.info("Start parsing news - techm")
        title = new_page.query_selector(".heading").inner_text()
        content = new_page.query_selector("#article-view-content-div").inner_text()
        return {"title": title.strip(), "content": content.strip()}

    def joongang(self, new_page):
        logger.info("Start parsing news - joongang")
        title = new_page.query_selector("h1").inner_text()
        content = new_page.query_selector(".article_body").inner_text()
        return {"title": title.strip(), "content": content.strip()}

    def fnnews(self, new_page):
        logger.info("Start parsing news - fnnews")
        title = new_page.query_selector("h1").inner_text()
        content = new_page.query_selector("#article_content").inner_text()
        return {"title": title.strip(), "content": content.strip()}

    def bonmedia(self, new_page):
        logger.info("Start parsing news - bonmedia")
        title = new_page.query_selector(".heading").inner_text()
        content = new_page.query_selector("#article-view-content-div").inner_text()
        return {"title": title.strip(), "content": content.strip()}

    def zdnet(self, new_page):
        logger.info("Start parsing news - zdnet")
        title = new_page.query_selector("h1").inner_text()
        content = new_page.query_selector("#articleBody").inner_text()
        return {"title": title.strip(), "content": content.strip()}

    def blockstreet(self, new_page):
        logger.info("Start parsing news - blockstreet")
        title = new_page.query_selector("h1").inner_text()
        content = new_page.query_selector(".view-body").inner_text()
        return {"title": title.strip(), "content": content.strip()}

    def dailian(self, new_page):
        logger.info("Start parsing news - dailian")
        title = new_page.query_selector("h1").inner_text()
        content = new_page.query_selector("description").inner_text()
        return {"title": title.strip(), "content": content.strip()}

    def newspim(self, new_page):
        logger.info("Start parsing news - newspim")
        title = new_page.query_selector("#titlArea1").inner_text()
        content = new_page.query_selector("#viewcontents").inner_text()
        return {"title": title.strip(), "content": content.strip()}

    def decenter(self, new_page):
        logger.info("Start parsing news - decenter")
        title = new_page.query_selector("h2").inner_text()
        content = new_page.query_selector("#articleBody").inner_text()
        return {"title": title.strip(), "content": content.strip()}

    def yna(self, new_page):
        logger.info("Start parsing news - yna")
        title = new_page.query_selector("h1").inner_text()
        content = new_page.query_selector(".article").inner_text()
        return {"title": title.strip(), "content": content.strip()}

    def mt(self, new_page):
        logger.info("Start parsing news - mt")
        title = new_page.query_selector("h1").inner_text()
        content = new_page.query_selector(".con_area").inner_text()
        return {"title": title.strip(), "content": content.strip()}

    def einfomax(self, new_page):
        logger.info("Start parsing news - einfomax")
        title = new_page.query_selector(".heading").inner_text()
        content = new_page.query_selector("#article-view-content-div").inner_text()
        return {"title": title.strip(), "content": content.strip()}
