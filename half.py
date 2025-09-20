import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import google.generativeai as genai

# ===============================
# 假設的輔助函數（請替換成你的實作）
# ===============================
def geocode_address(address, google_key):
    """將地址轉換成經緯度（請替換成你的 geocoding 實作）"""
    # TODO: 這裡換成你的 geocoding API
    return 25.0330, 121.5654  # 台北 101 當作示範

def query_google_places_by_type(lat, lng, google_key, categories, radius=500):
    """查詢 Google Places API（請替換成你的實作）"""
    # TODO: 這裡回傳模擬的生活機能資料
    return [{"name": "便利商店", "lat": lat+0.001, "lng": lng+0.001, "type": "便利商店"}]

def add_markers(map_obj, places, color):
    """在 folium 地圖上加上標記"""
    for p in places:
        folium.Marker(
            [p["lat"], p["lng"]],
            popup=p["name"],
            icon=folium.Icon(color=color, icon="info-sign")
        ).add_to(map_obj)

def format_info(address, info):
    """格式化房屋與生活機能資訊"""
    details = [f"- {p['type']}：{p['name']}" for p in info]
    return f"📍 地址：{address}\n" + "\n".join(details)


# ===============================
# API Key 輸入框
# ===============================
st.sidebar.header("🔑 API 設定")

google_key = st.sidebar.text_input("Google Maps API Key", type="password")
gemini_key = st.sidebar.text_input("Gemini API Key", type="password")

if google_key:
    st.session_state["google_key"] = google_key
if gemini_key:
    st.session_state["gemini_key"] = gemini_key
    genai.configure(api_key=gemini_key)


# ===============================
# 模擬收藏清單資料
# ===============================
if "saved_properties" not in st.session_state:
    st.session_state.saved_properties = [
        {"id": "A001", "name": "信義區豪宅", "address": "台北市信義路五段7號"},
        {"id": "B002", "name": "大安區電梯大樓", "address": "台北市大安路一段100號"},
        {"id": "C003", "name": "中山區景觀宅", "address": "台北市中山北路二段45號"}
    ]

PLACE_TYPES_COMPARE = {
    "便利商店": "convenience_store",
    "學校": "school",
    "醫院": "hospital",
    "餐廳": "restaurant",
    "大眾運輸": "transit_station",
    "購物中心": "shopping_mall"
}

# ===============================
# Streamlit 主畫面
# ===============================
st.title("🏠 房屋比較與分析")

# 確認是否有收藏
if not st.session_state.saved_properties:
    st.warning("⚠️ 尚未收藏任何房屋，請先到【收藏房屋】頁面新增。")
    st.stop()

# 從收藏清單選擇
prop_names = [f"{p['name']} - {p['address']}" for p in st.session_state.saved_properties]
col1, col2 = st.columns(2)
with col1:
    selected_a = st.selectbox("選擇房屋 A", prop_names, key="compare_a")
with col2:
    selected_b = st.selectbox("選擇房屋 B", prop_names, key="compare_b")

# 半徑選擇
radius = st.slider("搜尋半徑 (公尺)", min_value=100, max_value=2000, value=500, step=50)

# 生活機能類別
st.subheader("選擇要比較的生活機能類別")
selected_categories = []
cols = st.columns(3)
for idx, cat in enumerate(PLACE_TYPES_COMPARE.keys()):
    if cols[idx % 3].checkbox(cat, value=True):
        selected_categories.append(cat)

# 比較按鈕
if st.button("開始比較", use_container_width=True):
    if selected_a == selected_b:
        st.warning("⚠️ 請選擇不同的房屋來比較")
        st.stop()
    if not selected_categories:
        st.warning("⚠️ 請至少選擇一個類別")
        st.stop()
    if "google_key" not in st.session_state or not st.session_state.google_key:
        st.error("❌ 請先輸入 Google Maps API Key")
        st.stop()
    if "gemini_key" not in st.session_state or not st.session_state.gemini_key:
        st.error("❌ 請先輸入 Gemini API Key")
        st.stop()

    with st.spinner("正在查詢並分析..."):
        # 取出地址
        addr_a = st.session_state.saved_properties[prop_names.index(selected_a)]["address"]
        addr_b = st.session_state.saved_properties[prop_names.index(selected_b)]["address"]

        # 地址轉經緯度
        lat_a, lng_a = geocode_address(addr_a, st.session_state.google_key)
        lat_b, lng_b = geocode_address(addr_b, st.session_state.google_key)

        if not lat_a or not lat_b:
            st.error("❌ 無法解析其中一個地址，請檢查是否正確")
            st.stop()

        # 查詢周邊生活機能
        info_a = query_google_places_by_type(lat_a, lng_a, st.session_state.google_key, selected_categories, radius=radius)
        info_b = query_google_places_by_type(lat_b, lng_b, st.session_state.google_key, selected_categories, radius=radius)

        text_a = format_info(addr_a, info_a)
        text_b = format_info(addr_b, info_b)

        # 地圖顯示
        st.subheader("📍 房屋 A 周邊地圖")
        m_a = folium.Map(location=[lat_a, lng_a], zoom_start=15)
        folium.Marker([lat_a, lng_a], popup=f"房屋 A：{addr_a}", icon=folium.Icon(color="red", icon="home")).add_to(m_a)
        add_markers(m_a, info_a, "red")
        st_folium(m_a, width=700, height=400)

        st.subheader("📍 房屋 B 周邊地圖")
        m_b = folium.Map(location=[lat_b, lng_b], zoom_start=15)
        folium.Marker([lat_b, lng_b], popup=f"房屋 B：{addr_b}", icon=folium.Icon(color="blue", icon="home")).add_to(m_b)
        add_markers(m_b, info_b, "blue")
        st_folium(m_b, width=700, height=400)

        # Gemini 分析
        prompt = f"""你是一位房地產分析專家，請比較以下兩間房屋的生活機能，
        並列出優缺點與結論：
        {text_a}
        {text_b}
        """
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        result_text = response.text if hasattr(response, "text") else response.candidates[0].content.parts[0].text

        st.subheader("📊 Gemini 分析結果")
        st.markdown(result_text)

        # 側邊欄對照表
        st.sidebar.subheader("🏠 房屋資訊對照表")
        st.sidebar.write("### 房屋 A")
        st.sidebar.markdown(text_a)
        st.sidebar.markdown("---")
        st.sidebar.write("### 房屋 B")
        st.sidebar.markdown(text_b)
