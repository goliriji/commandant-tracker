import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
from audio_recorder_streamlit import audio_recorder
import time

st.set_page_config(page_title="Commandant Expense Tracker", page_icon="🛡️")
st.title("🛡️ Commandant Expense Tracker")

# 1. API Setup
if "GEMINI_API_KEY" not in st.secrets:
    st.error("API Key missing!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
# Using the stable ID format
model = genai.GenerativeModel('gemini-3.5-flash') 

# 2. State Management
if 'db' not in st.session_state: 
    st.session_state.db = []

# 3. Inputs
audio = audio_recorder(text="Tap to Record", icon_size="2x")
text_in = st.text_input("💬 Type expense manually...")

# 4. Process Logic (Isolated)
if st.button("Process Expense"):
    # Only proceed if we have valid input
    if (audio and len(audio) > 0) or (text_in and len(text_in) > 0):
        with st.status("🔍 Processing...", expanded=True) as status:
            try:
                prompt = 'Extract the expense item and amount in JSON format: {"item": "Name", "amount": 0.0}. Return a list.'
                
                # Prepare input safely
                input_content = {"mime_type": "audio/wav", "data": audio} if audio else text_in
                
                # API Call
                response = model.generate_content([prompt, input_content])
                
                # Cleanup
                raw_text = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(raw_text)
                
                if isinstance(data, dict):
                    st.session_state.db.append(data)
                elif isinstance(data, list):
                    st.session_state.db.extend(data)
                
                status.update(label="Added successfully!", state="complete")
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                status.update(label="Error processing data", state="error")
                if "429" in str(e):
                    st.error("Rate limit reached. Please wait 60 seconds.")
                else:
                    st.error(f"Error: {e}")
    else:
        st.warning("Please record audio or type an expense first.")

# 5. Display
if st.session_state.db:
    st.table(pd.DataFrame(st.session_state.db))
