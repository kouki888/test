import streamlit as st
import pandas as pd
import chardet
import plotly.express as px
from sklearn.preprocessing import LabelEncoder
import google.generativeai as genai
from dotenv import load_dotenv
import os
import io

# ===== 載入 API 金鑰 =====
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("❌ API 金鑰未設定，請確認 .env 檔案或環境變數")
    st.stop()

genai.configure(api_key=API_KEY)

# ===== 頁面設定 =====
st.set_page_config(page_title="Gemini Chat App", page_icon="🤖")

# ===== 側邊欄選單 =====
app_mode = st.sidebar.selectbox("選擇功能模式", ["🤖 Gemini 聊天機器人"])

# ===== Gemini 聊天機器人 =====
if app_mode == "🤖 Gemini 聊天機器人":
    st.title("🤖 Gemini Chatbot")
    st.markdown("請輸入任何問題，Gemini 將會回應你。")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "selected_chat" not in st.session_state:
        st.session_state.selected_chat = None

    user_input = st.text_area("✏️ 你想問 Gemini 什麼？", height=100)

    if st.button("🚀 送出"):
        if user_input.strip() == "":
            st.warning("請輸入問題後再送出。")
        elif len(user_input) > 1000:
            st.warning("⚠️ 輸入過長，請簡化你的問題（最多 1000 字元）。")
        else:
            with st.spinner("Gemini 正在生成回應..."):
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(user_input)
        reply = response.text.strip()

        if not reply:
            st.error("⚠️ 沒有收到 Gemini 的回應，可能是 API 請求逾時或失敗。")
        else:
            # 儲存與顯示
            ...
    except Exception as e:
        st.error(f"❌ 發生錯誤：{e}")


    with st.sidebar:
        st.markdown("---")
        st.header("📂 聊天紀錄")

        for idx, chat in enumerate(st.session_state.chat_history):
            if st.button(chat["title"], key=f"chat_{idx}"):
                st.session_state.selected_chat = idx

        if st.button("🧹 清除聊天紀錄"):
            st.session_state.chat_history = []
            st.session_state.selected_chat = None

    if st.session_state.selected_chat is not None:
        chat = st.session_state.chat_history[st.session_state.selected_chat]
        st.subheader("👤 使用者問題")
        st.info(chat["user_input"])
        st.subheader("🤖 Gemini 回應")
        st.success(chat["response"])
