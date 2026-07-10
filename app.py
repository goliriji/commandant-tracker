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

# --- पेज कॉन्फ़िगरेशन और थीम ---
st.set_page_config(page_title="Official Expense Manager", page_icon="🛡️", layout="centered")

# --- प्रीमियम लुक के लिए कस्टम CSS ---
st.markdown("""
    <style>
    /* मुख्य ऐप का बैकग्राउंड और फॉन्ट */
    .main { background-color: #f8f9fa; }
    h1, h2, h3 { color: #1e293b; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* प्रीमियम कार्ड डिज़ाइन */
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        border-left: 5px solid #0f172a;
        margin-bottom: 20px;
    }
    
    /* इनपुट बॉक्स और बटन का स्टाइल */
    .stButton>button {
        background-color: #0f172a !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1e293b !important;
        transform: translateY(-1px);
    }
    
    /* ऑडियो रिकॉर्डर कंटेनर */
    .audio-container {
        background: #f1f5f9;
        padding: 15px;
        border-radius: 8px;
        border: 1px dashed #cbd5e1;
        text-align: center;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- API & Sheets Setup ---
if "GEMINI_API_KEY" not in st.secrets or "GOOGLE_CREDENTIALS" not in st.secrets:
    st.error("Credentials missing in Streamlit Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-3.5-flash') 

def get_google_sheet():
    try:
        creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1i9oBBE86UhSrTzCl1XGZtEvPinmYhbSdYcZFykvBN5A/edit").sheet1
        return sheet
    except Exception as e:
        st.error(f"Google Sheets Connection Error: {e}")
        return None

# --- डेटा लोड और स्टेट मैनेजमेंट ---
if 'db' not in st.session_state:
    st.session_state.db = []
if 'error_msg' not in st.session_state:
    st.session_state.error_msg = None

# सिंक करने के लिए शुरुआती डेटा शीट से उठाना (यदि स्टेट खाली है)
if not st.session_state.db:
    try:
        sheet = get_google_sheet()
        if sheet:
            records = sheet.get_all_records()
            if records:
                # कॉलम के नाम मैच करने के लिए कस्टमाइज़ेशन
                st.session_state.db = records
    except:
        pass

# --- ऐप हेडर ---
st.markdown("<h2 style='text-align: center; margin-bottom: 25px;'>🛡️ एक्सपेंस ट्रैकर एवं रीइंबर्समेंट सिस्टम</h2>", unsafe_allow_html=True)

if st.session_state.error_msg:
    st.error(f"🚨 सिस्टम अलर्ट: {st.session_state.error_msg}")
    if st.button("Clear Alert"):
        st.session_state.error_msg = None
        st.rerun()

# --- प्रोफेशनल नेविगेशन टैब्स ---
tab1, tab2 = st.tabs(["📊 डैशबोर्ड और समरी", "➕ नया खर्च दर्ज करें"])

# --- टैब 1: डैशबोर्ड और डेटा व्यू ---
with tab1:
    df = pd.DataFrame(st.session_state.db) if st.session_state.db else pd.DataFrame(columns=["Date", "Item", "Amount"])
    
    # 1. एग्जीक्यूटिव मीट्रिक कार्ड
    total_amount = 0.0
    if not df.empty and "Amount" in df.columns:
        df["Amount"] = pd.to_numeric(df["Amount"], errors='coerce').fillna(0.0)
        total_amount = df["Amount"].sum()
        
    st.markdown(f"""
        <div class="metric-card">
            <span style="color: #64748b; font-size: 14px; uppercase; font-weight: 600;">कुल बकाया रीइंबर्समेंट राशि</span>
            <h1 style="margin: 5px 0 0 0; color: #0f172a; font-size: 36px;">₹ {total_amount:,.2f}</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # 2. डेटा टेबल और इमेज डाउनलोड
    if not df.empty:
        st.markdown("### 📋 खर्चों की सूची")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # रीइंबर्समेंट के लिए इमेज जनरेट करना
        fig, ax = plt.subplots(figsize=(6, len(df) * 0.4 + 1.2))
        ax.axis('tight')
        ax.axis('off')
        
        # प्रोफेशनल टेबल कलर स्कीम
        table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 1.6)
        
        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_text_props(weight='bold', color='white')
                cell.set_facecolor('#0f172a') # डार्क थीम हेडर
            else:
                cell.set_facecolor('#f8f9fa' if row % 2 == 0 else '#ffffff')
        
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches='tight', dpi=300, transparent=False, facecolor='white')
        buf.seek(0)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(label="⬇️ व्हाट्सएप पर भेजने के लिए इमेज डाउनलोड करें", data=buf, file_name=f'Expense_Summary_{datetime.now().strftime("%d-%b")}.png', mime='image/png', use_container_width=True)
        plt.close(fig)
    else:
        st.info("अभी कोई खर्च दर्ज नहीं है। 'नया खर्च दर्ज करें' टैब में जाकर एंट्री करें।")

# --- टैब 2: इनपुट फॉर्म ---
with tab2:
    st.markdown("### ✍️ एंट्री फॉर्म")
    
    text_in = st.text_input("खर्च का विवरण टाइप करें (रफ़ भाषा में भी चलेगा)", placeholder="उदाहरण: 2000 का गाड़ी में पेट्रोल डलवाया")
    
    st.markdown("<p style='font-weight: 600; margin-bottom: 5px;'>या आवाज़ रिकॉर्ड करें:</p>", unsafe_allow_html=True)
    st.markdown('<div class="audio-container">', unsafe_allow_html=True)
    audio = audio_recorder(text="यहाँ क्लिक करके बोलें", icon_size="2x", neutral_color="#0f172a", recording_color="#dc2626")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    img_upload = st.file_uploader("रसीद या बिल की फोटो अपलोड करें (वैकल्पिक)", type=["png", "jpg", "jpeg"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 खर्च को प्रोसेस और सेव करें", use_container_width=True):
        if img_upload or (audio and len(audio) > 0) or (text_in and len(text_in) > 0):
            with st.spinner("AI डेटा को सही कर रहा है और क्लाउड में सुरक्षित कर रहा है..."):
                try:
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
                        if isinstance(data, dict):
                            data = [data]
                            
                        st.session_state.db.extend(data)
                        
                        # ☁️ Google Sheets में सेव करना
                        sheet = get_google_sheet()
                        if sheet:
                            for row in data:
                                sheet.append_row([str(row.get("Date", "")), str(row.get("Item", "")), float(row.get("Amount", 0.0))])
                        
                        st.session_state.error_msg = None
                        st.toast("✅ खर्च सफलतापूर्वक क्लाउड और डेटाबेस में जुड़ गया!", icon="🎉")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.session_state.error_msg = f"AI प्रारूप को समझ नहीं पाया। कृपया दोबारा प्रयास करें।"
                        st.rerun()
                        
                except Exception as e:
                    st.session_state.error_msg = str(e)
                    st.rerun()
        else:
            st.warning("कृपया पहले कोई इनपुट दें (टाइप करें, बोलें या फोटो अपलोड करें)।")
