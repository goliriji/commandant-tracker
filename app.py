import streamlit as st
import pandas as pd
import requests
import json
import base64
from audio_recorder_streamlit import audio_recorder

# --- PAGE STYLING (Professional Look) ---
st.set_page_config(page_title="Commandant Expenses", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stApp { border-radius: 15px; }
    h1 { color: #2c3e50; text-align: center; font-family: sans-serif; }
    .stDataFrame { border: 1px solid #ddd; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Commandant Expense Tracker")
st.subheader("Professional AI Accountant")

# --- API KEY CHECK ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("⚠️ API Key missing! Add GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()
api_key = st.secrets["GEMINI_API_KEY"]

# --- APP LOGIC ---
if 'db' not in st.session_state: st.session_state.db = []

# Microphone & Input
col1, col2 = st.columns([1, 4])
with col1:
    audio = audio_recorder(text="", icon_size="2x")
with col2:
    text_in = st.text_input("💬 Type expense manually...", key="text_in")

input_data = None
if audio:
    b64 = base64.b64encode(audio).decode('utf-8')
    input_data = {"inlineData": {"mimeType": "audio/wav", "data": b64}}
elif text_in:
    input_data = {"text": text_in}

# Process Input
if input_data:
    with st.spinner("Analyzing with AI..."):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": "Extract item and amount. JSON ONLY: {\"item\": \"name\", \"amount\": 0.0}"}, input_data]}]}
            res = requests.post(url, json=payload).json()
            raw = res['candidates'][0]['content']['parts'][0]['text'].replace("```json", "").replace("```", "").strip()
            data = json.loads(raw)
            st.session_state.db.append(data)
            st.success(f"✅ Added: {data['item']} (₹{data['amount']})")
        except:
            st.error("❌ Processing failed. Please try again.")

# --- DISPLAY TABLE ---
if st.session_state.db:
    st.markdown("### 📋 Recent Entries")
    df = pd.DataFrame(st.session_state.db)
    st.table(df)
    st.metric("Total Expenses", f"₹{df['amount'].sum()}")
else:
    st.info("💡 Record your first expense by tapping the Mic or typing above.")
