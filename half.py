import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import google.generativeai as genai
import requests
import math
from streamlit.components.v1 import html

# ===============================
# Google Places 類別
# ===============================
PLACE_TYPES_COMPARE = {
    "交通": ["bus_stop", "subway_station", "train_station"],
    "超商": ["convenience_store"],
    "餐廳": ["restaurant", "cafe"],
    "學校": ["school", "university", "primary_school", "secondary_school"],
    "醫院": ["hospital"],
    "藥局": ["pharmacy"],
}

# ===============================
# 工具函式
# ===============================
def geocode_address(address: str, api_key: str):
    """將地址轉換為經緯度"""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key, "language": "zh-TW"}
    r = requests.get(url, params=params, timeout=10).json()
    if r.get("status") == "OK" and r["results"]:
        loc = r["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]
    return None, None

def haversine(lat1, lon1, lat2, lon2):
    """計算兩點間的球面距離（公尺）"""
    R = 6371000
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def query_google_places_by_type(lat, lng, api_key, selected_categories, radius=500):
    """根據 Places API 的 type 參數查詢（房屋比較用）"""
    results = {k: [] for k in selected_categories}
    for label in selected_categories:
        for t in PLACE_TYPES_COMPARE[label]:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": radius,
                "type": t,
                "language": "zh-TW",
                "key": api_key,
            }
            r = requests.get(url, params=params, timeout=10).json()
            for place in r.get("results", []):
                name = place.get("name", "未命名")
                p_lat = place["geometry"]["location"]["lat"]
                p_lng = place["geometry"]["location"]["lng"]
                dist = int(haversine(lat, lng, p_lat, p_lng))
                results[label].append((name, p_lat, p_lng, dist))
    return results

def format_info(address, info_dict):
    """將查詢結果格式化為文字"""
    lines = [f"房屋（{address}）："]
    for k, v in info_dict.items():
        lines.append(f"- {k}: {len(v)} 個")
    return "\n".join(lines)

def add_markers(m, info_dict, color):
    """在 Folium 地圖上添加標記"""
    for category, places in info_dict.items():
        for name, lat, lng, dist in places:
            folium.Marker(
                [lat, lng],
                popup=f"{category}：{name}（{dist} 公尺）",
                icon=folium.Icon(color=color, icon="info-sign"),
            ).add_to(m)

# ===============================
# Streamlit 介面
# ===============================
st.set_page_config(layout="wide", page_title="🏠 房屋生活機能比較")

st.title("🏠 房屋生活機能比較與分析")

# API Key 輸入區（採用新版）
with st.sidebar:
    st.header("🔑 API Key 設定")
    google_key = st.text_input("Google Maps API Key", type="password")
    gemini_key = st.text_input("Gemini API Key", type="password")

if not google_key or not gemini_key:
    st.info("請先在左側欄位輸入 Google Maps 與 Gemini API Key")
    st.stop()
else:
    genai.configure(api_key=gemini_key)

# 模擬收藏清單資料
if "saved_properties" not in st.session_state:
    st.session_state.saved_properties = [
        {"id": "A001", "name": "信義區豪宅", "address": "台北市信義路五段7號"},
        {"id": "B002", "name": "大安區電梯大樓", "address": "台北市大安路一段100號"},
        {"id": "C003", "name": "中山區景觀宅", "address": "台北市中山北路二段45號"}
    ]

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

    with st.spinner("正在查詢並分析..."):
        addr_a = st.session_state.saved_properties[prop_names.index(selected_a)]["address"]
        addr_b = st.session_state.saved_properties[prop_names.index(selected_b)]["address"]

        lat_a, lng_a = geocode_address(addr_a, google_key)
        lat_b, lng_b = geocode_address(addr_b, google_key)

        if not lat_a or not lat_b:
            st.error("❌ 無法解析其中一個地址，請檢查是否正確")
            st.stop()

        info_a = query_google_places_by_type(lat_a, lng_a, google_key, selected_categories, radius=radius)
        info_b = query_google_places_by_type(lat_b, lng_b, google_key, selected_categories, radius=radius)

        text_a = format_info(addr_a, info_a)
        text_b = format_info(addr_b, info_b)

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

        prompt = f"""你是一位房地產分析專家，請比較以下兩間房屋的生活機能，
        並列出優缺點與結論：
        {text_a}
        {text_b}
        """
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        st.subheader("📊 Gemini 分析結果")
        st.markdown(response.text)

        st.sidebar.subheader("🏠 房屋資訊對照表")
        st.sidebar.markdown(f"**房屋 A**\n{text_a}")
        st.sidebar.markdown(f"**房屋 B**\n{text_b}")
