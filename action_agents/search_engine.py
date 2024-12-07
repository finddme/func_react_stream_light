import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import urllib.parse
import datetime
import re
from tavily import TavilyClient
from langchain.schema import Document
from utils.config import *
import httpx
import json
import http.client
# from langchain_community.retrievers import ArxivRetriever
from model.models import tavily_engine
from model.completion import Completion_instructor
from utils.config import state_name_list, states_bank
from utils.doc_search import *
from functools import reduce
from crawl4ai import AsyncWebCrawler
from urllib.parse import urljoin, urlparse
import json
import asyncio
from crawl4ai import AsyncWebCrawler
from urllib.parse import urljoin, urlparse
import aiohttp

tavily_client=tavily_engine()

class Search_API:
    @staticmethod
    def wikipedia_ko(query):
        try:
            return httpx.get("https://ko.wikipedia.org/w/api.php", params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json"
            }).json()["query"]["search"][0]["snippet"]
        except Exception as e: return None

    @staticmethod
    def wikipedia_en(query):
        try:
            return httpx.get("https://en.wikipedia.org/w/api.php", params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json"
            }).json()["query"]["search"][0]["snippet"]
        except Exception as e: return None

    @staticmethod
    def tavily(query):
        tavily_response = tavily_client.search(query=query,search_depth="advanced")
        tavily_response2 = tavily_client.qna_search(query=query, search_depth="advanced",max_results =3)
        web_results = "\n".join([d["content"] for d in tavily_response["results"]])
        web_results+=f"\n{tavily_response2}"
        # web_results = Document(page_content=web_results)
        return web_results

    @staticmethod
    def serper(query):
        serper_client = http.client.HTTPSConnection("google.serper.dev")
        payload = json.dumps({
          "q": query,
          "hl": "en",
          "num": 4,
          "page": 2
        })
        headers = {
          'X-API-KEY': SERPER_API_KEY,
          'Content-Type': 'application/json'
        }
        serper_client.request("POST", "/search", payload, headers)
        response_res = serper_client.getresponse()
        data = response_res.read()
        result=json.loads(data.decode("utf-8"))["organic"]
        
        search_res=""
        for r in result:
            title=r["title"]
            snippet=r["snippet"]
            search_res+=f"{title}: {snippet}\n"
        return search_res
        
    # @staticmethod
    # def arxiv(query):
    #     retriever = ArxivRetriever(
    #         # load_max_docs=1,
    #         get_ful_documents=True,
    #         top_k_results=2
    #     )
    #     docs = retriever.invoke(query)

    #     search_res=""
    #     for d in docs:
    #         title=d.metadata["Title"]
    #         page_content=d.page_content
    #         search_res+=f"{title}: {page_content}\n"

    #         return search_res

