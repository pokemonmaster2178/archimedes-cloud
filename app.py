import streamlit as st
from groq import Groq

# Initialize completely free Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Archimedes Terminal", page_icon="🦉", layout="centered")

st.title("🦉 Archimedes Cloud Terminal")
st.caption("The wise mechanical owl workshop assistant — Powered by Groq Free Tier.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_speech := st.chat_input("Speak to Archimedes..."):
    with st.chat_message("user"):
        st.markdown(user_speech)
    st.session_state.messages.append({"role": "user", "content": user_speech})

    system_context = "You are Archimedes, a wise mechanical owl workshop assistant. Keep answers brief, natural, and intelligent."

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile", # Free tier flagship model
                messages=[
                    {"role": "system", "content": system_context},
                    * [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ],
            )
            spoken_reply = completion.choices[0].message.content.strip()
            message_placeholder.markdown(spoken_reply)
            st.session_state.messages.append({"role": "assistant", "content": spoken_reply})
        except Exception as e:
            message_placeholder.markdown(f"⚠️ *My internal cognitive gears seem to be slipping. Error:* {e}")
