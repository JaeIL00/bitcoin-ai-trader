import time
from datetime import datetime,timedelta
from playwright.sync_api import sync_playwright, Playwright

def run(playwright: Playwright):
    print('크롤링 모듈 시작')
    chromium = playwright.chromium # or "firefox" or "webkit".
    browser = chromium.launch()
    page = browser.new_page()
    page.set_default_navigation_timeout(60000)
    try:
        page.goto(url="https://coinness.com/article",wait_until="networkidle")

        category_btn = page.query_selector('.hKZRXc')
        print('암호화폐 카테고리 탐색 완료')

        category_btn.click()
        page.wait_for_load_state('networkidle')
        print('암호화폐 카테고리 클릭 완료')

        filtered_news_list = []
        is_load_news = True

        while is_load_news:
            print('오늘(어제) 기사 탐색 반복문 시작')
            news_list = page.query_selector_all('.ArticleWrapper-sc-42qvi5-0')
            print('현재 기사 목록 탐색 완료')

            for news in news_list:
                date = news.query_selector('.TimeWrap-sc-42qvi5-1')
                print('기사 업로드 날짜 탐색 완료')
                date_text = date.inner_text()
                lines = date_text.split('\n')  
                date_str = lines[1] 
                
                date_str = ' '.join(date_str.split()[:-1])  
        
                article_date = datetime.strptime(date_str, '%Y년 %m월 %d일')
                
                today = datetime.now()
                
                is_today = (
                    article_date.year == today.year and
                    article_date.month == today.month and
                    article_date.day == today.day
                )

                # 어제 기사 데이터가 서비스에 없을 시 최초에만 수행
                # yesterday = today - timedelta(days=1)  # 어제 날짜 계산
                # is_yesterday = (
                #     article_date.year == yesterday.year and
                #     article_date.month == yesterday.month and
                #     article_date.day == yesterday.day
                # )

            

                if(is_today):
                    filtered_news_list.append(news)
                    # if(len(filtered_news_list) > 3):
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
                page.wait_for_load_state('networkidle')
        
        print('오늘(어제) 기준 기사 탐색 완료')
        print('오늘(어제) 기준 기사 Title, Content 추출 시작')

        errr =  []

        for news in filtered_news_list:
            new_page = browser.new_page()
            news_url = news.get_attribute('href')
            new_page.goto(url=news_url,wait_until="domcontentloaded")
            title = None
            content = None
            if 'digitaltoday' in news_url:
                print('digitaltoday')
                title = new_page.query_selector('h3').inner_text()
                content = new_page.query_selector('#article-view-content-div').inner_text()
            elif 'coinreaders' in news_url:
                print('coinreaders')
                title = new_page.query_selector('.read_title').inner_text()
                content = new_page.query_selector('#textinput').inner_text()
            elif 'blockmedia' in news_url:
                print('blockmedia')
                title = new_page.query_selector('h1').inner_text()
                content = new_page.query_selector('#pavo_contents').inner_text()
            elif 'donga' in news_url:
                print('donga')
                title_list = new_page.query_selector_all('h1')
                title = title_list[1].inner_html()
                content = new_page.query_selector('.news_view').inner_text()
            elif 'etoday' in news_url:
                print('etoday')
                title = new_page.query_selector('.main_title').inner_text()
                content = new_page.query_selector('.articleView').inner_text()
            elif 'asiae' in news_url:
                print('asiae')
                title = new_page.query_selector('h1').inner_text()
                content_container = new_page.query_selector('.article')
                contents = content_container.query_selector_all('p')
                for content_elem in contents:
                    if content is None:
                        content = content_elem.inner_text()
                    else:
                        content += content_elem.inner_text()
            elif 'sedaily' in news_url:
                print('sedaily')
                title = new_page.query_selector('h1').inner_text()
                content = new_page.query_selector('.article').inner_text()
            elif 'techm' in news_url:
                print('techm')
                title = new_page.query_selector('.heading').inner_text()
                content = new_page.query_selector('#article-view-content-div').inner_text()
            elif 'joongang' in news_url:
                print('joongang')
                title = new_page.query_selector('h1').inner_text()
                content = new_page.query_selector('.article_body').inner_text()
            elif 'fnnews' in news_url:
                print('fnnews')
                title = new_page.query_selector('h1').inner_text()
                content = new_page.query_selector('#article_content').inner_text()
            elif 'bonmedia' in news_url:
                print('bonmedia')
                title = new_page.query_selector('.heading').inner_text()
                content = new_page.query_selector('#article-view-content-div').inner_text()
            elif 'zdnet' in news_url:
                print('zdnet')
                title = new_page.query_selector('h1').inner_text()
                content = new_page.query_selector('#articleBody').inner_text()
            elif 'blockstreet' in news_url:
                print('blockstreet')
                title = new_page.query_selector('h1').inner_text()
                content = new_page.query_selector('.view-body').inner_text()
            elif 'dailian' in news_url:
                print('dailian')
                title = new_page.query_selector('h1').inner_text()
                content = new_page.query_selector('description').inner_text()
            elif 'newspim' in news_url:
                print('newspim')
                title = new_page.query_selector('#titlArea1').inner_text()
                content = new_page.query_selector('#viewcontents').inner_text()
            elif 'decenter' in news_url:
                print('decenter')
                title = new_page.query_selector('h2').inner_text()
                content = new_page.query_selector('#articleBody').inner_text()
            elif 'yna.co' in news_url:
                print('yna')
                title = new_page.query_selector('h1').inner_text()
                content = new_page.query_selector('.article').inner_text()
            elif 'mt.co' in news_url:
                print('mt')
                title = new_page.query_selector('h1').inner_text()
                content = new_page.query_selector('.con_area').inner_text()
            elif 'einfomax' in news_url:
                print('einfomax')
                title = new_page.query_selector('.heading').inner_text()
                content = new_page.query_selector('#article-view-content-div').inner_text()

            
            if title is not None and content is not None:
                print(f"title: {title}")
                print(f"content: {len(content)}")
            else:
                errr.append(news_url)

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
            new_page.close()
            time.sleep(0.1)
            
        print('errr',errr) 

    except Exception as e:
        print(f"e: {e}")
      

    # print('브라우저 클로즈')
    # browser.close()

    
    
def crawling():
    print('jo')
    return
    with sync_playwright() as playwright:
        # 오늘 또는 오늘,어제를 기준으로 모든 목록 조회하여 뉴스 기사 db insert
        run(playwright)
        
        # 암호화폐 카테고리를 정말 클릭해서 해당 기사만 보이는건지 점검해야함
    
