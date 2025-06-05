import streamlit as st
import pandas as pd
import google.generativeai as genai

# ===== 頁面設定 =====
st.set_page_config(page_title="📊 資料分析 & Gemini 聊天", page_icon="🧠", layout="wide")

# ===== API 金鑰設定 =====
genai.configure(api_key="🔑 請填入你的 Gemini API 金鑰")

# ===== 側邊欄設定 =====
with st.sidebar:
    st.header("💼 工具選單")

    # 功能切換
    selected_page = st.radio("選擇功能頁", ["📊 資料集分析", "🤖 Gemini 聊天機器人"])

    st.markdown("---")
    st.header("🎨 主題設定")
    theme = st.selectbox("選擇主題色", ["淺色", "深色"])

# ===== 主題樣式切換 =====
if theme == "深色":
    st.markdown("""
        <style>
        .stApp { background-color: #000000; color: white; }
        section[data-testid="stSidebar"] { background-color: #111111; color: white; }
        .stButton>button { background-color: #444 !important; color: white !important; }
        h1, h2, h3, h4, h5, h6, p, label, span, div { color: white !important; }
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

# ====== 功能頁 1：資料集分析 ======
if selected_page == "📊 資料集分析":
    st.title("📁 公開資料集上傳與分析")
    st.markdown("上傳一個 Kaggle 或其他來源的 `.csv` 檔案，進行資料預覽與簡易分析。")

    uploaded_file = st.file_uploader("📤 上傳你的 CSV 檔案", type=["csv"])
    show_preview = st.checkbox("顯示資料預覽", value=True)
    num_rows = st.slider("顯示幾列資料", min_value=5, max_value=100, value=10)

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
                st.warning("📌 資料內容目前已被隱藏。請勾選『顯示資料預覽』查看。")
        except Exception as e:
            st.error(f"❌ 發生錯誤：{e}")
    else:
        st.info("請先上傳一個 CSV 檔案")

# ====== 功能頁 2：Gemini 聊天機器人 ======
elif selected_page == "🤖 Gemini 聊天機器人":
    st.title("🤖 Gemini Chatbot")
    st.markdown("請輸入任何問題，Gemini 將會回應你。")

    user_input = st.text_area("✏️ 你想問 Gemini 什麼？", height=150)

    if st.button("🚀 送出"):
        if user_input.strip() == "":
            st.warning("請輸入問題後再送出。")
        else:
            with st.spinner("Gemini 正在思考中..."):
                try:
                    model = genai.GenerativeModel("models/gemini-1.5-flash")
                    response = model.generate_content(user_input)
                    st.success("✅ Gemini 回應：")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"❌ 發生錯誤：{e}")
