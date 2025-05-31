import streamlit as st
import pandas as pd
from PIL import Image

# ====== 頁面設定 ======
st.set_page_config(page_title="📊 資料集分析工具", page_icon="📁", layout="wide")

# ====== 🔒 主題選單區（樣式保持預設） ======
with st.sidebar:
    st.header("🔧 設定選單")
    
    # 包裹住 selectbox 區塊，方便指定不被主題樣式改變
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
        h1, h2, h3, h4, h5, h6, p, label, span, div {
            color: white !important;
        }
        .dataframe th, .dataframe td {
            color: white !important;
        }

        /* 🌟 保持主題選單樣式不變：白底黑字 */
        .theme-select-box .stSelectbox {
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
        .theme-select-box [data-baseweb="select"] div {
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
    # 淺色主題樣式（使用預設樣式即可，也可以客製）
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
st
