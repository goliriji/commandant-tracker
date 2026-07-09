import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import io
import requests
import json
import base64
from audio_recorder_streamlit import audio_recorder

st.set_page_config(page_title="AI Commandant Tracker", page_icon="🤖")
st.title("🤖 AI Commandant Expense Assistant")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = None
    st.error("API Key missing in Secrets!")

if 'main_db' not in st.session_state: st.session_state.main_db = []
if 'chat_history' not in st.session_state: st.session_state.chat_history = [("assistant", "Jai Hind! Tap 🎙️ Mic or Type to start.")]

for role, text in st.session_state.chat_history:
    with st.chat_message(role): st.write(text)

audio_bytes = audio_recorder(text="Tap to Record", icon_size="2x")
user_input = st.chat_input("Type here...")

input_data = None
display = ""

if audio_bytes:
    display = "🎤 [Voice Sent]"
    b64 = base64.b64encode(audio_bytes).decode('utf-8')
    input_data = {"inlineData": {"mimeType": "audio/wav", "data": b64}}
elif user_input:
    display = user_input
    input_data = {"text": user_input}

if input_data:
    st.session_state.chat_history.append(("user", display))
    if api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": "You are an accountant. Return ONLY valid JSON: {\"date\": \"DD-MM-YYYY\", \"item\": \"Name\", \"amount\": 0.0, \"reply\": \"Msg\"}"}, input_data]}]}
            res = requests.post(url, json=payload).json()
            txt = res['candidates'][0]['content']['parts'][0]['text'].replace("```json", "").replace("```", "").strip()
            data = json.loads(txt)
            if data.get("amount", 0) > 0:
                st.session_state.main_db.append({"Date": data.get("date", "09-07-2026"), "Item": data["item"], "Amount": float(data["amount"])})
            st.session_state.chat_history.append(("assistant", data.get("reply", "Done!")))
            st.rerun()
        except:
            st.session_state.chat_history.append(("assistant", "Error processing input."))
            st.rerun()

st.markdown("---")
if st.session_state.main_db:
    df = pd.DataFrame(st.session_state.main_db)
    st.dataframe(df)
    st.write(f"### Total: ₹{df['Amount'].sum()}")
