import streamlit as st
import requests
import json
import base64
from audio_recorder_streamlit import audio_recorder

st.title("🤖 AI Expense Tracker")

# API Key check
if "GEMINI_API_KEY" not in st.secrets:
    st.error("API Key missing! Add in App Settings > Secrets.")
    st.stop()
api_key = st.secrets["GEMINI_API_KEY"]

if 'history' not in st.session_state: st.session_state.history = []

for msg in st.session_state.history:
    with st.chat_message(msg["role"]): st.write(msg["content"])

audio = audio_recorder(text="Tap Mic to Record", icon_size="2x")
user_text = st.chat_input("Or type here...")

input_data = None
if audio:
    st.session_state.history.append({"role": "user", "content": "🎙️ [Voice Audio]"})
    b64 = base64.b64encode(audio).decode('utf-8')
    input_data = {"inlineData": {"mimeType": "audio/wav", "data": b64}}
elif user_text:
    st.session_state.history.append({"role": "user", "content": user_text})
    input_data = {"text": user_text}

if input_data:
    st.rerun()

# Processing (Only if user sent something)
if len(st.session_state.history) > 0 and st.session_state.history[-1]["role"] == "user":
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": "You are a smart accountant. Extract item and amount. Return ONLY valid JSON: {\"item\": \"Name\", \"amount\": 0.0, \"reply\": \"Message\"}"}, input_data]}]}
        res = requests.post(url, json=payload).json()
        raw_text = res['candidates'][0]['content']['parts'][0]['text'].replace("```json", "").replace("```", "").strip()
        data = json.loads(raw_text)
        
        reply = data.get("reply", "Entry added!")
        st.session_state.history.append({"role": "assistant", "content": reply})
        st.rerun()
    except Exception as e:
        st.error(f"AI Error: {e}")
