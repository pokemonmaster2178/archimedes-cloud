import streamlit as st
from groq import Groq
from gtts import gTTS
import os

# Initialize Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Archimedes Terminal", page_icon="🦉", layout="centered")

st.title("🦉 Archimedes Voice Terminal")
st.caption("Talk or type to your wise mechanical owl workshop assistant — 100% Free.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "audio" in message:
            st.audio(message["audio"], format="audio/mp3")

# --- INPUT SECTION: VOICE & TEXT ---
user_text = st.chat_input("Type your message here...")
audio_file = st.audio_input("Or tap to record your voice 🎙️")

input_received = None

# If user used voice recording
if audio_file is not None:
    # Save temporary audio file to send to Groq Whisper
    with open("temp_user_voice.wav", "wb") as f:
        f.write(audio_file.read())
    
    with st.spinner("🦉 Listening to your voice..."):
        try:
            with open("temp_user_voice.wav", "rb") as audio:
                transcription = client.audio.transcriptions.create(
                    model="whisper-large-v3", 
                    file=audio
                )
            input_received = transcription.text
        except Exception as e:
            st.error(f"Failed to process voice: {e}")
    
    # Clean up temp file
    if os.path.exists("temp_user_voice.wav"):
        os.remove("temp_user_voice.wav")

# If user typed instead
elif user_text:
    input_received = user_text

# --- PROCESSING THE RESPONSE ---
if input_received:
    # Append user message
    with st.chat_message("user"):
        st.markdown(input_received)
    st.session_state.messages.append({"role": "user", "content": input_received})

    system_context = "You are Archimedes, a wise, slightly witty mechanical owl workshop assistant. Keep answers brief, natural, and intelligent."

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            # 1. Get Text Reply from Llama
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_context},
                    * [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ],
            )
            spoken_reply = completion.choices[0].message.content.strip()
            message_placeholder.markdown(spoken_reply)
            
            # 2. Convert text reply to audio speech
            tts = gTTS(text=spoken_reply, lang='en', tld='co.uk') # British accent for an old owl vibe!
            audio_path = f"reply_{len(st.session_state.messages)}.mp3"
            tts.save(audio_path)
            
            # Play the sound instantly
            st.audio(audio_path, format="audio/mp3", autoplay=True)
            
            # Save message along with its audio track to history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": spoken_reply,
                "audio": audio_path
            })
            
        except Exception as e:
            message_placeholder.markdown(f"⚠️ *My internal cognitive gears seem to be slipping. Error:* {e}")
