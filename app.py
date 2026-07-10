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

# पेज का लेआउट सेट करना
st.set_page_config(page_title="Commandant Expense Tracker", page_icon="🛡️", layout="centered")

# --- CUSTOM CSS (मोबाइल ऑप्टिमाइजेशन और Gemini लुक के लिए) ---
st.markdown("""
<style>
    /* खाली स्क्रीन का स्टाइल */
    .empty-state {
        text-align: center;
        font-size: 28px;
        color: #1f1f1f;
        margin-top: 15vh;
        font-weight: 500;
        font-family: sans-serif;
    }

    /* 📱 मोबाइल स्क्रीन के लिए कॉलम को एक लाइन (Row) में जबरदस्ती रखना */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
        }
        div[data-testid="column"] {
            width: auto !important;
            flex: 1 1 0% !important;
            min-width: 0 !important;
            padding: 0 3px !important;
        }
    }

    /* 🗂️ File Uploader को छोटा और साफ बनाना */
    div[data-testid="stFileUploaderDropzone"] {
        padding: 5px !important;
        min-height: 40px !important;
    }
    div[data-testid="stFileUploaderDropzoneInstructions"] {
        display: none !important; /* "Drag and drop" टेक्स्ट छिपाएं */
    }
    small {
        display: none !important; /* "200MB limit" टेक्स्ट छिपाएं */
    }
    
    /* टेक्स्ट इनपुट बॉक्स का मार्जिन कम करना */
    div.stTextInput > div > div > input {
        padding: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# 1. API Setup
if "GEMINI_API_KEY" not in st.secrets:
    st.error("API Key missing! Please add it to Streamlit Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
# डिफ़ॉल्ट रूप से लेटेस्ट प्रो एक्सटेंडेड मॉडल का उपयोग किया जा रहा है
model = genai.GenerativeModel('gemini-3.5-pro') 

# 2. State Management
if 'db' not in st.session_state: 
    st.session_state.db = []

# ==========================================
# TOP SECTION: डेटा डिस्प्ले और खाली स्क्रीन
# ==========================================
if st.session_state.db:
    df = pd.DataFrame(st.session_state.db)
    
    col_title, col_down = st.columns([3, 1])
    with col_title:
        st.markdown("### 🛡️ Expense Data")
    with col_down:
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
        
        st.download_button(
            label="⬇️ Image",
            data=buf,
            file_name='expenses.png',
            mime='image/png',
            use_container_width=True
        )
        plt.close(fig)
        
    st.dataframe(df, use_container_width=True)
else:
    st.markdown('<div class="empty-state">✨<br>Any new expenses to track?</div>', unsafe_allow_html=True)

st.markdown("<br><br><br>", unsafe_allow_html=True)

# ==========================================
# BOTTOM SECTION: Gemini स्टाइल इनपुट बार
# ==========================================
st.markdown("---")

col1, col2, col3, col4 = st.columns([1.5, 4, 1.2, 1.2], gap="small")

with col1:
    img_upload = st.file_uploader("Upload", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
with col2:
    text_in = st.text_input("Ask", placeholder="Ask Gemini...", label_visibility="collapsed")
with col3:
    audio = audio_recorder(text="", icon_size="2x")
with col4:
    process_btn = st.button("▶", use_container_width=True)


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
