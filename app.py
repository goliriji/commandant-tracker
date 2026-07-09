import streamlit as st
import requests
import json
import base64
from audio_recorder_streamlit import audio_recorder
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Commandant Expense Tracker", page_icon="🛡️")
st.title("🛡️ Commandant Expense Tracker")

# 2. API Key Check
if "GEMINI_API_KEY" not in st.secrets:
    st.error("API Key not found in Secrets. Please add it.")
    st.stop()
api_key = st.secrets["GEMINI_API_KEY"]

# 3. Session State
if 'db' not in st.session_state: 
    st.session_state.db = []

# 4. Input Area
audio = audio_recorder(text="Tap to Record", icon_size="2x")
text_in = st.text_input("💬 Type expense manually...")

# 5. Logic
input_data = None
if audio:
    b64 = base64.b64encode(audio).decode('utf-8')
    input_data = {"inlineData": {"mimeType": "audio/wav", "data": b64}}
elif text_in:
    input_data = {"text": text_in}

if input_data:
    st.write("🔍 Processing...")
    try:
        # यहाँ gemini-1.5-flash का इस्तेमाल है
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{
                "parts": [
                    {"text": 'Extract item name and amount. Return ONLY valid JSON: {"item": "Name", "amount": 0.0}'},
                    input_data
                ]
            }]
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            res_json = response.json()
            raw_text = res_json['candidates'][0]['content']['parts'][0]['text'].replace("```json", "").replace("```", "").strip()
            data = json.loads(raw_text)
            st.session_state.db.append(data)
            st.rerun()
        else:
            st.error(f"API Error: {response.status_code}")
    except Exception as e:
        st.error(f"Error: {e}")

# 6. Display
if st.session_state.db:
    df = pd.DataFrame(st.session_state.db)
    st.table(df)
    st.write(f"### Total: ₹{df['amount'].sum()}")
