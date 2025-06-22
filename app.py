# ====== 功能 2: Gemini 聊天機器人（保留對話歷史） ======
elif app_mode == "🤖 Gemini 聊天機器人":
    st.title("🤖 Gemini Chatbot")
    st.markdown("請輸入任何問題，Gemini 將會回應你，並為你建立主題。")

    # 初始化聊天主題與記錄
    if "topics" not in st.session_state:
        st.session_state.topics = {}  # { 主題名稱: chat_obj }
        st.session_state.active_topic = None

    # ====== 側邊欄主題清單 ======
    with st.sidebar:
        st.subheader("🗂️ 你的聊天主題")
        for topic_name in st.session_state.topics.keys():
            if st.button(topic_name, key=topic_name):
                st.session_state.active_topic = topic_name

    # 顯示目前主題名稱
    if st.session_state.active_topic:
        st.caption(f"🧠 目前主題：**{st.session_state.active_topic}**")

    # ====== 使用者輸入 ======
    user_input = st.text_area("✏️ 你想問 Gemini 什麼？", height=100)

    if st.button("🚀 送出"):
        if user_input.strip() == "":
            st.warning("請輸入問題後再送出。")
        elif len(user_input) > 1000:
            st.warning("⚠️ 輸入過長，請簡化你的問題（最多 1000 字元）。")
        else:
            # 建立主題名稱（自動產生）
            topic_title = user_input.strip()[:20] + "..." if len(user_input.strip()) > 20 else user_input.strip()

            if topic_title not in st.session_state.topics:
                model = genai.GenerativeModel("models/gemini-1.5-flash")
                chat = model.start_chat(history=[])
                st.session_state.topics[topic_title] = chat

            st.session_state.active_topic = topic_title
            chat = st.session_state.topics[topic_title]

            with st.spinner("Gemini 正在生成回應..."):
                try:
                    response = chat.send_message(user_input, stream=True)

                    full_response = ""
                    for chunk in response:
                        if chunk.text:
                            full_response += chunk.text

                    st.success("✅ Gemini 回應：")
                    st.markdown(
                        f"<div style='white-space: pre-wrap;'>{full_response}</div>",
                        unsafe_allow_html=True
                    )

                except requests.exceptions.Timeout:
                    st.error("⏰ 請求逾時，請稍後再試。")
                except Exception as e:
                    st.error(f"❌ 發生錯誤：{e}")

    # ====== 重設所有主題 ======
    if st.button("🧹 清空所有主題"):
        st.session_state.topics = {}
        st.session_state.active_topic = None
        st.success("✅ 已清空所有主題與對話。")

    # ====== 顯示目前主題對話歷程 ======
    if st.session_state.active_topic:
        with st.expander("🕘 查看對話歷程"):
            history = st.session_state.topics[st.session_state.active_topic].history
            for msg in history:
                role = msg.role  # "user" 或 "model"
                text = msg.parts[0].text if msg.parts else ""
                if role == "user":
                    st.markdown(f"**你：** {text}")
                else:
                    st.markdown(f"**Gemini：** {text}")
