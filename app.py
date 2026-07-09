import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
from audio_recorder_streamlit import audio_recorder

st.set_page_config(page_title="Commandant Expense Tracker", page_icon="🛡️")
st.title("🛡️ Commandant Expense Tracker")

# API Configuration
if "GEMINI_API_KEY" not in st.secrets:
    st.error("API Key missing!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# आपकी फोटो के अनुसार लेटेस्ट मॉडल आईडी
model = genai.GenerativeModel('gemini-3.5-flash') 

if 'db' not in st.session_state: st.session_state.db = []

audio = audio_recorder(text="Tap to Record", icon_size="2x")
text_in = st.text_input("💬 Type expense manually...")

# प्रोसेसिंग
if audio or text_in:
    st.write("🔍 Processing...")
    try:
        prompt = 'Extract the expense item and amount in strictly JSON format: {"item": "Name", "amount": 0.0}'
        
        # प्रॉम्प्ट और इनपुट भेजना
        input_data = text_in if text_in else audio
        response = model.generate_content([prompt, input_data])
        
        # रिस्पॉन्स को क्लीन करना
        raw_text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw_text)
        
        st.session_state.db.append(data)
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

if st.session_state.db:
    st.table(pd.DataFrame(st.session_state.db))
