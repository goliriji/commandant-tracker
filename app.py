import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
from audio_recorder_streamlit import audio_recorder
from PIL import Image
import time
import io
import re
import matplotlib.pyplot as plt
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="Commandant Expense Tracker", page_icon="🛡️")

# --- API & Sheets Setup ---
if "GEMINI_API_KEY" not in st.secrets or "gcp_service_account" not in st.secrets:
    st.error("API Key या Google Sheets Credentials गायब हैं! Streamlit Secrets चेक करें।")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-3.5-flash') 

def get_google_sheet():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        client = gspread.authorize(creds)
        # आपकी शीट का लिंक यहाँ है
        sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1i9oBBE86UhSrTzCl1XGZtEvPinmYhbSdYcZFykvBN5A/edit").sheet1
        return sheet
    except Exception as e:
        st.error(f"Google Sheets Connection Error: {e}")
        return None

# --- State Management ---
if 'db' not in st.session_state: 
    st.session_state.db = []
if 'error_msg' not in st.session_state:
    st.session_state.error_msg = None

# --- ERROR DISPLAY ---
if st.session_state.error_msg:
    st.error(f"🚨 ERROR: {st.session_state.error_msg}")
    if st.button("Clear Error"):
        st.session_state.error_msg = None
        st.rerun()

# --- TOP SECTION: Data ---
st.markdown("### 🛡️ Expense Data")
if st.session_state.db:
    df = pd.DataFrame(st.session_state.db)
    
    fig, ax = plt.subplots(figsize=(6, len(df) * 0.5 + 1))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.5)
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight', dpi=300, transparent=False, facecolor='white')
    buf.seek(0)
    
    st.download_button(label="⬇️ Download Image for Reimbursement", data=buf, file_name='expenses.png', mime='image/png')
    plt.close(fig)
        
    st.dataframe(df, use_container_width=True)
else:
    st.info("No expenses yet. Add one below.")

st.divider()

# --- BOTTOM SECTION: Inputs ---
st.markdown("**Add Expense:**")

img_upload = st.file_uploader("Upload Receipt/Image", type=["png", "jpg", "jpeg"])
text_in = st.text_input("Type Expense", placeholder="e.g. 1 kg chicken 280")
st.write("Or record voice:")
audio = audio_recorder(text="Record", icon_size="2x")

# --- PROCESS LOGIC ---
if st.button("Process Expense", use_container_width=True, type="primary"):
    if img_upload or (audio and len(audio) > 0) or (text_in and len(text_in) > 0):
        with st.spinner("Processing with Gemini & Saving to Cloud..."):
            try:
                # प्रॉम्प्ट में Date, Item, Amount फिक्स किया गया है
                current_date = datetime.now().strftime("%d-%b-%Y")
                prompt = f'''Extract the expense items. Return ONLY a valid JSON list format: [{{"Date": "DD-MMM-YYYY", "Item": "Name", "Amount": 0.0}}]. 
                If no specific date is mentioned, use today's date: {current_date}. If it is an image, identify the item and price.'''
                
                input_data = [prompt]
                
                if img_upload:
                    image = Image.open(img_upload)
                    input_data.append(image)
                elif audio:
                    input_data.append({"mime_type": "audio/wav", "data": audio})
                elif text_in:
                    input_data.append(text_in)
                
                response = model.generate_content(input_data)
                match = re.search(r'\[.*\]|\{.*\}', response.text, re.DOTALL)
                
                if match:
                    data = json.loads(match.group())
                    # Make sure it's a list
                    if isinstance(data, dict):
                        data = [data]
                        
                    st.session_state.db.extend(data)
                    
                    # ☁️ Save to Google Sheets
                    sheet = get_google_sheet()
                    if sheet:
                        for row in data:
                            sheet.append_row([row.get("Date", ""), row.get("Item", ""), row.get("Amount", "")])
                    
                    st.session_state.error_msg = None
                    time.sleep(1)
                    st.rerun()
                else:
                    st.session_state.error_msg = f"AI failed to format JSON. Raw output: {response.text}"
                    st.rerun()
                    
            except Exception as e:
                st.session_state.error_msg = str(e)
                st.rerun()
    else:
        st.warning("Please provide input (Image, Text, or Audio) first.")

# ==========================================
# PROCESS LOGIC
# ==========================================
if process_btn:
    if img_upload or (audio and len(audio) > 0) or (text_in and len(text_in) > 0):
        with st.status("✨ Processing...", expanded=True) as status:
            try:
                prompt = 'Extract the expense items and amounts. Return ONLY a valid JSON list format: [{"item": "Name", "amount": 0.0}]. If it is an image of a receipt or item, identify the item and its price.'
                
                input_data = [prompt]
                
                if img_upload:
                    image = Image.open(img_upload)
                    input_data.append(image)
                elif audio:
                    input_data.append({"mime_type": "audio/wav", "data": audio})
                elif text_in:
                    input_data.append(text_in)
                
                response = model.generate_content(input_data)
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
                st.error(f"🚨 ACTUAL ERROR: {e}")
    else:
        st.warning("कृपया कुछ इनपुट दें (➕ फोटो, टेक्स्ट, या 🎙️ ऑडियो)!")