class NAVER_NEWS:
    def __call__(self,keyword):
        return self.search(keyword)
        
    def get_news_with_query(self, keyword):
        keyword=quote(keyword)
        url=f"https://search.naver.com/search.naver?where=news&query={keyword}&sm=tab_opt&sort=0&photo=3&field=0&pd=0&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Ar%2Cp%3Aall&is_sug_officeid=0&office_category=0&service_area=0" 
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_titles = []
        news_contents = []
        news_release_date = []
        naver_news_links=[]
        
        def parse_page(soup):
            for idx,info in enumerate(soup.find_all(class_='news_info')):
                if idx<5:
                    date=info.find_all('span',{"class":"info"})[1]
                    news_release_date.append(date.get_text().strip())
    
                    naver_news_link=info.find_all('a', {"class":"info"},href=True)[-1]
                    naver_news_links.append(naver_news_link['href'])
                
            for tit_idx,title in enumerate(soup.find_all(class_='news_tit')):
                if tit_idx<5:
                    news_titles.append(title.get_text().strip())
            for con_idx,content in enumerate(soup.find_all(class_='news_dsc')):
                if con_idx<5:
                    news_contents.append(content.get_text().strip())
    
        parse_page(soup)
        
        next_page_url = url+"#"
        response = requests.get(next_page_url, stream=True)
        response.raw.decode_content = True
        soup = BeautifulSoup(response.text, 'html.parser')
        parse_page(soup)
        return news_titles,news_contents,news_release_date,naver_news_links
    
    def news_crawling(self, naver_news_link):
        response = requests.get(naver_news_link, stream=True)
        response.raw.decode_content = True
        soup = BeautifulSoup(response.text, 'html.parser')
    
        articles=[]
        article = soup.select_one("#dic_area")
        for a in article:
            # print(a)
            articles.append(a.get_text())
        articles=[value for value in articles if value != ""]
        articles=[value for value in articles if value != "\n"]
        articles=articles[1:7]
        articles_str= "\n".join(articles)
        return articles_str
    
    def parse_date(self, date_str):
        now = datetime.datetime.now()
        if '전' in date_str:
            number, unit = re.match(r'(\d+)(\D+)', date_str).groups()
            number = int(number)
            
            if '시간' in unit:
                return now - datetime.timedelta(hours=number)
            elif '분' in unit:
                return now - datetime.timedelta(minutes=number)
            elif '일' in unit:
                return now - datetime.timedelta(days=number)
            elif '주' in unit:
                return now - datetime.timedelta(weeks=number)
            elif '개월' in unit or "달" in unit:
                return now - datetime.timedelta(days=number*30)
        else:
            date_str = date_str.rstrip('.')
            return datetime.datetime.strptime(date_str, "%Y.%m.%d")
    
    def get_news(self, news_titles,news_contents,news_release_date,naver_news_links):
        crawling_result=[]
        for title,content,date,link in zip(news_titles,news_contents,news_release_date,naver_news_links):
            try:
                article_source=self.news_crawling(link)
                res={"title":title,"date":date, "article_source":article_source}
                # res={"title":title,"content":article_source}
                crawling_result.append(res)
            except Exception as e: pass
        crawling_result = sorted(crawling_result, key=lambda x: self.parse_date(x['date']), reverse=True)
        return crawling_result
    
    def search(self, keyword):
        res=[]
        news_titles,news_contents,news_release_date,naver_news_links= self.get_news_with_query(keyword)
        crawling_res= self.get_news(news_titles,news_contents,news_release_date,naver_news_links)
        for idx,c in enumerate(crawling_res):# search result number control
            if idx==0:return c
        #     if idx<5:
        #         res.append(c)
        # return res

