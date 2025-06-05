import streamlit as st
import google.generativeai as genai
import requests

# ===== 頁面設定 =====
st.set_page_config(page_title="🤖 Gemini 聊天機器人", page_icon="💬")

# ===== API 設定 =====
genai.configure(api_key="🔑 請填入你的 Gemini API 金鑰")

st.title("🤖 Gemini Chatbot")
st.markdown("請輸入任何問題，Gemini 將會回應你。")

user_input = st.text_area("✏️ 你想問 Gemini 什麼？", height=150)

MAX_TOKENS = 1000

if st.button("🚀 送出"):
    if user_input.strip() == "":
        st.warning("請輸入問題後再送出。")
    elif len(user_input) > MAX_TOKENS:
        st.warning(f"⚠️ 輸入過長（上限 {MAX_TOKENS} 字元），請簡化內容。")
    else:
        with st.spinner("Gemini 正在思考中..."):
            try:
                model = genai.GenerativeModel("models/gemini-1.5-flash")
                response = model.generate_content(user_input, stream=True)

                st.success("✅ Gemini 回應：")
                for chunk in response:
                    if chunk.text:
                        st.write(chunk.text)
            except requests.exceptions.Timeout:
                st.error("⏰ 請求逾時，請稍後再試。")
            except Exception as e:
                st.error(f"❌ 發生錯誤：{e}")
