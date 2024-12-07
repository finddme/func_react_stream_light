"""
command:
streamlit run streamlit_fastapi.py

http://192.168.2.186:8501/
"""
import asyncio
import streamlit as st
import requests
import json
import io
from functools import reduce

async def main():
    # st.title(""":blue[#Function calling #Multi-Agent #ReACT]""")
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

    api_url = "https://fa78-222-233-253-190.ngrok-free.app/chat"

    user_input = st.text_input("검색어를 입력하세요:", "")

    if st.button("Enter"):
        with st.spinner("Searching for information..."):
            text_placeholder = st.empty()

            with requests.post(api_url, json={"user_input": user_input}, stream=True) as response:
                full_text = ""
                buffer = b""
                for chunk in response.iter_content(chunk_size=1):
                    if chunk:
                        buffer += chunk
                        try:
                            chunk_str = buffer.decode('utf-8')
                            full_text += chunk_str
                            text_placeholder.markdown(full_text + "▌")
                            buffer = b""
                        except UnicodeDecodeError:
                            continue

            text_placeholder.markdown(full_text)
    st.image("https://finddme.github.io/public/fc_react.png", caption="search box pipeline")

if __name__ == '__main__':
    asyncio.run(main())

