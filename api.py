import google.generativeai as genai
from dotenv import load_dotenv
import os

# 載入 .env 檔案中的 GOOGLE_API_KEY
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("❌ API 金鑰未設定，請確認 .env 檔案或環境變數。")
    exit()

# 設定 Gemini API 金鑰
genai.configure(api_key=API_KEY)

try:
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    response = model.generate_content("你好，請用一句話介紹你自己")
    print("✅ Gemini 回應：")
    print(response.text.strip())
except Exception as e:
    print(f"❌ 發生錯誤：{e}")
