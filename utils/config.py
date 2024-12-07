import os
Openai_API_KEY=os.environ.get('Openai_API_KEY')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
Claude_API_KEY=os.environ.get('Claude_API_KEY')
Together_API_KEY=os.environ.get('Together_API_KEY')

TAVILY_API_KEY=os.environ.get('TAVILY_API_KEY')
SERPER_API_KEY=os.environ.get('SERPER_API_KEY')
coher_API_KEY= os.environ.get('coher_API_KEY')

HF_KEY=os.environ.get('HF_KEY')

openai_model_name="gpt-4o"
groq_model_name="llama-3.1-70b-versatile"
claude_model_name="claude-3-5-sonnet-20240620"
together_model_name="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"


DB={"known_class":["b_with_title","law"],
    "weaviate_url":"http://192.168.0.186:8080",
    "weaviate_url_webcluster":"https://8ggks8n0s0iockcedg1gma.c0.us-west3.gcp.weaviate.cloud",
    "weaviate_auth":"BISuJChcrxKaopUYA5Y6N7gxXt3zcdwyanbX",
    "ai_weaviate_class":"b_with_title",
    "law_weaviate_class":"law",
    "law_consult_weaviate_class":"law_consult"}

IMAGE={"image_model":"black-forest-labs/FLUX.1-schnell",
    "image_gen_endpoint":"http://115.71.28.105:8782/genrate_image"}

additional_phrase={"korea_news_search":"", 
        "global_news_search":"", 
        "financial_market_search": "\n\n\n ※ 정확한 금융 지식 및 투자 정보는 금융 전문가에게 문의하는 것을 추천드립니다. ",
        "ai_related_search": "",
       "legal_related_search": "\n\n\n ※ 정확한 법률 지식 및 법률 상담은 법률 전문가에게 문의하는 것을 추천드립니다."}

state_name_list={"미국":["미국", "USA", "America", "US"], 
                "유럽":["Europe", "유럽",    "알바니아", "안도라", "아르메니아", "오스트리아", "아제르바이잔", "벨라루스", "벨기에",
                        "보스니아 헤르체고비나", "불가리아", "크로아티아", "키프로스", "체코",
                        "덴마크", "에스토니아", "핀란드", "프랑스", "조지아", "독일", "그리스",
                        "헝가리", "아이슬란드", "아일랜드", "이탈리아", "카자흐스탄", "코소보", "라트비아",
                        "리히텐슈타인", "리투아니아", "룩셈부르크", "몰타", "몰도바", "모나코",
                        "몬테네그로", "네덜란드", "북마케도니아", "노르웨이", "폴란드", "포르투갈",
                        "루마니아", "러시아", "산마리노", "세르비아", "슬로바키아", "슬로베니아", "스페인",
                        "스웨덴", "스위스", "터키", "우크라이나", "바티칸 시국"], 
                "영국":["영국","UK"], 
                "일본":["일본"], 
                "중국":["중국"],
                "캐나다":["캐나다"], 
                "호주":["호주"], 
                "러시아":["러시아"], 
                "사우디아라비아":["사우디아라비아","사우디"],
                "브라질":["브라질"], 
                "인도":["인도"],
                "튀르키예":["튀르키예","터키"], 
                "남아프리카":["남아프리카"],
                "아르헨티나":["아르헨티나"], 
                "인도네시아":["인도네시아"]}

kor=["대한민국","한국","우리나라"]

states_bank={"미국":"미국 기준금리 추이", "유럽":"유럽중앙은행 기준금리", "영국":"영국은행 기준금리", "일본":"일본은행 기준금리", "중국":"중국인민은행 기준금리", 
                "캐나다":"캐나다은행 기준금리", "호주":"호주연방준비은행 기준금리", "러시아":"러시아연방중앙은행 기준금리", "사우디아라비아":"사우디아라비아 통화청 기준금리", 
                "브라질":"브라질 중앙은행 기준금리", "인도":"인도연방준비은행 기준금리","튀르키예":"튀르키예중앙은행 기준금리", "남아프리카":"남아프리카준비은행 기준금리", 
                "아르헨티나":"아르헨티나중앙은행 기준금리", "인도네시아":"인도네시아 기준금리"}

  
