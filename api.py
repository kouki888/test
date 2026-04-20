import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("❌ 請設定 GOOGLE_API_KEY")
    st.stop()

genai.configure(api_key=API_KEY)

for m in genai.list_models():
    print(m.name, m.supported_generation_methods)
