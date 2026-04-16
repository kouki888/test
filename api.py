import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

# ===== 載入 API 金鑰 =====
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("❌ API 金鑰未設定")
    st.stop()

genai.configure(api_key=API_KEY)

# ===== 初始化 session =====
if "conversations" not in st.session_state:
    st.session_state.conversations = {}

if "topic_ids" not in st.session_state:
    st.session_state.topic_ids = []

if "current_topic" not in st.session_state:
    st.session_state.current_topic = "new"

# ===== 頁面 =====
st.set_page_config(page_title="法律AI分析系統", page_icon="⚖️")

st.title("⚖️ 法律情境分析系統（Gemini AI）")

# ===== 使用者輸入 =====
user_input = st.text_area("📌 請輸入案件情境", height=120)

# ===== 分析按鈕 =====
if st.button("🔍 開始分析"):

    if user_input.strip() == "":
        st.warning("請輸入情境")
    else:
        with st.spinner("AI分析中..."):
            try:
                model = genai.GenerativeModel("models/gemini-1.5-flash")

                # ⭐ 核心：法律分析 Prompt
                prompt = f"""
你是一位台灣法律專家，請分析以下案件：

【案件】
{user_input}

請用以下格式回答（一定要照格式）：

【可能涉及罪名】
- （列出罪名）

【法律依據】
- （列出法條）

【構成要件分析】
- （說明為什麼成立）

【可能責任】
- （刑責或民事責任）
"""

                response = model.generate_content(prompt)
                reply = response.text

                # ===== 存成對話 =====
                topic_id = len(st.session_state.topic_ids)
                st.session_state.topic_ids.append(topic_id)

                st.session_state.conversations[topic_id] = {
                    "title": user_input[:10],
                    "content": reply
                }

                st.session_state.current_topic = topic_id

            except Exception as e:
                st.error(f"錯誤：{e}")

# ===== 顯示分析結果 =====
if st.session_state.current_topic != "new":
    data = st.session_state.conversations[st.session_state.current_topic]

    st.markdown("---")
    st.subheader(f"📂 主題：{data['title']}")
    st.write(data["content"])

# ===== 側邊欄 =====
with st.sidebar:
    st.header("🗂️ 案件紀錄")

    if st.button("🆕 新分析"):
        st.session_state.current_topic = "new"

    for tid in st.session_state.topic_ids:
        title = st.session_state.conversations[tid]["title"]
        label = f"✔️ {title}" if tid == st.session_state.current_topic else title

        if st.button(label, key=f"topic_{tid}"):
            st.session_state.current_topic = tid

    st.markdown("---")
    if st.button("🧹 清除紀錄"):
        st.session_state.conversations = {}
        st.session_state.topic_ids = []
        st.session_state.current_topic = "new"
