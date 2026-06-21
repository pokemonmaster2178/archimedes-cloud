import streamlit as st
from groq import Groq
from gtts import gTTS
import os

# Initialize free Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Archimedes Core", page_icon="🦉", layout="centered")

# --- UI VISUAL CUSTOMIZATION (JARVIS WORKSHOP THEME) ---
st.markdown("""
    <style>
    /* Main background and font */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    /* Headers styling */
    h1 {
        color: #00f2fe;
        text-shadow: 0 0 10px rgba(0, 242, 254, 0.5);
        font-family: 'Courier New', Courier, monospace;
    }
    /* Chat inputs and mic styling */
    .stChatInputContainer {
        border-radius: 10px;
        border: 1px solid #00f2fe !important;
        box-shadow: 0 0 8px rgba(0, 242, 254, 0.2);
    }
    /* Status spinners */
    div blockquote {
        border-left: 3px solid #ff007f !important;
        background-color: #161b22;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Archimedes: Jarvis Core")
st.caption("Advanced Workshop Intelligence System Architecture — Active")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history with custom audio blocks
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "audio" in message:
            st.audio(message["audio"], format="audio/mp3")

# --- INPUT CHANNELS ---
user_text = st.chat_input("Input command or text query...")
audio_file = st.audio_input("Initialize Voice Uplink 🎙️")

input_received = None

if audio_file is not None:
    with open("temp_user_voice.wav", "wb") as f:
        f.write(audio_file.read())
    
    with st.spinner("⚡ Processing audio frequencies..."):
        try:
            with open("temp_user_voice.wav", "rb") as audio:
                transcription = client.audio.transcriptions.create(
                    model="whisper-large-v3", 
                    file=audio
                )
            input_received = transcription.text
        except Exception as e:
            st.error(f"Uplink Error: {e}")
    
    if os.path.exists("temp_user_voice.wav"):
        os.remove("temp_user_voice.wav")

elif user_text:
    input_received = user_text

# --- SYSTEM COMPUTATION ---
if input_received:
    with st.chat_message("user"):
        st.markdown(input_received)
    st.session_state.messages.append({"role": "user", "content": input_received})

    # Personality profile to mimic a sophisticated workspace assistant
    system_context = "You are Archimedes, an elite AI terminal modeled closely after JARVIS. Speak confidently, intelligently, and with an efficient, calm demeanor. Keep responses snappy."

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_context},
                    * [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ],
            )
            spoken_reply = completion.choices[0].message.content.strip()
            message_placeholder.markdown(spoken_reply)
            
            # Formulate speech using standard accent variations for an elegant masculine tone
            tts = gTTS(text=spoken_reply, lang='en', tld='com') 
            audio_path = f"reply_{len(st.session_state.messages)}.mp3"
            tts.save(audio_path)
            
            st.audio(audio_path, format="audio/mp3", autoplay=True)
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": spoken_reply,
                "audio": audio_path
            })
            
        except Exception as e:
            message_placeholder.markdown(f"⚠️ *Core matrix exception:* {e}")
