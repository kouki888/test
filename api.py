import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv  # ← 加上這行

# ===== 頁面設定 =====
st.set_page_config(page_title="💬 Gemini 對話介面", page_icon="🤖")

# ===== 載入 .env 並設定 API 金鑰 =====
load_dotenv()  # ← 載入 .env 檔案
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
                # 使用 Gemini 模型
                model = genai.GenerativeModel("models/gemini-1.5-flash")
                response = model.generate_content(user_input)

                # 顯示回應
                st.success("✅ Gemini 回應：")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"❌ 發生錯誤：{e}")
