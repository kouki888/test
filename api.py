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

    # ====== 初始化狀態 ======
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "selected_chat" not in st.session_state:
        st.session_state.selected_chat = None

    # ====== 顯示過去主題 ======
    titles = [chat["title"] for chat in st.session_state.chat_history]
    if titles:
        selected_title = st.selectbox("🗂 過去對話紀錄", titles[::-1])  # 反向顯示最新的在上面
        index = len(titles) - 1 - titles[::-1].index(selected_title)
        st.markdown(f"**你問：** {st.session_state.chat_history[index]['user_input']}")
        st.markdown(f"**Gemini 回應：** {st.session_state.chat_history[index]['response']}")

    # ====== 使用者輸入 ======
    user_input = st.text_area("✏️ 你想問 Gemini 什麼？", height=100)

    if st.button("🚀 送出"):
        if user_input.strip() == "":
            st.warning("請輸入問題後再送出。")
        elif len(user_input) > 1000:
            st.warning("⚠️ 輸入過長，請簡化你的問題（最多 1000 字元）。")
        else:
            with st.spinner("Gemini 正在生成回應..."):
                try:
                    # 建立模型並回應
                    model = genai.GenerativeModel("models/gemini-1.5-flash")
                    response = model.generate_content(user_input)
                    reply = response.text.strip()

                    # 自動生成主題
                    title_prompt = f"請用不超過10個中文字為以下內容取一個簡短主題：\n{user_input}"
                    try:
                        title_resp = model.generate_content(title_prompt)
                        title = title_resp.text.strip().split("\n")[0]
                        if len(title) > 10:
                            title = title[:10]
                    except:
                        title = "未命名主題"

                    # 儲存對話
                    st.session_state.chat_history.append({
                        "title": title,
                        "user_input": user_input,
                        "response": reply
                    })
                    st.session_state.selected_chat = len(st.session_state.chat_history) - 1

                    # 顯示回應
                    st.success("✅ Gemini 回應：")
                    st.markdown(reply)

                except Exception as e:
                    st.error(f"❌ 發生錯誤：{e}")
