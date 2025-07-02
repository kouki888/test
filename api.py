import streamlit as st
import google.generativeai as genai

# ===== 頁面設定 =====
st.set_page_config(page_title="💬 Gemini 對話介面", page_icon="🤖")

# ===== API 金鑰設定 =====
# 🚨 替換為你自己的 Gemini API 金鑰
load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))

# ===== 網頁標題與說明 =====
st.title("🤖 Gemini Chatbot")
st.markdown("請輸入任何問題，Gemini 將會回應你。")

# ===== 使用者輸入 =====
user_input = st.text_area("✏️ 你想問 Gemini 什麼？", height=150)

# ===== 回應區塊 =====
if st.button("🚀 送出"):
    if user_input.strip() == "":
        st.warning("請輸入問題後再送出。")
    else:
        with st.spinner("Gemini 正在生成回應..."):
            try:
                model = genai.GenerativeModel("models/gemini-1.5-flash")
                response = model.generate_content(user_input)
                st.success("✅ Gemini 回應：")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"❌ 發生錯誤：{e}")
