"""
command:
streamlit run streamlit.py

http://192.168.2.186:8501/
"""
import asyncio
from asyncio import run_coroutine_threadsafe
from threading import Thread
import os
import sys
import streamlit as st
import requests
import random
import time
from streamlit_chat import message
from langserve import RemoteRunnable
from pprint import pprint
import json
import io
from functools import reduce
from run.run import RUN
import streamlit as st
import requests
import json
import asyncio
import io
import aiohttp


import streamlit as st
import requests

async def streamlit_app(args):
    st.markdown("""
    <style>
    .small-font {
        font-size:12px !important;
        color:gray;
        margin-top: 0%;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown(""":orange[**Law | Finance | Ai | Conversation | Web search**]""", 
                unsafe_allow_html=True)

    user_input = st.text_input("검색어를 입력하세요:", "")

    if st.button("Enter"):
        with st.spinner("Searching for information..."):
            text_placeholder = st.empty()
            full_text=""
            for chunk in RUN(args).run(user_input):
                if chunk:
                    try:
                        full_text += chunk
                        text_placeholder.markdown(full_text + "▌")
                        buffer = b""
                    except UnicodeDecodeError:
                        continue
            text_placeholder.markdown(full_text)

# if __name__ == "__main__":
#     streamlit_app()
