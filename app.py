import streamlit as st
import requests
import json
import base64
from audio_recorder_streamlit import audio_recorder

st.title("🛡️ Commandant Expense Tracker")

if "GEMINI_API_KEY" not in st.secrets:
    st.error("API Key missing!")
    st.stop()
api_key = st.secrets["GEMINI_API_KEY"]

if 'db' not in st.session_state: st.session_state.db = []

audio = audio_recorder(text="Tap to Record", icon_size="2x")
text_in = st.text_input("💬 Type expense here:")

input_data = None
if audio:
    b64 = base64.b64encode(audio).decode('utf-8')
    input_data = {"inlineData": {"mimeType": "audio/wav", "data": b64}}
elif text_in:
    input_data = {"text": text_in}

if input_data:
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        # एआई को सिर्फ JSON देने के लिए मजबूर करना
        prompt = 'Extract item and amount. Return ONLY valid JSON format like {"item": "Milk", "amount": 50}. No other words.'
        payload = {"contents": [{"parts": [{"text": prompt}, input_data]}]}
        
        response = requests.post(url, json=payload).json()
        
        # रिस्पॉन्स को साफ करना
        res_text = response['candidates'][0]['content']['parts'][0]['text']
        clean_text = res_text.replace("```json", "").replace("```", "").strip()
        
        data = json.loads(clean_text)
        st.session_state.db.append(data)
        st.rerun()
    except Exception as e:
        st.error(f"AI Response Error: {e}")
        st.write("AI said:", res_text if 'res_text' in locals() else "Nothing")

if st.session_state.db:
    import pandas as pd
    st.table(pd.DataFrame(st.session_state.db))
