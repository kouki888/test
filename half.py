import streamlit as st
import requests
import math
from streamlit.components.v1 import html
import google.generativeai as genai
import os
from dotenv import load_dotenv

# ===============================
# 環境變數
# ===============================
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    st.error("❌ 請先設定環境變數 GEMINI_API_KEY")
    st.stop()
genai.configure(api_key=GEMINI_KEY)

# ===============================
# Google Places 類型
# ===============================
PLACE_TYPES = {
    "教育": {
        "圖書館": "library",
        "幼兒園": "preschool",
        "小學": "primary_school",
        "學校": "school",
        "中學": "secondary_school",
        "大學": "university",
    },
    "健康與保健": {
        "牙醫": "dentist",
        "醫師": "doctor",
        "藥局": "pharmacy",
        "醫院": "hospital",
    },
    "購物": {
        "便利商店": "convenience_store",
        "超市": "supermarket",
        "百貨公司": "department_store",
    },
    "交通運輸": {
        "公車站": "bus_station",
        "地鐵站": "subway_station",
        "火車站": "train_station",
    },
    "餐飲": {
        "餐廳": "restaurant"
    }
}

# ===============================
# 工具函式
# ===============================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def geocode_address(address, api_key):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key, "language": "zh-TW"}
    res = requests.get(url, params=params).json()
    if res.get("status") == "OK":
        loc = res["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]
    return None, None

def search_category(address, category, radius, api_key):
    lat, lng = geocode_address(address, api_key)
    if not lat:
        return []

    all_places = []
    for sub_type, place_type in PLACE_TYPES[category].items():
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": place_type,
            "key": api_key,
            "language": "zh-TW"
        }
        res = requests.get(url, params=params).json()
        for p in res.get("results", []):
            name = p.get("name", "未命名")
            p_lat = p["geometry"]["location"]["lat"]
            p_lng = p["geometry"]["location"]["lng"]
            dist = int(haversine(lat, lng, p_lat, p_lng))
            all_places.append((sub_type, name, p_lat, p_lng, dist))

    all_places.sort(key=lambda x: x[4])
    return all_places

def format_places(address, places_list):
    lines = [f"房屋（{address}）周邊生活機能："]
    if not places_list:
        lines.append("- 該範圍內無相關地點。")
    else:
        counter = {}
        for t, name, _, _, _ in places_list:
            counter[t] = counter.get(t, 0) + 1
        for k, v in counter.items():
            lines.append(f"- {k}: {v} 個")
    return "\n".join(lines)

# ===============================
# Streamlit UI
# ===============================
st.title("🏠 房屋周邊生活機能比較 + 💬 Gemini 分析")

google_api_key = st.text_input("輸入 Google Maps API Key", type="password")
radius = st.select_slider("搜尋半徑 (公尺)", [200, 400, 600, 1000], value=400)

col1, col2 = st.columns(2)
with col1:
    addr_a = st.text_input("輸入房屋 A 地址")
with col2:
    addr_b = st.text_input("輸入房屋 B 地址")

st.write("### 點擊分類按鈕來選擇要比較的生活機能")
selected_category = st.radio("分類", list(PLACE_TYPES.keys()))

if st.button("比較房屋"):
    if not google_api_key or not addr_a or not addr_b:
        st.warning("請先輸入 Google Maps API Key 和兩個地址")
        st.stop()

    # 搜尋兩個房屋的周邊資料
    places_a = search_category(addr_a, selected_category, radius, google_api_key)
    places_b = search_category(addr_b, selected_category, radius, google_api_key)

    # 顯示地點列表
    st.subheader(f"🏡 {addr_a} - {selected_category}")
    if not places_a:
        st.write("該範圍內無相關地點。")
    else:
        for t, name, _, _, dist in places_a:
            st.write(f"**{t}** - {name} ({dist} 公尺)")

    st.subheader(f"🏡 {addr_b} - {selected_category}")
    if not places_b:
        st.write("該範圍內無相關地點。")
    else:
        for t, name, _, _, dist in places_b:
            st.write(f"**{t}** - {name} ({dist} 公尺)")

    # 整理給 Gemini 的文字
    text_a = format_places(addr_a, places_a)
    text_b = format_places(addr_b, places_b)

    prompt = f"""
你是一位房地產分析專家，請比較以下兩間房屋的生活機能。
請列出優點與缺點，最後做總結：
{text_a}
{text_b}
"""
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    st.subheader("📊 Gemini 分析結果")
    st.write(response.text)
