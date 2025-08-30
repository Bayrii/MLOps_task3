import requests
import streamlit as st

#FastAPI backend URL
BACKEND_URL = "http://backend:8000"  



SYSTEM_PROMPT = """
Your name is Purpo.
You are an expert Azercell assistant. 
Answer all user questions accurately and politely. 
Use concise and clear language.
"""

st.set_page_config(
    page_title="Purpo",
    page_icon="🟣",
    layout="centered",
)


# ---------------------------
# Session state initialization
# ---------------------------
if "chats" not in st.session_state:
    st.session_state.chats = {}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

# ---------------------------
# Sidebar: Chat management
# ---------------------------
st.sidebar.title("💬 Chat Sessions")

# Create new chat
if st.sidebar.button("➕ New Chat"):
    chat_id = f"Chat {len(st.session_state.chats) + 1}"
    st.session_state.chats[chat_id] = []
    st.session_state.current_chat = chat_id

# List existing chats with delete button
for chat_id in list(st.session_state.chats.keys()):
    cols = st.sidebar.columns([4, 1])
    with cols[0]:
        if st.button(chat_id, key=f"open_{chat_id}"):
            st.session_state.current_chat = chat_id
    with cols[1]:
        if st.button("❌", key=f"delete_{chat_id}"):
            del st.session_state.chats[chat_id]
            if st.session_state.current_chat == chat_id:
                st.session_state.current_chat = None
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.write("✅ Connected to backend:", BACKEND_URL)

# ---------------------------
# Main Chat UI
# ---------------------------
st.title("Azercelli Purpo 👾⋆˚☆˖°👾")

if st.session_state.current_chat is None:
    st.info("Click **New Chat** in the sidebar to start.")
else:
    chat_id = st.session_state.current_chat
    messages = st.session_state.chats[chat_id]

    # Display chat history
    for msg in messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])

    # Input box
    if prompt := st.chat_input("Type your message..."):
        # Add current user message
        messages.append({"role": "user", "content": prompt})

        # Build context: all previous messages except last user message
        conversation_context = []
        if len(messages) > 1:
            for m in messages[:-1]:
                conversation_context.append(f"{m['role'].capitalize()}: {m['content']}")
        context_text = "\n".join(conversation_context)

        # Current user message
        current_user_message = messages[-1]["content"]

        # Combine context + current message
        full_prompt = f"{context_text}\nUser: {current_user_message}" if context_text else current_user_message

        # Call FastAPI backend
        with st.chat_message("assistant"):
            response_box = st.empty()
            streamed_text = ""

            try:
                with requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"query": full_prompt, "system": SYSTEM_PROMPT},
                    stream=True,
                ) as r:
                    if r.status_code != 200:
                        response_box.error(f"❌ Error {r.status_code}: {r.text}")
                    else:
                        for chunk in r.iter_content(chunk_size=None):
                            if chunk:
                                decoded = chunk.decode("utf-8")
                                streamed_text += decoded
                                response_box.markdown(streamed_text + "▌")
            except Exception as e:
                response_box.error(f"[Error] {str(e)}")

            # Save assistant reply
            messages.append({"role": "assistant", "content": streamed_text})
            response_box.markdown(streamed_text)
