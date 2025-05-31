import streamlit as st         # 匯入 Streamlit 用來建立 Web 應用介面
import pandas as pd            # 匯入 pandas 用來處理 CSV 資料
from PIL import Image          # 匯入 PIL 套件用來處理圖片（目前程式未使用）

# ====== 頁面設定 ======
st.set_page_config(
    page_title="📊 資料集分析工具",  # 頁籤標題
    page_icon="📁",              # 頁籤的小圖示
    layout="wide"               # 使用寬版版面
)

# ====== 🔒 主題選單設定區塊（樣式保持預設） ======
with st.sidebar:  # 側邊欄開始
    st.header("🔧 設定選單")  # 側邊欄標題

    # 使用容器包住主題選單，這樣可以對主題選單應用特定樣式
    with st.container():
        # HTML 包裹用來套 CSS 樣式
        st.markdown('<div class="theme-select-box">', unsafe_allow_html=True)
        theme = st.selectbox("🎨 選擇主題色", ["淺色", "深色"], key="theme_select")
        st.markdown('</div>', unsafe_allow_html=True)

    # 顯示資料預覽的切換開關
    show_preview = st.checkbox("顯示資料預覽", value=True)

    # 選擇要顯示幾列資料
    num_rows = st.slider("顯示幾列資料", min_value=5, max_value=100, value=10)

    # 分隔線
    st.markdown("---")

    # 上傳提示訊息
    st.info("請上傳 CSV 檔案。")

# ====== 主題樣式切換（淺色／深色） ======
if theme == "深色":
    # 套用黑色主題樣式
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
        .css-1xarl3l {
            background-color: #222222 !important;
        }

        /* 🌟 保持主題選單樣式不變：白底黑字 
        .theme-select-box .stSelectbox {
            background-color: white !important;
            color: black !important;
            border: 1px solid #ddd !important;
            border-radius: 5px !important;
        }
        .theme-select-box label {
            color: black !important;
        }
        .theme-select-box .stSelectbox div[data-baseweb="select"] {
            background-color: white !important;
            color: black !important;
        }*/
        </style>
    """, unsafe_allow_html=True)
else:
    # 套用白色主題樣式
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

# ====== 主頁面內容區塊 ======
st.title("📁 公開資料集上傳與分析")  # 主標題
st.markdown("上傳一個 Kaggle 或其他來源的 `.csv` 檔案，進行資料預覽與簡易分析。")  # 說明文字

# ====== 上傳 CSV 檔案 ======
uploaded_file = st.file_uploader("📤 上傳你的 CSV 檔案", type=["csv"])

# ====== 資料處理與顯示區 ======
if uploaded_file:  # 如果使用者有上傳檔案
    try:
        df = pd.read_csv(uploaded_file)  # 讀取 CSV 檔案
        st.success("✅ 成功載入資料！")  # 顯示成功訊息

        # 建立三個頁籤
        tab1, tab2, tab3 = st.tabs(["🔍 資料預覽", "📊 敘述統計", "🧩 欄位篩選器"])

        # 頁籤一：預覽資料
        with tab1:
            if show_preview:
                st.subheader("🔍 預覽前幾列")
                st.dataframe(df.head(num_rows), use_container_width=True)

        # 頁籤二：顯示敘述統計
        with tab2:
            st.subheader("📊 資料敘述統計")
            st.write(df.describe())  # 使用 pandas 的 describe 方法統計摘要

        # 頁籤三：欄位篩選
        with tab3:
            st.subheader("🧩 欄位篩選器")
            column = st.selectbox("請選擇要顯示的欄位", df.columns)  # 下拉選單選欄位
            st.dataframe(df[[column]].head(num_rows), use_container_width=True)  # 顯示選定欄位

    except Exception as e:
        # 如果讀取資料失敗，顯示錯誤訊息
        st.error(f"❌ 錯誤：無法讀取檔案，請確認格式正確。\n\n{e}")
else:
    # 尚未上傳檔案時提示
    st.warning("📌 請上傳一個 `.csv` 檔案。")
