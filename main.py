import os
import streamlit as st
import os
import subprocess
os.system("sh /mount/src/function_calling_react/func_react_stream_light/setup.sh")

def install_system_dependencies():
    try:
        packages = [
            "libnss3", "libnspr4", "libatk1.0-0", "libatk-bridge2.0-0",
            "libcups2", "libdrm2", "libxcomposite1", "libxdamage1",
            "libxfixes3", "libxrandr2", "libgbm1", "libxkbcommon0",
            "libpango-1.0-0", "libcairo2", "libasound2", "libatspi2.0-0"
        ]
        subprocess.run(["apt-get", "update"], check=True)
        subprocess.run(["apt-get", "install", "-y"] + packages, check=True)

        subprocess.run(["playwright", "install", "chromium"], check=True)
    except Exception as e:
        st.error(f"Dependencies installation failed: {str(e)}")
        
# os.system("playwright install")      
# install_system_dependencies()
os.system("pip install crawl4ai")
# os.system("playwright install-deps")
# os.system("npx playwright install-deps --dry-run")
os.system("pip install nest-asyncio")
os.system("crawl4ai-setup")
# os.system("python -m playwright install chromium")
os.system("pip install --upgrade playwright")
os.environ['PYTHONPATH'] = os.getcwd()

async def main(args):
    await streamlit_app(args)

# async def main(args):
#     with sync_playwright() as p:
#         browser = p.chromium.launch()
#         await streamlit_app(args)
#         browser.close()

import argparse
import six, torch
from app.direct_streamlit import streamlit_app
import asyncio
from utils.doc_search import *
from utils.config import *
import os
from action_agents.search_engine import Blog
from playwright.sync_api import sync_playwright

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--defined-action', type=list, nargs='+', 
                        default=["web_search","ai_related_search",
                                "casual_conversation",
                                "financial_market_search"], 
                        choices=["web_search","ai_related_search",
                                "casual_conversation",
                                "financial_market_search"], 
                        required=False)
    parser.add_argument('--llm', type=str, default='together', 
                        choices=["claude","together"], required=False)
    parser.add_argument('--web-cluster-db-update', type=str, default="False", choices=["True","False"], required=False)

    args = parser.parse_args()

    asyncio.run(main(args))




    
