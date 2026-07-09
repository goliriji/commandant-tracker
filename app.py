import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
from audio_recorder_streamlit import audio_recorder
import time

st.set_page_config(page_title="Commandant Expense Tracker", page_icon="🛡️")
st.title("🛡️ Commandant Expense Tracker")

if "GEMINI_API_KEY" not in st.secrets:
    st.error("API Key missing!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-3.5-flash') 

if 'db' not in st.session_state: st.session_state.db = []

audio = audio_recorder(text="Tap to Record", icon_size="2x")
text_in = st.text_input("💬 Type expense manually...")

# Button to trigger the process
if st.button("Process Expense"):
    if audio or text_in:
        # Use a placeholder to manage the status message
        status = st.empty()
        status.write("🔍 Processing... please wait.")
        
        try:
            prompt = 'Extract the expense item and amount in JSON format: {"item": "Name", "amount": 0.0}. If multiple, return a list.'
            input_data = {"mime_type": "audio/wav", "data": audio} if audio else text_in
            
            response = model.generate_content([prompt, input_data])
            
            raw_text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(raw_text)
            
            # Handle both single dict and list of dicts
            if isinstance(data, dict):
                st.session_state.db.append(data)
            elif isinstance(data, list):
                st.session_state.db.extend(data)
            
            status.success("Added successfully!")
            time.sleep(1)
            st.rerun()
            
        except Exception as e:
            status.empty() # Remove processing message
            if "429" in str(e):
                st.error("Rate limit hit! Please wait 60 seconds before trying again.")
            else:
                st.error(f"Error: {e}")
    else:
        st.warning("Please record audio or type an expense first.")

if st.session_state.db:
    st.table(pd.DataFrame(st.session_state.db))
