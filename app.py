import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
from audio_recorder_streamlit import audio_recorder
import time
import matplotlib.pyplot as plt
import io
import re  # नया: JSON को सुरक्षित निकालने के लिए

st.set_page_config(page_title="Commandant Expense Tracker", page_icon="🛡️")
st.title("🛡️ Commandant Expense Tracker")

# 1. API Setup
if "GEMINI_API_KEY" not in st.secrets:
    st.error("API Key missing! Please add it to Streamlit Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash') 
# 2. State Management
if 'db' not in st.session_state: 
    st.session_state.db = []

# 3. Inputs
audio = audio_recorder(text="Tap to Record", icon_size="2x")
text_in = st.text_input("💬 Type expense manually...")

# 4. Process Logic 
if st.button("Process Expense"):
    if (audio and len(audio) > 0) or (text_in and len(text_in) > 0):
        with st.status("🔍 Processing...", expanded=True) as status:
            try:
                # प्रॉम्प्ट को और भी सख्त बनाया गया है
                prompt = 'Extract the expense item and amount in JSON format: [{"item": "Name", "amount": 0.0}]. Return ONLY a valid JSON list, no other text.'
                
                input_content = {"mime_type": "audio/wav", "data": audio} if audio else text_in
                response = model.generate_content([prompt, input_content])
                
                # Regex का उपयोग करके केवल JSON भाग को खोजना
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
                    raise ValueError(f"AI Model did not return JSON. Raw text: {response.text}")
                
            except Exception as e:
                status.update(label="Error processing data", state="error")
                # एरर को बाहर दिखाने के लिए सेव करें
                st.session_state.last_error = str(e)
    else:
        st.warning("Please record audio or type an expense first.")

# अगर कोई असली एरर है, तो उसे बॉक्स के बाहर प्रमुखता से दिखाएं
if 'last_error' in st.session_state:
    st.error(f"🚨 ACTUAL ERROR: {st.session_state.last_error}")
    del st.session_state.last_error

# 5. Display and Download as Image
if st.session_state.db:
    df = pd.DataFrame(st.session_state.db)
    st.table(df)
    
    fig, ax = plt.subplots(figsize=(8, len(df) * 0.6 + 1))
    ax.axis('tight')
    ax.axis('off')
    
    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.5)
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight', dpi=300, transparent=False, facecolor='white')
    buf.seek(0)
    
    st.download_button(
        label="⬇️ Download Data as PNG",
        data=buf,
        file_name='commandant_expenses.png',
        mime='image/png',
    )