class NAVER_FINANCE:
    @staticmethod
    def finance():
        news_res=[]
        url ="https://finance.naver.com/news/mainnews.naver"
        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        # print(soup)
        news_titles = []
        for title in soup.find_all(class_='articleSubject'):
            news_titles.append(title.get_text().strip())

        news_contents = []
        for content in soup.find_all(class_='articleSummary'):
            news_contents.append(content.get_text().split('\n\t')[1].strip())

        for idx,(t,c) in enumerate(zip(news_titles,news_contents)):
            if idx <5:
                news_res.append({'title': f"[최근 금융 시장 주요 뉴스] {t}", 'article_source': c})
        
        return news_res

    @staticmethod
    def finance_search(query):
        search_res=[]

        replacements={"\t":"",
                    "\n":""}
        replace_func = lambda text: reduce(lambda t, kv: t.replace(kv[0], kv[1]), replacements.items(), text)


        query=urllib.parse.quote(query.encode('euc-kr'))
        url=f"https://finance.naver.com/news/news_search.naver?q={query}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        for news in soup.find_all(class_='newsList'):
            article_subject=news.find_all('dd',{"class":"articleSubject"})
            article_summary=news.find_all('dd',{"class":"articleSummary"})
            for idx,(sub,sum) in enumerate(zip(article_subject,article_summary)):
                if idx <5:
                    search_res.append({"title":replace_func(sub.get_text().strip()), "article_source":replace_func(sum.get_text())})
        return search_res


    @staticmethod
    def finance_sise_top():
        news_res=[]
        url ="https://finance.naver.com/"
        response = requests.get(url)
    
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='tbl_home')
        
        rows = table.find('tbody').find_all('tr')
        
        table_data = []
        
        for row in rows:
            stock_name = row.find('th').get_text(strip=True)
            current_price = row.find_all('td')[0].get_text(strip=True)
            change = row.find_all('td')[1].get_text(strip=True)
            rate_of_change = row.find_all('td')[2].get_text(strip=True)
            
            table_data.append({
                '종목명': stock_name,
                '현재가': current_price,
                '전일대비': change,
                '등락률': rate_of_change
            })
    
        return table_data

    @staticmethod
    def finance_sise_top_global():
        url ="https://finance.naver.com/world/"
        response = requests.get(url)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data_list = soup.select('ul.data_lst li')
        
        results = []
        
        for item in data_list:
            title = item.select_one('dt a').text.strip()  # 제목
            value = item.select_one('dd.point_status strong').text.strip()  # 지수 값
            change = item.select_one('dd.point_status em').text.strip()  # 변화 값
            percentage_change = item.select_one('dd.point_status span').text.strip()  # 퍼센트 변화
            date = item.select_one('dd.date em').text.strip()  # 날짜
            
            # 정보를 딕셔너리로 저장
            result = {
                "지수명": title,
                "지수 값": value,
                "변동 값": change,
                "변동 퍼센트": percentage_change,
                "기준 날짜": date
            }
            
            results.append(result)

    @staticmethod
    def finance_stock_market():
        index_data=[]
        url ="https://finance.naver.com/"
        response = requests.get(url)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for area in soup.find_all('div', class_='heading_area'):
            index_name = area.find('a', class_='_stock_section').get_text(strip=True)
            index_value = area.find('span', class_='num').get_text(strip=True)
            change_value = area.find('span', class_='num2').get_text(strip=True)
            percentage_change = area.find('span', class_='num3').get_text(strip=True)
            
            index_data.append({
                'Index Name': index_name,
                'Index Value': index_value,
                'Change Value': change_value,
                'Percentage Change': percentage_change
            })
        return index_data

    @staticmethod
    def kor_base_interest_rate():
        url=f"https://search.naver.com/search.naver?sm=tab_sug.top&where=nexearch&ssc=tab.nx.all&query=%ED%95%9C%EA%B5%AD+%EA%B8%B0%EC%A4%80%EA%B8%88%EB%A6%AC+%EC%B6%94%EC%9D%B4&oquery=%EA%B8%B0%EC%A4%80%EA%B8%88%EB%A6%AC&tqi=ir78KsqptbNssDJYcJGssssss5N-333521&acq=%EA%B8%B0%EC%A4%80%EA%B8%88%EB%A6%AC%EC%B6%94%EC%9D%B4&acr=4&qdt=0"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        base_interest_rate=[]
        base_interest_rate_final=[]
        def parse_page(soup):
            for infos in soup.find_all(class_='cont_info'):
                info_list=infos.find_all('span',{"class":"text"})
                for info in info_list:
                    base_interest_rate.append(info.get_text().strip())

        parse_page(soup)

        for i in range(0, len(base_interest_rate), 3):
            base_interest_rate_final.append(base_interest_rate[i:i+3])

        final_res=""
        for r in base_interest_rate_final[1:]:
            txt=f"{r[0]} 기준 금리 {r[1]}"
            if r[2] == "-": txt += " 변동 없음"
            else: txt += r[2]
            final_res+= f"{txt}\n"
        
        return final_res

    @staticmethod
    def global_base_interest_rate(keyword):
        def find_state(keyword):
            key_list=[]
            for key, values in state_name_list.items():
                for value in values:
                    if value in keyword:
                        key_list.append(key)
            if len(key_list)!=0:
                return key_list
            else:
                return None

        global_base_interest_rate_final=[]
        def parse_page(soup):
            base_interest_rate=[]
            for infos in soup.find_all(class_='cont_info'):
                info_list=infos.find_all('span',{"class":"text"})
                for info in info_list:
                    base_interest_rate.append(info.get_text().strip())
            return base_interest_rate
            
        states=find_state(keyword)
        if states:
            for state in states:
                state_bank=states_bank[state]
                try:
                    query=quote(state_bank)
                    url=f"https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query={query}"
                    response = requests.get(url)
                    soup = BeautifulSoup(response.text, 'html.parser')
                
                    base_interest_rate=[]
                    base_interest_rate_final=[]
                    base_interest_rate=parse_page(soup)
        
                    for i in range(0, len(base_interest_rate), 3):
                        base_interest_rate_final.append(base_interest_rate[i:i+3])
                
                    final_res=""
                    for r in base_interest_rate_final[1:]:
                        txt=f"{r[0]} 기준 금리 {r[1]}"
                        if r[2] == "-": txt += " 변동 없음"
                        else: txt += r[2]
                        final_res+= f"{txt}\n"
                    if final_res=="":pass
                    else:
                        global_base_interest_rate_final.append({"state":state,"interest_rate":final_res})
                except Exception as e: pass

        return global_base_interest_rate_final


