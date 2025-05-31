import streamlit as st
import pandas as pd
from PIL import Image

# ====== 頁面設定 ======
st.set_page_config(page_title="📊 資料集分析工具", page_icon="📁", layout="wide")

# ====== 🔒 主題選單區塊（樣式保持白底黑字） ======
with st.sidebar:
    st.header("🔧 設定選單")

    # 用 container 包住 selectbox，加上自定 class 名稱
    with st.container():
        st.markdown('<div class="theme-select-box">', unsafe_allow_html=True)
        theme = st.selectbox("🎨 選擇主題色", ["淺色", "深色"], key="theme_select")
        st.markdown('</div>', unsafe_allow_html=True)

    show_preview = st.checkbox("顯示資料預覽", value=True)
    num_rows = st.slider("顯示幾列資料", min_value=5, max_value=100, value=10)
    st.markdown("---")
    st.info("請上傳 CSV 檔案。")

# ====== 主題樣式切換 ======
if theme == "深色":
    st.markdown("""
        <style>
        .stApp {
            background-color: #000000;
            color: white;
        }
        section[data-testid="stSidebar"] {
            background-color: #111111;
            color: white;
        }
        h1, h2, h3, h4, h5, h6, p,label, span {
            color: white !important;
        }
        .dataframe th, .dataframe td {
            color: white !important;
        }

        /* 🌟 保持主題選單樣式為白底黑字 */
        .theme-select-box .stSelectbox,
        .theme-select-box .stSelectbox > div {
            background-color: white !important;
            color: black !important;
            border: 1px solid #ddd !important;
            border-radius: 5px !important;
        }

        .theme-select-box label {
            color: black !important;
        }

        .theme-select-box [data-baseweb="select"] {
            background-color: white !important;
            color: black !important;
        }

        .theme-select-box [data-baseweb="select"] * {
            color: black !important;
            background-color: white !important;
        }

        .theme-select-box [data-baseweb="select"] div:hover {
            background-color: #f0f0f0 !important;
            color: black !important;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    # 淺色主題樣式（預設）
    st.markdown("""
        <style>
        .stApp {
            background-color: #ffffff;
            color: black;
        }
        section[data-testid="stSidebar"] {
            background-color: #f0f2f6;
            color: black;
        }
        </style>
    """, unsafe_allow_html=True)

# ====== 主頁面內容 ======
st.title("📁 公開資料集上傳與分析")
st.markdown("上傳一個 Kaggle 或其他來源的 `.csv` 檔案，進行資料預覽與簡易分析。")

# ====== 上傳檔案 ======
uploaded_file = st.file_uploader("📤 上傳你的 CSV 檔案", type=["csv"])

# ====== 資料處理區 ======
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ 成功載入資料！")

        # 建立分頁
        tab1, tab2, tab3 = st.tabs(["🔍 資料預覽", "📊 敘述統計", "🧩 欄位篩選"])

        with tab1:
            if show_preview:
                st.subheader("🔍 預覽前幾列")
                st.dataframe(df.head(num_rows), use_container_width=True)

        with tab2:
            st.subheader("📊 資料敘述統計")
            st.write(df.describe())

        with tab3:
            st.subheader("🧩 欄位篩選器")
            column = st.selectbox("請選擇要顯示的欄位", df.columns)
            st.dataframe(df[[column]].head(num_rows), use_container_width=True)

    except Exception as e:
        st.error(f"❌ 錯誤：無法讀取檔案，請確認格式正確。\n\n{e}")
else:
    st.warning("📌 請上傳一個 `.csv` 檔案。")
