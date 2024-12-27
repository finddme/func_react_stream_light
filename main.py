import os
# os.system("sh /mount/src/func_react_stream_light/setup.sh")

import streamlit as st
import subprocess
import argparse
import six, torch
from app.direct_streamlit import streamlit_app
import asyncio
from utils.doc_search import *
from utils.config import *
import os
from action_agents.search_engine import Blog
from playwright.sync_api import sync_playwright

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
        
        subprocess.run(["playwright", "install", "chrome"], check=True)
        subprocess.run(["playwright", "install", "chromium"], check=True)
        
    except Exception as e:
        st.error(f"Dependencies installation failed: {str(e)}")
             
# install_system_dependencies()
# os.environ['PYTHONPATH'] = os.getcwd()

async def main(args):
    await streamlit_app(args)

# async def main(args):
#     with sync_playwright() as p:
#         browser = p.chromium.launch()
#         await streamlit_app(args)
#         browser.close()

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




    
