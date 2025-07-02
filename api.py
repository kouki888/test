import streamlit as st
import pandas as pd
import chardet
import plotly.express as px
from sklearn.preprocessing import LabelEncoder
import google.generativeai as genai
from dotenv import load_dotenv
import os
import io

# 讀取 .env 檔案
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# 檢查 API KEY
if not API_KEY:
    st.error("API 金鑰未設定，請確認 .env 檔案或環境變數")
    st.stop()

# 設定 Gemini API
genai.configure(api_key=API_KEY)

# 初始化 Session State
if 'df_raw_dict' not in st.session_state:
    st.session_state['df_raw_dict'] = {}
if 'df_dict' not in st.session_state:
    st.session_state['df_dict'] = {}
if 'corr_dict' not in st.session_state:
    st.session_state['corr_dict'] = {}
if 'has_data' not in st.session_state:
    st.session_state['has_data'] = False
t.header("Gemini")
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    chat = genai.ChatSession(model=model)

    user_input = st.text_input("請輸入問題")
    if user_input:
        response = chat.send_message(user_input)
        st.markdown(f"Gemini 回答: {response.text}")
