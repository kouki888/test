import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

# =========================
# 🔑 載入 API KEY
# =========================
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("❌ 請設定 GOOGLE_API_KEY")
    st.stop()

genai.configure(api_key=API_KEY)

# =========================
# 🤖 模型自動選擇（防404）
# =========================
def get_model():
    model_names = ["gemini-3-flash-preview"]
    
    for name in model_names:
        try:
            model = genai.GenerativeModel(name)
            return model
        except:
            continue
    
    st.error("❌ 無可用模型")
    st.stop()

# =========================
# 🧠 Gemini 法律分析
# =========================
def analyze_with_ai(text):
    model = get_model()

    prompt = f"""
你是一位台灣法律專家，請分析以下案件：

【案件內容】
{text}

請務必用以下格式回答：

【可能涉及罪名】
- （列出所有可能罪名）

【法律依據】
- （列出法條，例如刑法第幾條）

【構成要件分析】
- （逐點說明為何成立）

【可能法律責任】
- （刑責或民事責任）
"""

    response = model.generate_content(prompt)
    return response.text

# =========================
# 🗂️ 初始化 session
# =========================
if "conversations" not in st.session_state:
    st.session_state.conversations = {}

if "topic_ids" not in st.session_state:
    st.session_state.topic_ids = []

if "current_topic" not in st.session_state:
    st.session_state.current_topic = "new"

# =========================
# 🎨 UI 主畫面
# =========================
st.set_page_config(page_title="法律AI分析系統", page_icon="⚖️")

st.title("⚖️ 法律情境分析系統（Gemini AI）")
st.write("輸入情境，AI將自動分析涉及的法條與責任")

# =========================
# ✏️ 使用者輸入
# =========================
user_input = st.text_area("📌 請輸入案件情境", height=150)

if st.button("🔍 開始分析"):

    if user_input.strip() == "":
        st.warning("請輸入內容")
    else:
        with st.spinner("AI分析中..."):
            try:
                result = analyze_with_ai(user_input)

                # 存成新對話
                topic_id = len(st.session_state.topic_ids)
                st.session_state.topic_ids.append(topic_id)

                st.session_state.conversations[topic_id] = {
                    "title": user_input[:10],
                    "content": result
                }

                st.session_state.current_topic = topic_id

            except Exception as e:
                st.error(f"❌ 錯誤：{e}")

# =========================
# 📄 顯示結果
# =========================
if st.session_state.current_topic != "new":
    data = st.session_state.conversations[st.session_state.current_topic]

    st.markdown("---")
    st.subheader(f"📂 案件：{data['title']}")
    st.write(data["content"])

# =========================
# 📚 側邊欄
# =========================
with st.sidebar:
    st.header("🗂️ 案件紀錄")

    if st.button("🆕 新案件"):
        st.session_state.current_topic = "new"

    for tid in st.session_state.topic_ids:
        title = st.session_state.conversations[tid]["title"]

        label = f"✔️ {title}" if tid == st.session_state.current_topic else title

        if st.button(label, key=f"topic_{tid}"):
            st.session_state.current_topic = tid

    st.markdown("---")

    if st.button("🧹 清除紀錄"):
        st.session_state.conversations = {}
        st.session_state.topic_ids = []
        st.session_state.current_topic = "new"
