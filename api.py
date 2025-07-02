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

app_mode == "🤖 Gemini 聊天機器人":
    st.title("🤖 Gemini Chatbot")
    st.markdown("請輸入任何問題，Gemini 將會回應你。")

    # ====== 初始化聊天狀態 ======
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "selected_chat" not in st.session_state:
        st.session_state.selected_chat = None

    # ====== 使用者輸入問題 ======
    user_input = st.text_area("✏️ 你想問 Gemini 什麼？", height=100)

    if st.button("🚀 送出"):
        if user_input.strip() == "":
            st.warning("請輸入問題後再送出。")
        elif len(user_input) > 1000:
            st.warning("⚠️ 輸入過長，請簡化你的問題（最多 1000 字元）。")
        else:
            with st.spinner("Gemini 正在生成回應..."):
                try:
                    # 建立模型
                    model = genai.GenerativeModel("models/gemini-1.5-flash")

                    # 回應內容
                    response = model.generate_content(user_input)
                    reply = response.text.strip()

                    # 自動產生主題（限制 10 字內）
                    title_prompt = f"請用不超過10個中文字為以下內容取一個簡短主題：\n{user_input}"
                    title_resp = model.generate_content(title_prompt)
                    title = title_resp.text.strip().split("\n")[0]

                    # 加入對話紀錄
                    st.session_state.chat_history.append({
                        "title": title,
                        "user_input": user_input,
                        "response": reply
                    })
                    st.session_state.selected_chat = len(st.session_state.chat_history) - 1

                except Exception as e:
                    st.error(f"❌ 發生錯誤：{e}")
