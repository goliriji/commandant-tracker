import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import io
import requests
import json
import base64
from audio_recorder_streamlit import audio_recorder

# Page configuration
st.set_page_config(page_title="AI Commandant Expense Tracker", page_icon="🤖")
st.title("🤖 AI Commandant Expense Assistant")

# --- SECRETS MANAGEMENT ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = None
    st.error("⚠️ API Key not found in Streamlit Secrets! Please add it in App Settings > Secrets.")

# Initialize memory structures
if 'main_db' not in st.session_state:
    st.session_state.main_db = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [("assistant", "Jai Hind Sir! I am your AI Expense Assistant (Running on Gemini Flash). \n\n👉 **Tap the 🎙️ MIC icon** to speak, OR \n👉 **Type below** to add an expense!")]

# Display chat history
st.subheader("💬 Chat with Assistant")
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.write(text)

# --- NATIVE VOICE RECORDING WIDGET (MIC) ---
st.markdown("---")
col1, col2 = st.columns([1, 4])
with col1:
    audio_bytes = audio_recorder(text="", icon_size="2x", icon_name="microphone")
with col2:
    st.write("👆 **Tap the Mic to Speak** (Audio will be sent directly to AI)")

# --- NORMAL TEXT INPUT ---
user_input = st.chat_input("Or type your message here...")

# --- PROCESSING INPUT (AUDIO OR TEXT) ---
input_received = False
part_data = None
display_text = ""

# Check if audio was recorded
if audio_bytes:
    input_received = True
    display_text = "🎤 [Voice Audio Sent]"
    # Convert audio to base64 so Gemini can listen directly
    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
    part_data = {"inlineData": {"mimeType": "audio/wav", "data": audio_b64}}
# Check if text was typed
elif user_input:
    input_received = True
    display_text = user_input
    part_data = {"text": f"User Input: {user_input}"}

if input_received:
    # Show user input in chat
    st.session_state.chat_history.append(("user", display_text))
    
    if not api_key:
        st.session_state.chat_history.append(("assistant", "Sir, my API Key is missing from the Secrets Vault!"))
        st.rerun()
    else:
        current_date_str = datetime.today().strftime("%d-%m-%Y")
        
        system_prompt = f"""You are an expert AI Accountant for a military Commandant's Expense Tracker.
        The user will provide expense entries via TEXT or RAW AUDIO (in Hindi, English, or Hinglish).
        Listen to the audio or read the text, correct any typos, translate the item name into clean professional English, and extract the details.

        Current Date: {current_date_str}

        Strict Output Format (Return ONLY JSON):
        {{
            "action": "add" or "chat",
            "date": "DD-MM-YYYY",
            "item": "Corrected English Item Name",
            "amount": float_number,
            "reply": "A polite acknowledgment in mixed Hindi/English confirming the addition"
        }}
        """
        
        try:
            # Using Gemini 1.5 Flash for high-speed voice and text processing
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [{"text": system_prompt}, part_data]
                }]
            }
            response = requests.post(url, json=payload, timeout=15)
            res_json = response.json()
            
            ai_response_text = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
            
            # Clean JSON formatting
            if ai_response_text.startswith("
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1
http://googleusercontent.com/immersive_entry_chip/2

इसे पेस्ट करके **Commit changes** कर दीजिए।

### अब यह कैसे काम करेगा:
जैसे ही ऐप रीफ्रेश होगा (इसमें 1-2 मिनट लग सकते हैं क्योंकि हमने एक नया टूल जोड़ा है):
1. आपको स्क्रीन पर एक बड़ा **माइक आइकॉन (🎙️)** दिखाई देगा।
2. आप उस पर टैप करके सीधा बोल सकते हैं (पहली बार में यह माइक की परमिशन मांगेगा)। 
3. और अगर आपका बोलने का मन नहीं है, तो सबसे नीचे **चैट बॉक्स** भी मौजूद है, जहाँ आप आराम से टाइप भी कर सकते हैं।
