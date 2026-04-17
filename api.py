import streamlit as st
import cv2
import numpy as np
import ollama
from groq import Groq
import base64
import time

# =========================
# 1. 設定與 API 金鑰
# =========================
GROQ_API_KEY = "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"
traffic_video_url = "https://tcnvr3.taichung.gov.tw/983191db"

traffic_prompt = """
請仔細分析這張即時路況畫面，提供以下詳細資訊：
1. 交通流量狀態 (擁擠程度、車輛密度)
2. 道路環境觀察 (天氣、光線、道路類型)
3. 異常狀況偵測 (事故、施工、障礙物)
請使用繁體中文且盡可能的提供具體、客觀和詳細的描述。
"""

# =========================
# 2. 影像連線相關函式
# =========================
def create_cap():
    """建立新的攝影機連線"""
    cap = cv2.VideoCapture(traffic_video_url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 🔥 關鍵：避免延遲累積
    return cap

def encode_image(image):
    _, buffer = cv2.imencode(".jpg", image)
    return base64.b64encode(buffer).decode("utf-8")

# =========================
# 3. AI 分析
# =========================
def analyze_image(image, api_choice):
    base64_img = encode_image(image)

    if api_choice == "Ollama":
        try:
            response = ollama.chat(
                model="llama3.2-vision:11b",
                messages=[{
                    "role": "user",
                    "content": traffic_prompt,
                    "images": [base64_img]
                }]
            )
            return response["message"]["content"]
        except Exception as e:
            return f"Ollama 錯誤：{e}"

    elif api_choice == "Groq":
        try:
            client = Groq(api_key=GROQ_API_KEY)
            completion = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": traffic_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_img}"
                            }
                        }
                    ]
                }],
                temperature=0.7,
                max_completion_tokens=500
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Groq 錯誤：{e}"

# =========================
# 4. 即時影像顯示（LV2 核心）
# =========================
@st.fragment(run_every=0.3)
def show_live_stream():
    # 初始化 cap
    if "cap" not in st.session_state:
        st.session_state.cap = create_cap()
        st.session_state.fail_count = 0

    cap = st.session_state.cap

    # 若 cap 異常，直接重連
    if not cap.isOpened():
        cap.release()
        st.session_state.cap = create_cap()
        st.session_state.fail_count = 0
        st.warning("⚠️ 重新連線中...")
        return

    ret, frame = cap.read()

    # 讀取失敗 → 累計失敗次數
    if not ret or frame is None:
        st.session_state.fail_count += 1

        # 連續失敗 3 次才重連（避免抖動）
        if st.session_state.fail_count >= 3:
            cap.release()
            st.session_state.cap = create_cap()
            st.session_state.fail_count = 0
            st.warning("⚠️ 影像中斷，已自動重新連線")
        return

    # 成功讀取，歸零失敗次數
    st.session_state.fail_count = 0
    st.session_state.current_frame = frame

    st.image(
        frame,
        channels="BGR",
        use_container_width=True,
        caption="🔴 即時路況（自動重連）"
    )

# =========================
# 5. Streamlit 主介面
# =========================
st.title("🚦 即時路況分析系統")

if "current_frame" not in st.session_state:
    st.session_state.current_frame = None

col1, col2 = st.columns([2, 1])

with col1:
    show_live_stream()

with col2:
    st.subheader("控制台")
    api_choice = st.radio("選擇 AI 模型", ["Ollama", "Groq"])
    st.divider()

    if st.button("📸 立即截圖分析", type="primary"):
        if st.session_state.current_frame is not None:
            st.image(
                st.session_state.current_frame,
                channels="BGR",
                caption="已擷取當前畫面",
                use_container_width=True
            )

            with st.spinner("AI 分析中..."):
                result = analyze_image(
                    st.session_state.current_frame,
                    api_choice
                )
                st.success("分析完成！")
                st.markdown(f"### 📊 分析報告\n{result}")
        else:
            st.warning("影像尚未就緒，請稍候")
