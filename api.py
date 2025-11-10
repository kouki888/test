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

# ===== 初始化 Session State =====
def init_session_state():
    defaults = {
        "chat_history": [],           # 用於顯示主對話紀錄
        "selected_chat": None,        # 當前選中的聊天索引
        "topic_ids": [],              # 主題 ID 清單
        "conversations": {},          # 每個主題的對話內容
        "current_topic": "new"        # 當前主題狀態
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ===== 側邊欄選單 =====
app_mode = st.sidebar.selectbox("選擇功能模式", ["🤖 Gemini 聊天機器人"])

# ===== Gemini 聊天機器人 =====
if app_mode == "🤖 Gemini 聊天機器人":
    st.title("🤖 Gemini Chatbot")
    st.markdown("請輸入任何問題，Gemini 將會回應你。")

    # ===== 使用者輸入問題 =====
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
                    model = genai.GenerativeModel("models/gemini-2.0-flash")

                    # 取得 Gemini 回覆
                    response = model.generate_content(user_input)
                    reply = response.text.strip()

                    # 產生簡短主題（限制 10 字內）
                    title_prompt = f"請用不超過10個中文字為以下內容取一個簡短主題：\n{user_input}"
                    title_resp = model.generate_content(title_prompt)
                    title = title_resp.text.strip().split("\n")[0]

                    # 建立新主題 ID
                    new_topic_id = len(st.session_state.topic_ids) + 1

                    # 儲存對話紀錄
                    st.session_state.conversations[new_topic_id] = {
                        "title": title,
                        "messages": [
                            {"role": "user", "content": user_input},
                            {"role": "assistant", "content": reply}
                        ]
                    }

                    # 更新主題列表
                    if new_topic_id not in st.session_state.topic_ids:
                        st.session_state.topic_ids.append(new_topic_id)
                    st.session_state.current_topic = new_topic_id

                    # 同步主要聊天紀錄（可省略）
                    st.session_state.chat_history.append({
                        "title": title,
                        "user_input": user_input,
                        "response": reply
                    })

                    st.success("✅ 已新增到聊天紀錄！")

                except Exception as e:
                    st.error(f"❌ 發生錯誤：{e}")

    # ===== 顯示當前對話 =====
    if st.session_state.current_topic != "new":
        current_id = st.session_state.current_topic
        conv = st.session_state.conversations.get(current_id, {})
        if conv:
            st.subheader(f"🗂️ 主題：{conv['title']}")
            for msg in conv["messages"]:
                if msg["role"] == "user":
                    st.markdown(f"**👤 你：** {msg['content']}")
                else:
                    st.markdown(f"**🤖 Gemini：** {msg['content']}")

# ====== 側邊欄：聊天主題清單（使用按鈕）======
with st.sidebar:
    st.markdown("---")
    st.header("🗂️ 聊天紀錄")

    # 新對話按鈕
    if st.button("🆕 新對話", key="new_topic_btn"):
        st.session_state.current_topic = "new"

    # 顯示所有主題按鈕
    if len(st.session_state.topic_ids) == 0:
        st.info("尚無聊天紀錄。")
    else:
        for tid in st.session_state.topic_ids:
            title = st.session_state.conversations[tid]["title"]
            button_label = f"✔️ {title}" if tid == st.session_state.current_topic else title
            if st.button(button_label, key=f"topic_{tid}"):
                st.session_state.current_topic = tid

    # 清除所有聊天
    st.markdown("---")
    if st.button("🧹 清除所有聊天紀錄"):
        st.session_state.conversations = {}
        st.session_state.topic_ids = []
        st.session_state.current_topic = "new"
        st.session_state.chat_history = []
        st.success("✅ 所有聊天已清除！")
