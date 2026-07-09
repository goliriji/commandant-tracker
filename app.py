import streamlit as st
import requests
import json
import base64
import pandas as pd
from audio_recorder_streamlit import audio_recorder

# पेज सेटिंग
st.set_page_config(page_title="Commandant Expense Tracker", page_icon="🛡️")
st.title("🛡️ Commandant Expense Tracker")

# API की चेक
if "GEMINI_API_KEY" not in st.secrets:
    st.error("API Key missing in Secrets!")
    st.stop()
api_key = st.secrets["GEMINI_API_KEY"]

if 'db' not in st.session_state: 
    st.session_state.db = []

# इनपुट इंटरफेस
audio = audio_recorder(text="Tap to Record", icon_size="2x")
text_in = st.text_input("💬 Type expense manually...")

input_data = None
if audio:
    b64 = base64.b64encode(audio).decode('utf-8')
    input_data = {"inlineData": {"mimeType": "audio/wav", "data": b64}}
elif text_in:
    input_data = {"text": text_in}

# प्रोसेसिंग लॉजिक
if input_data:
    st.write("🔍 Processing...")
    try:
        # यहाँ आपके बताए अनुसार 3.1 मॉडल का इस्तेमाल है
        model_name = "gemini-3.1-flash-lite"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": 'Extract JSON: {"item": "Name", "amount": 0.0}'}, input_data]}]
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            res_json = response.json()
            raw_text = res_json['candidates'][0]['content']['parts'][0]['text'].replace("```json", "").replace("```", "").strip()
            data = json.loads(raw_text)
            st.session_state.db.append(data)
            st.rerun()
        else:
            st.error(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Critical Error: {e}")

# डिस्प्ले टेबल
if st.session_state.db:
    df = pd.DataFrame(st.session_state.db)
    st.table(df)
    st.write(f"### Total: ₹{df['amount'].sum()}")
