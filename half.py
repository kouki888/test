import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# ====== 頁面設定 ======
st.set_page_config(page_title="📊 資料集分析工具", page_icon="📁", layout="wide")

# ====== 🔒 側邊選單 ======
with st.sidebar:
    st.header("🔧 設定選單")

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
        .stApp { background-color: #000000; color: white; }
        section[data-testid="stSidebar"] { background-color: #111111; color: white; }
        h1, h2, h3, h4, h5, h6, p { color: white !important; }
        .dataframe th, .dataframe td { color: white !important; }
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
        .theme-select-box [data-baseweb="select"],
        .theme-select-box [data-baseweb="select"] * {
            background-color: white !important;
            color: black !important;
        }
        .theme-select-box [data-baseweb="select"] div:hover {
            background-color: #f0f0f0 !important;
            color: black !important;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp { background-color: #ffffff; color: black; }
        section[data-testid="stSidebar"] { background-color: #f0f2f6; color: black; }
        </style>
    """, unsafe_allow_html=True)

# ====== 主頁面內容 ======
st.title("📁 公開資料集上傳與分析")
st.markdown("上傳一個 Kaggle 或其他來源的 `.csv` 檔案，進行資料預覽與簡易分析。")

# ====== 上傳檔案 ======
uploaded_file = st.file_uploader("📤 上傳你的 CSV 檔案", type=["csv"])

# ====== 資料處理與顯示 ======
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ 成功載入資料！")

        if show_preview:
            tab1, tab2, tab3, tab4 = st.tabs(["🔍 資料預覽", "📊 敘述統計", "🧩 欄位篩選", "📈 圖表分析"])

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

            with tab4:
                st.subheader("📈 圖表分析工具")
                chart_type = st.selectbox("請選擇圖表類型", ["長條圖（Bar Chart）", "散佈圖（Scatter Plot）"])

                numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
                category_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

                if not numeric_cols:
                    st.warning("❗ 資料中沒有數值欄位可用於圖表分析。")
                else:
                    y_axis = st.selectbox("選擇數值欄位（Y軸）", numeric_cols)

                    if chart_type == "長條圖（Bar Chart）":
                        if not category_cols:
                            st.warning("❗ 資料中沒有類別欄位可用作 X 軸。")
                        else:
                            x_axis = st.selectbox("選擇分類欄位（X軸）", category_cols)
                            chart_df = df.groupby(x_axis)[y_axis].mean().reset_index()
                            st.plotly_chart(
                                px.bar(chart_df, x=x_axis, y=y_axis, title=f"{x_axis} vs {y_axis} 平均值"),
                                use_container_width=True
                            )

                    elif chart_type == "散佈圖（Scatter Plot）":
                        x_axis = st.selectbox("選擇數值欄位（X軸）", numeric_cols, index=0)
                        color_col = st.selectbox("選擇分類欄位（顏色分組）", category_cols) if category_cols else None

                        st.plotly_chart(
                            px.scatter(df, x=x_axis, y=y_axis, color=color_col, title=f"{x_axis} vs {y_axis} 散佈圖"),
                            use_container_width=True
                        )
        else:
            st.warning("📌 資料內容目前已被隱藏。請在左側勾選『顯示資料預覽』查看資料。")

    except Exception as e:
        st.error(f"❌ 錯誤：無法讀取檔案，請確認格式正確。\n\n{e}")
else:
    st.warning("📌 請上傳一個 `.csv` 檔案。")
