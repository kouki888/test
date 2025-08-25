import streamlit as st
import requests
import folium
import os
from dotenv import load_dotenv
from streamlit_folium import st_folium
import google.generativeai as genai

# ===============================
# 載入環境變數
# ===============================
load_dotenv()
OPENCAGE_KEY = os.getenv("OPENCAGE_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if not OPENCAGE_KEY:
    st.error("❌ 請先設定環境變數 OPENCAGE_API_KEY")
    st.stop()

if not GEMINI_KEY:
    st.error("❌ 請先設定環境變數 GEMINI_API_KEY")
    st.stop()

# 設定 Gemini API
genai.configure(api_key=GEMINI_KEY)

# ===============================
# 支援查詢的 OSM Tags
# ===============================
OSM_TAGS = {
    "交通": '["public_transport"="stop_position"]',
    "超商": '["shop"="convenience"]',
    "餐廳": '["amenity"="restaurant"]',
    "學校": '["amenity"="school"]',
    "醫院": '["amenity"="hospital"]',
    "藥局": '["amenity"="pharmacy"]'
}

# ===============================
# 工具函式
# ===============================
def geocode_address(address: str):
    """利用 OpenCage 把地址轉成經緯度"""
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {"q": address, "key": OPENCAGE_KEY, "language": "zh-TW", "limit": 1}
    try:
        res = requests.get(url, params=params, timeout=10).json()
        if res["results"]:
            return res["results"][0]["geometry"]["lat"], res["results"][0]["geometry"]["lng"]
        else:
            return None, None
    except Exception:
        return None, None


def query_osm(lat, lng):
    """查詢某座標 400 公尺內的地點"""
    results = {}
    for tag_name, tag in OSM_TAGS.items():
        query = f"""
        [out:json];
        (
          node{tag}(around:400,{lat},{lng});
          way{tag}(around:400,{lat},{lng});
          relation{tag}(around:400,{lat},{lng});
        );
        out center;
        """
        try:
            r = requests.post("https://overpass-api.de/api/interpreter", data=query.encode("utf-8"), timeout=20)
            data = r.json()
        except:
            continue

        places = []
        for el in data.get("elements", []):
            if "lat" in el and "lon" in el:
                lat_el, lon_el = el["lat"], el["lon"]
            elif "center" in el:
                lat_el, lon_el = el["center"]["lat"], el["center"]["lon"]
            else:
                continue
            name = el.get("tags", {}).get("name", "未命名")
            places.append(name)
        results[tag_name] = places
    return results


def format_info(address, info_dict):
    """把查詢結果整理成文字"""
    lines = [f"房屋（{address}）："]
    for k, v in info_dict.items():
        if v:
            lines.append(f"- {k}: {len(v)} 個 ({'、'.join(v[:5])}{'…' if len(v) > 5 else ''})")
        else:
            lines.append(f"- {k}: 無")
    return "\n".join(lines)


# ===============================
# Streamlit UI
# ===============================
st.title("🏠 房屋比較助手 (OSM + OpenCage + Gemini)")

col1, col2 = st.columns(2)
with col1:
    addr_a = st.text_input("輸入房屋 A 地址")
with col2:
    addr_b = st.text_input("輸入房屋 B 地址")

if st.button("比較房屋"):
    if not addr_a or not addr_b:
        st.warning("請輸入兩個地址")
        st.stop()

    # 1️⃣ Geocode
    lat_a, lng_a = geocode_address(addr_a)
    lat_b, lng_b = geocode_address(addr_b)
    if not lat_a or not lat_b:
        st.error("❌ 無法解析其中一個地址")
        st.stop()

    # 2️⃣ OSM 查詢
    info_a = query_osm(lat_a, lng_a)
    info_b = query_osm(lat_b, lng_b)

    text_a = format_info(addr_a, info_a)
    text_b = format_info(addr_b, info_b)

    # 3️⃣ Gemini 比較
    prompt = f"""
    你是一位房地產分析專家，請比較以下兩間房屋的生活機能，列出優點與缺點，最後做總結：

    {text_a}

    {text_b}
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    # 4️⃣ 顯示結果
    st.subheader("📊 Gemini 分析結果")
    st.write(response.text)

    # 左右對照
    st.subheader("🏠 房屋資訊對照表")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"### 房屋 A\n{text_a}")
    with c2:
        st.markdown(f"### 房屋 B\n{text_b}")



