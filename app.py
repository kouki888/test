elif app_mode == "🤖 Gemini 聊天機器人":
    st.title("🤖 Gemini Chatbot")
    st.markdown("請輸入任何問題，Gemini 將回應你，並自動為對話產生主題並加入左側清單。")

    # 初始化 Session State
    if "topics" not in st.session_state:
        st.session_state.topics = {}  # 儲存每個主題對應的 chat 物件
    if "active_topic" not in st.session_state:
        st.session_state.active_topic = None

    # ====== 使用者輸入框 ======
    user_input = st.text_input("✏️ 請輸入你的問題")
    submitted = st.button("🚀 送出")

    # ====== 若使用者送出訊息 ======
    if submitted and user_input.strip():
        # 自動產生主題名稱
        topic_title = user_input.strip()[:20] + "..." if len(user_input.strip()) > 20 else user_input.strip()

        # 若是新主題則建立 chat 並加入 topics
        if topic_title not in st.session_state.topics:
            model = genai.GenerativeModel("models/gemini-1.5-flash")
            chat = model.start_chat(history=[])
            st.session_state.topics[topic_title] = chat
        else:
            chat = st.session_state.topics[topic_title]

        # 設定目前主題為這一則輸入
        st.session_state.active_topic = topic_title

        # 發送訊息並取得回覆
        with st.spinner("💬 Gemini 正在思考中..."):
            try:
                response = chat.send_message(user_input, stream=True)
                full_response = ""
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                st.success("✅ Gemini 回應：")
                st.markdown(f"<div style='white-space: pre-wrap;'>{full_response}</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ 發生錯誤：{e}")

    # ====== 側邊欄主題清單 ======
    with st.sidebar:
        st.subheader("🗂️ 你的聊天主題")
        for topic_name in list(st.session_state.topics.keys()):
            if st.button(topic_name, key=topic_name):
                st.session_state.active_topic = topic_name

        if st.button("🧹 清空所有主題"):
            st.session_state.topics = {}
            st.session_state.active_topic = None
            st.success("✅ 已清空所有主題與對話。")

    # ====== 顯示目前主題對話歷程 ======
    if st.session_state.active_topic:
        st.markdown(f"### 🧠 主題：**{st.session_state.active_topic}**")
        chat = st.session_state.topics[st.session_state.active_topic]
        for msg in chat.history:
            role = msg.role
            text = msg.parts[0].text if msg.parts else ""
            if role == "user":
                st.markdown(f"🧑‍💬 **你：** {text}")
            else:
                st.markdown(f"🤖 **Gemini：** {text}")
