import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
from audio_recorder_streamlit import audio_recorder
from PIL import Image
import time
import io
import re

# पेज का लेआउट सेट करना
st.set_page_config(page_title="Commandant Expense Tracker", page_icon="🛡️", layout="centered")

# 1. API Setup
if "GEMINI_API_KEY" not in st.secrets:
    st.error("API Key missing! Please add it to Streamlit Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-3.5-flash') 

# 2. State Management
if 'db' not in st.session_state: 
    st.session_state.db = []

# --- TOP SECTION: Title & Data ---
st.markdown("### 🛡️ Commandant Expense Tracker")

if st.session_state.db:
    df = pd.DataFrame(st.session_state.db)
    st.dataframe(df, use_container_width=True)
else:
    st.info("कोई डेटा नहीं है। नीचे ➕ से रसीद की फोटो डालें, बोलें या टाइप करें।")

st.divider() # एक लाइन खींचने के लिए

# --- BOTTOM SECTION: Gemini Style Input Area ---
st.markdown("**नया खर्च जोड़ें:**")

# तीन कॉलम बनाना (फोटो, टेक्स्ट, ऑडियो)
col1, col2, col3 = st.columns([1.5, 4, 1.5], gap="small")

with col1:
    # ➕ इमेज/कैमरा अपलोड
    img_upload = st.file_uploader("➕ फोटो", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

with col2:
    # टेक्स्ट इनपुट
    text_in = st.text_input("💬 टाइप करें", placeholder="खर्च टाइप करें...", label_visibility="collapsed")

with col3:
    # वॉइस रिकॉर्डर
    audio = audio_recorder(text="🎙️", icon_size="2x")

# --- PROCESS LOGIC ---
if st.button("🚀 Process", use_container_width=True):
    if img_upload or (audio and len(audio) > 0) or (text_in and len(text_in) > 0):
        with st.status("🔍 Processing AI...", expanded=True) as status:
            try:
                # प्रॉम्प्ट जो फोटो, टेक्स्ट या ऑडियो तीनों के लिए काम करेगा
                prompt = 'Extract the expense items and amounts. Return ONLY a valid JSON list format: [{"item": "Name", "amount": 0.0}]. If it is an image of a receipt or item, identify the item and its price.'
                
                # इनपुट डेटा लिस्ट बनाना
                input_data = [prompt]
                
                if img_upload:
                    # अगर फोटो है, तो उसे PIL Image में बदलकर भेजना
                    image = Image.open(img_upload)
                    input_data.append(image)
                elif audio:
                    input_data.append({"mime_type": "audio/wav", "data": audio})
                elif text_in:
                    input_data.append(text_in)
                
                # API Call
                response = model.generate_content(input_data)
                
                # JSON Extraction
                match = re.search(r'\[.*\]|\{.*\}', response.text, re.DOTALL)
                
                if match:
                    data = json.loads(match.group())
                    if isinstance(data, dict):
                        st.session_state.db.append(data)
                    elif isinstance(data, list):
                        st.session_state.db.extend(data)
                    
                    status.update(label="Added successfully!", state="complete")
                    time.sleep(1)
                    st.rerun()
                else:
                    raise ValueError(f"AI failed to format JSON. Raw: {response.text}")
                    
            except Exception as e:
                status.update(label="Error processing data", state="error")
                st.session_state.last_error = str(e)
                st.rerun()
    else:
        st.warning("कृपया पहले फोटो डालें, बोलें या टाइप करें।")

# एरर दिखाने का सिस्टम
if 'last_error' in st.session_state:
    st.error(f"🚨 ERROR: {st.session_state.last_error}")
    del st.session_state.last_error
