import streamlit as st
from groq import Groq
import re

# Initialize the Groq client pulling securely from cloud secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Archimedes Terminal", page_icon="🦉", layout="centered")

st.title("🦉 Archimedes Cloud Terminal")
st.caption("The wise mechanical owl workshop assistant — running at full cloud power.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def clean_ai_response(raw_text):
    """Removes deep thoughts wrapped in thinking tags to keep answers clean."""
    clean = re.sub(r'<think>.*?</think>', '', raw_text, flags=re.DOTALL)
    return clean.strip()

# Handle user input
if user_speech := st.chat_input("Speak to Archimedes..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_speech)
    st.session_state.messages.append({"role": "user", "content": user_speech})

    # Build prompt context
    system_context = "You are Archimedes, a wise mechanical owl workshop assistant. Keep answers brief, natural, and intelligent."

    # Generate cloud response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": system_context},
                    * [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ],
                stream=False,
            )
            raw_reply = completion.choices[0].message.content
            spoken_reply = clean_ai_response(raw_reply)
            message_placeholder.markdown(spoken_reply)
            st.session_state.messages.append({"role": "assistant", "content": spoken_reply})
        except Exception as e:
            message_placeholder.markdown("⚠️ *My internal cognitive gears seem to be slipping.*")