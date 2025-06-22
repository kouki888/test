# ====== 🤖 功能 2：Gemini 聊天機器人 ======
elif app_mode == "🤖 Gemini 聊天機器人":
    st.title("🤖 Gemini Chatbot")
    st.markdown("請輸入任何問題，Gemini 將會回應你。")

    # 初始化 session_state 儲存對話紀錄
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "selected_chat" not in st.session_state:
        st.session_state.selected_chat = None

    # 顯示側邊欄的聊天記錄清單
    with st.sidebar:
        st.markdown("---")
        st.header("🗂️ 聊天紀錄")

        for idx, chat in enumerate(st.session_state.chat_history):
            if st.button(chat["title"], key=f"chat_{idx}"):
                st.session_state.selected_chat = idx

        if st.button("🗑️ 清除所有聊天紀錄"):
            st.session_state.chat_history = []
            st.session_state.selected_chat = None

    # 使用者輸入區塊
    user_input = st.text_area("✏️ 你想問 Gemini 什麼？", height=100)

    if st.button("🚀 送出"):
        if user_input.strip() == "":
            st.warning("請輸入問題後再送出。")
        elif len(user_input) > 1000:
            st.warning("⚠️ 輸入過長，請簡化你的問題（最多 1000 字元）。")
        else:
            with st.spinner("Gemini 正在生成回應..."):
                try:
                    # 建立模型
                    model = genai.GenerativeModel("models/gemini-1.5-flash")
                    response = model.generate_content(user_input)
                    reply = response.text.strip()

                    # 主題摘要：生成簡短主題
                    title_prompt = "請為以下問題生成一個簡短有代表性的主題（不超過10字）：\n\n" + user_input
                    title_response = model.generate_content(title_prompt)
                    title = title_response.text.strip().replace("\n", "")

                    # 儲存進 session_state
                    st.session_state.chat_history.append({
                        "title": title,
                        "user_input": user_input,
                        "response": reply
                    })
                    st.session_state.selected_chat = len(st.session_state.chat_history) - 1

                except requests.exceptions.Timeout:
                    st.error("⏰ 請求逾時，請稍後再試。")
                except Exception as e:
                    st.error(f"❌ 發生錯誤：{e}")

    # 顯示選定的對話紀錄
    if st.session_state.selected_chat is not None:
        chat = st.session_state.chat_history[st.session_state.selected_chat]
        st.markdown("### 🧑 使用者提問")
        st.info(chat["user_input"])
        st.markdown("### 🤖 Gemini 回應")
        st.success(chat["response"])
