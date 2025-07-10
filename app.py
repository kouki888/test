import streamlit as st
import pandas as pd
import chardet
import plotly.express as px
from sklearn.preprocessing import LabelEncoder
import google.generativeai as genai
from dotenv import load_dotenv
import os
import io

# ========== 載入 API 金鑰 ==========
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("❌ API 金鑰未設定，請確認 .env 檔案或環境變數")
    st.stop()

genai.configure(api_key=API_KEY)

# ========== 頁面設定 ==========
st.set_page_config(page_title="多功能應用工具", page_icon="🧰", layout="wide")

# ========== 側邊欄選單 ==========
st.sidebar.title("🧰 多功能選單")
app_mode = st.sidebar.selectbox("請選擇功能", ["🤖 Gemini 聊天機器人", "📊 資料集分析工具"])

# ========== Gemini 聊天機器人 ==========
if app_mode == "🤖 Gemini 聊天機器人":
    st.title("🤖 Gemini Chatbot")
    st.markdown("請輸入任何問題，Gemini 將會回應你。")

    # 初始化聊天狀態
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "selected_chat" not in st.session_state:
        st.session_state.selected_chat = None

    # 使用者輸入
    user_input = st.text_area("✏️ 你想問 Gemini 什麼？", height=100)

    if st.button("🚀 送出"):
        if user_input.strip() == "":
            st.warning("請輸入問題後再送出。")
        elif len(user_input) > 1000:
            st.warning("⚠️ 輸入過長，請簡化你的問題（最多 1000 字元）。")
        else:
            with st.spinner("Gemini 正在生成回應..."):
                try:
                    model = genai.GenerativeModel("models/gemini-2.0-flash")
                    response = model.generate_content(user_input)
                    reply = response.text.strip()

                    # 自動產生主題
                    title_prompt = f"請用不超過10個中文字為以下內容取一個簡短主題：\n{user_input}"
                    title_resp = model.generate_content(title_prompt)
                    title = title_resp.text.strip().split("\n")[0]

                    st.session_state.chat_history.append({
                        "title": title,
                        "user_input": user_input,
                        "response": reply
                    })
                    st.session_state.selected_chat = len(st.session_state.chat_history) - 1

                except Exception as e:
                    st.error(f"❌ 發生錯誤：{e}")

    # 聊天主題紀錄
    with st.sidebar:
        st.markdown("---")
        st.header("🗂️ 聊天紀錄")
        for idx, chat in enumerate(st.session_state.chat_history):
            if st.button(chat["title"], key=f"chat_{idx}"):
                st.session_state.selected_chat = idx
        if st.button("🧹 清除所有聊天紀錄"):
            st.session_state.chat_history = []
            st.session_state.selected_chat = None

    # 顯示聊天內容
    if st.session_state.selected_chat is not None:
        chat = st.session_state.chat_history[st.session_state.selected_chat]
        st.subheader("👤 使用者問題")
        st.info(chat["user_input"])
        st.subheader("🤖 Gemini 回應")
        st.success(chat["response"])

# ========== 資料集分析工具 ==========
elif app_mode == "📊 資料集分析工具":
    st.title("📁 公開資料集上傳與分析")
    st.markdown("上傳一個 Kaggle 或其他來源的 `.csv` 檔案，進行資料預覽與簡易分析。")

    with st.sidebar:
        st.header("🔧 分析設定")
        theme = st.selectbox("🎨 選擇主題色", ["淺色", "深色"], key="theme_select")
        show_preview = st.checkbox("顯示資料預覽", value=True)
        num_rows = st.slider("顯示幾列資料", min_value=5, max_value=100, value=10)

    # 主題樣式
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

    # 上傳檔案
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
