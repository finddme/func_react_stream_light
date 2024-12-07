from .search_engine import *
from utils.config import *
from db.retrieve import *
import random
import torch
# from model.models import img_model_call,img_inference
from utils.config import state_name_list, kor

naver_news=NAVER_NEWS()
naver_finance=NAVER_FINANCE()
search_engine=Search_API()
print("--- Make search engine ---")
blog=Blog()
asyncio.run(blog.prepare_allpost_chunk())

class Action:
    @staticmethod
    def web_ko(query):
        wiki_res=search_engine.wikipedia_ko(query)
        naver_news_res=naver_news(query)
        tavily_res=search_engine.tavily(query)

        web_search_list=tavily_res.split("\n")
        web_search_list.append(wiki_res)
        # list(map(lambda x: web_search_list.append(str(x)), naver_news_res)) # naver_news_res 결과도 rerank
        web_search_list = list(map(lambda x: {"info": x}, web_search_list))
        web_search_res=reranker_cohere_basic(query, web_search_list, "info")

        web_search_res=f"""뉴스 검색 결과: {naver_news_res} 
                            기타 검색 결과: {web_search_res}"""

        return web_search_res

    @staticmethod
    def web_global(query):
        wiki_res=search_engine.wikipedia_en(query)
        tavily_res=search_engine.tavily(query)
        serper_res=search_engine.serper(query)
        web_search_res=f"{serper_res} \n {tavily_res} \n {wiki_res}"
        return web_search_res

    @staticmethod
    def web_finance(query):
        fn_res=naver_finance.finance()
        fn_search_res=naver_finance.finance_search(query)

        fn_news_res=fn_res+fn_search_res
        fn_news_res=reranker_cohere_basic(query, fn_news_res, "title")

        fn_sise_res=naver_finance.finance_sise_top()
        fn_sm_res=naver_finance.finance_stock_market()
        fn_sise_global_res=naver_finance.finance_sise_top_global()

        base_interest=""
        if "금리" in query:
            if len([g for g in state_name_list if g in query.replace(" ","")])!=0:
                finance_info= naver_finance.global_base_interest_rate(query)
                if len(finance_info)!=0:
                    for fi in finance_info:
                        state=fi["state"]
                        interest_rate=fi["interest_rate"]
                        base_interest+=f"{state} 금리 정보: {interest_rate}\n"
            if len([k for k in kor if k in query.replace(" ","")])!=0:
                finance_info= naver_finance.kor_base_interest_rate()
                base_interest+=f"대한민국 금리 정보: {finance_info}\n"

        web_search_res=f"""뉴스: {fn_news_res}
                            대한민국 주식 거래 상위 종목:{fn_sise_res}
                            해외 주식 거래 상위 종목: {fn_sise_global_res}
                            증시: {fn_sm_res}
                            {base_interest}"""
        return web_search_res

    @staticmethod
    def ai_retrieval(query):
        return blog.blog_serach_basic(query)
    
class Action_Map:
    def __init__(self,state):
        self.query=state["query"]
        self.action=state["action "]

        act_function=action_map[self.action]
        action_res=act_function(self.query)

        return action_res
