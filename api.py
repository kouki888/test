import streamlit as st
import pandas as pd
import chardet
import plotly.express as px
from sklearn.preprocessing import LabelEncoder
import google.generativeai as genai
from dotenv import load_dotenv
import os
import io

# ===== 載入 .env 檔案 =====
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# ===== 檢查 API 金鑰是否存在 =====
if not API_KEY:
    st.error("❌ API 金鑰未設定，請確認 .env 檔案中是否包含 GOOGLE_API_KEY")
    st.stop()

# ===== 設定 Gemini API 金鑰 =====
genai.configure(api_key=API_KEY)

# ===== 頁面設定 =====
st.set_page_config(page_title="📊 Gemini Chatbot + Data App", page_icon="🤖")

# ===== 介面說明 =====
st.title("🤖 Gemini Chatbot with Streamlit")
st.markdown("請輸入你的問題，Gemini 將會嘗試回應你。")

# ===== 使用者輸入問題 =====
user_input = st.text_area("✏️ 你想問 Gemini 什麼？", height=150)

# ===== Gemini 回應區 =====
if st.button("🚀 送出問題"):
    if user_input.strip() == "":
        st.warning("請先輸入問題。")
    else:
        with st.spinner("Gemini 正在思考中..."):
            try:
                model = genai.GenerativeModel("models/gemini-1.5-flash")
                response = model.generate_content(user_input)
                st.success("✅ Gemini 回應如下：")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"❌ 發生錯誤：{e}")