class Blog:
    def __init__(self,main_url="https://finddme.github.io/"):
        self.main_url=main_url
        self.search_engine = DocumentSearch(openai_api_key=Openai_API_KEY)

    def should_crawl(self,url, domain, visited_urls):
        if url in visited_urls:
            return False
        parsed_url = urlparse(url)
        if parsed_url.netloc != domain:
            return False
            
        excluded_extensions = ['.pdf', '.jpg', '.png', '.gif', '.zip']
        if any(url.lower().endswith(ext) for ext in excluded_extensions):
            return False
        return True

    def filtering_category(self,url):
        if "#" in url.split("/")[-1]: return False
            
        categories=["llm", "multimodal", "natural", "dev"]
        for c in categories:
            if c in url: return True
            else: return False

    def remove_date_format(self,text):
        pattern = r'\d{2}\s+[A-Z][a-z]{2}\s+\d{4}'
        result = re.sub(pattern, '', text)
        result = ' '.join(result.split())
        return result

    async def extract_title_url(self,crawler, domain,visited_urls):
        try:
            result = await crawler.arun(url=self.main_url)
            
            page_info = {
                'url': self.main_url,
                'content': result.markdown,
                'title': result.title if hasattr(result, 'title') else 'No Title',
                'crawled_at': datetime.datetime.now().isoformat()
            }
            
            urls = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', result.markdown)
            new_links = set()
            title_url_pairs=[]
            
            for found_title, found_url in urls:
                absolute_url = urljoin(self.main_url, found_url)
                if self.should_crawl(absolute_url, domain,visited_urls):
                    if self.filtering_category(absolute_url):
                        new_links.add(absolute_url)
                        title_url_pairs.append({"title":self.remove_date_format(found_title).replace("*","").strip(), "url":absolute_url})
                    
            return page_info, title_url_pairs
        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")
            return None, set()
            
    ############## main page만 크롤링(제목 수집) ##############
    async def title_scrap(self,crawling_verbose=False):
        results = []
        visited_urls = set()
        
        async with AsyncWebCrawler(verbose=crawling_verbose) as crawler: 
            domain = urlparse(self.main_url).netloc
            print(f"Scrap titles from {self.main_url}")
            page_info, title_url_pairs= await self.extract_title_url(self.main_url, crawler, domain,visited_urls)

            await asyncio.sleep(1)  
        
        return results,title_url_pairs

    def find_relative_post_instructor(self, llm, title_url_pairs,query):
        completion=Completion_instructor(llm)
        
        # titles="\n".join([tup["title"] for tup in title_url_pairs])
        titles=str(title_url_pairs)
        prompt=get_relevant_post_prompt.formt(titles,query)

        result=completion(prompt,"")

        return [{"title":ft.title,"url":ft.url} for ft in result.titles]

    ############## 검색된 결과 crawling ##############
    async def process_url(self,url, crawler, domain, visited_urls, session):
        try:
            result = await crawler.arun(url=url) # URL Crawling

            # Crawling 내용 저장
            page_info = {
                'url': url,
                'content': result.markdown,
                'title': result.title if hasattr(result, 'title') else 'No Title',
                'crawled_at': datetime.datetime.now().isoformat()
            }
            ############# link extract 부분 (Crawling 내용에서 URL 추출)#############
            urls = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', result.markdown)
            new_links = set()
            
            for _, found_url in urls:
                absolute_url = urljoin(url, found_url)
                # URL 검증
                if self.should_crawl(absolute_url, domain,visited_urls):
                    if self.filtering_category(absolute_url):
                        new_links.add(absolute_url)
                    
            return page_info, new_links
        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")
            return None, None

    async def crawl(self, relative_posts=None,all=True, max_pages=None,crawling_verbose=True):
        print("--- Crawling Start ---")
        to_crawl = set()
        if relative_posts:
            relative_urls=[rp["url"] for rp in relative_posts]
            to_crawl.update(relative_urls)
        else:to_crawl.add(self.main_url)
        
        results = []
        total_downloaded = []
        visited_urls = set()
        
        while to_crawl and (max_pages is None or len(visited_urls) < max_pages):
            async with AsyncWebCrawler(verbose=crawling_verbose) as crawler: 
                async with aiohttp.ClientSession() as session:
                    current_batch = list(to_crawl)[:min(5, len(to_crawl))]  # 처리할 URL들 batch로 묶음
                    domain = urlparse(current_batch[0]).netloc
                    print(f"Crawling batch of {len(current_batch)} URLs from domain: {domain}")

                    tasks = [self.process_url(url, crawler, domain,visited_urls,session) for url in current_batch] # crawling task 리스트 생성
                    
                    batch_results = await asyncio.gather(*tasks) # 태스크 병렬 실행 

                    all_new_links = set()
                    for url, (page_info, new_link) in zip(current_batch, batch_results):
                        if page_info:
                            results.append(page_info)
                            # total_downloaded.extend(downloaded_file)
                            if all==True:
                                all_new_links.update(new_link)
                        visited_urls.add(url) # 처리된 URL은 visited_urls에 추가하고 to_crawl에서 제거
                        to_crawl.remove(url)
                    
                    to_crawl.update(all_new_links - visited_urls) # 새로 발견한 링크 중에서 아직 방문 안 한 url을 크롤링 대상에 추가
                    
                    await asyncio.sleep(1)  
        
        return results

    ############## 전처리 ##############
    def preprocess_blog_content(self,text):
        text = re.sub(r'Loading \[MathJax\].*?\.js\n*', '', text) # 1. MathJax 로딩 스크립트 제거
        text = re.sub(r'Contact.*?ABOUT \](/about/)\n*', '', text) # 2. 네비게이션, 헤더 부분 제거
        
        # 3. 푸터 부분 제거
        text = re.sub(r'© 2024.*?simplicity_savage\..*?\n*', '', text) 
        text = re.sub(r'Powered by.*?\n*', '', text)
        
        text = re.sub(r'!\[.*?\](?:\(.*?\))?', '', text) # 4. 이미지 태그 제거
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text) # 5. 불필요한 링크 제거
        text = re.sub(r'\* \[(.*?)\]\(#.*?\)', r'* \1', text) # 6. 목차 부분 정리 )
        
        text = re.sub(r'\n\s*\n', '\n\n', text) # 연속 개행 하나로 통합
        
        text = re.sub(r'`{3,}.*?`{3,}', '```', text, flags=re.DOTALL) # 8. 코드 블록 정리 (백틱 통일)
        
        text = text.strip() 
        
        return text

    def extract_main_content(self,text):
        content_pattern = r'# .*?(?=×\n\n#### Search|$)'
        match = re.search(content_pattern, text, re.DOTALL)
        
        if match:
            content = match.group(0)
            return self.preprocess_blog_content(content)
        
        return ""

    def post_markdown_perprocessing(self,crawling_results):
        preprocessing_result=[]
        for cr in crawling_results:
            doc_content=cr["content"]
            processed_text = self.extract_main_content(doc_content)
            
            title_match = re.search(r'# (.*?)\n', processed_text)
            title = title_match.group(1) if title_match else ""
            
            date_match = re.search(r'(\d{2} [A-Za-z]+ \d{4})', processed_text)
            date = date_match.group(1) if date_match else ""
            
            preprocessing_result.append({
                                        'url':cr["url"],
                                        'title': title,
                                        'date': date,
                                        'content': processed_text
                                        })
        return preprocessing_result
    
    ############## chunk 만들기 ##############
    def chunk_split(self,text, chunk_size: int = 2200) -> list[str]:
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        
    def get_chunk(self,processed_result):
        chunked_result=[]
        for pr in processed_result:
            chunks=self.chunk_split(pr["content"])
            for c in chunks:
                pr_bak=pr
                pr_bak["content"]=c
                chunked_result.append(pr_bak)
        return chunked_result

    ############## 실행 ##############
    async def blog_search_basedontitle(self,llm,query):
        results,title_url_pairs = await self.title_scrap()
        relative_posts= self.find_relative_post_instructor( llm, title_url_pairs,query)
        crawling_results = await self.crawl(relative_posts=relative_posts,all=False)
        processed_result=self.post_markdown_perprocessing(crawling_results)
        chunked_result=self.get_chunk(processed_result)

        # search_engine = DocumentSearch(openai_api_key=Openai_API_KEY)
        search_engine.add_documents(chunked_result)
    
    def blog_serach_basic(self, query):
        retrieval_results = self.search_engine.search(query, k=3)
        return retrieval_results

    async def prepare_allpost_chunk(self):
        crawling_results = await self.crawl()
        processed_result=self.post_markdown_perprocessing(crawling_results)
        chunked_result=self.get_chunk(processed_result)

        # search_engine = DocumentSearch(openai_api_key=Openai_API_KEY)
        self.search_engine.add_documents(chunked_result)
        print("--- Search engine Complete ---")
        # return search_engine

