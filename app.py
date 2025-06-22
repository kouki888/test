import streamlit as st
import pandas as pd
import google.generativeai as genai
from PIL import Image
import requests
import hashlib

# ====== 頁面設定 ======
st.set_page_config(page_title="專題作業一", page_icon="📊", layout="wide")

# ====== API 金鑰設定 ======
genai.configure(api_key="AIzaSyBcTohvzAeRE71-GIfCD9sfFsvYf403h8w")  # 🚨 請替換為你自己的金鑰

# ====== 🔒 側邊欄選單 ======
with st.sidebar:
    st.header("🔧 工具選單")
    app_mode = st.radio("選擇功能頁", ["📊 資料集分析", "🤖 Gemini 聊天機器人"])

    st.markdown("---")
    st.header("🎨 主題設定")
    theme = st.selectbox("選擇主題色", ["淺色", "深色"])

    if app_mode == "📊 資料集分析":
        show_preview = st.checkbox("顯示資料預覽", value=True)
        num_rows = st.slider("顯示幾列資料", min_value=5, max_value=100, value=10)
        st.info("請上傳 CSV 檔案。")

# ====== 主題樣式切換 ======
if theme == "深色":
    st.markdown("""
        <style>
        .stApp { background-color: #000000; color: white; }
        section[data-testid="stSidebar"] { background-color: #111111; color: white; }
        h1, h2, h3, h4, h5, h6, p { color: white !important; }
        .dataframe th, .dataframe td { color: white !important; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp { background-color: #ffffff; color: black; }
        section[data-testid="stSidebar"] { background-color: #f0f2f6; color: black; }
        </style>
    """, unsafe_allow_html=True)

# ====== 功能 1: 資料集分析 ======
if app_mode == "📊 資料集分析":
    st.title("HW.1")
    st.markdown("上傳一個 Kaggle 或其他來源的 `.csv` 檔案，進行資料預覽與簡易分析。")

    uploaded_file = st.file_uploader("📤 上傳你的 CSV 檔案", type=["csv"])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("✅ 成功載入資料！")

            if show_preview:
                tab1, tab2, tab3 = st.tabs(["🔍 資料預覽", "📊 敘述統計", "🧩 欄位篩選"])

                with tab1:
                    st.subheader("🔍 預覽前幾列")
                    st.dataframe(df.head(num_rows), use_container_width=True)

                with tab2:
                    st.subheader("📊 資料敘述統計")
                    st.write(df.describe())

                with tab3:
                    st.subheader("🧩 欄位篩選器")
                    column = st.selectbox("請選擇要顯示的欄位", df.columns)
                    st.dataframe(df[[column]].head(num_rows), use_container_width=True)
            else:
                st.warning("📌 資料內容目前已被隱藏。請在左側勾選『顯示資料預覽』查看資料。")

        except Exception as e:
            st.error(f"❌ 錯誤：無法讀取檔案，請確認格式正確。\n\n{e}")
    else:
        st.warning("📌 請上傳一個 `.csv` 檔案。")

# ====== 功能 2: Gemini 聊天機器人 ======
elif app_mode == "🤖 Gemini 聊天機器人":
    st.title("🤖 Gemini Chatbot")
    st.markdown("請輸入任何問題，Gemini 將回應你，並自動為對話產生主題並加入左側清單。")

    # 初始化聊天記憶
    if "topics" not in st.session_state:
        st.session_state.topics = {}  # { hash_key: chat_obj }
    if "active_topic" not in st.session_state:
        st.session_state.active_topic = None
    if "topic_titles" not in st.session_state:
        st.session_state.topic_titles = {}  # { hash_key: readable_title }

    # 使用者輸入區
    user_input = st.text_input("✏️ 請輸入你的問題")
    submitted = st.button("🚀 送出")

    if submitted and user_input.strip():
        user_input_clean = user_input.strip()
        topic_hash = hashlib.md5(user_input_clean.encode()).hexdigest()
        topic_title = user_input_clean[:20] + "..." if len(user_input_clean) > 20 else user_input_clean

        # 建立或切換主題
        if topic_hash not in st.session_state.topics:
            model = genai.GenerativeModel("models/gemini-1.5-flash")
            chat = model.start_chat(history=[])
            st.session_state.topics[topic_hash] = chat
            st.session_state.topic_titles[topic_hash] = topic_title

        st.session_state.active_topic = topic_hash
        chat = st.session_state.topics[topic_hash]

        # 發送訊息與回覆
        with st.spinner("💬 Gemini 正在思考中..."):
            try:
                response = chat.send_message(user_input_clean, stream=True)
                full_response = ""
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                st.success("✅ Gemini 回應：")
                st.markdown(f"<div style='white-space: pre-wrap;'>{full_response}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ 發生錯誤：{e}")

    # 側邊欄主題選單
    with st.sidebar:
        st.subheader("🗂️ 你的聊天主題")
        for topic_hash, title in st.session_state.topic_titles.items():
            if st.button(title, key=topic_hash):
                st.session_state.active_topic = topic_hash

        if st.button("🧹 清空所有主題"):
            st.session_state.topics = {}
            st.session_state.topic_titles = {}
            st.session_state.active_topic = None
            st.success("✅ 已清空所有主題與對話。")

    # 顯示對話紀錄
    if st.session_state.active_topic:
        chat = st.session_state.topics[st.session_state.active_topic]
        title = st.session_state.topic_titles[st.session_state.active_topic]
        st.markdown(f"### 🧠 主題：**{title}**")
        for msg in chat.history:
            role = msg.role
            text = msg.parts[0].text if msg.parts else ""
            if role == "user":
                st.markdown(f"🧑‍💬 **你：** {text}")
            else:
                st.markdown(f"🤖 **Gemini：** {text}")
