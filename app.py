import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import io
import requests
import json

# Page configuration
st.set_page_config(page_title="AI Commandant Expense Tracker", page_icon="🤖")
st.title("🤖 AI Commandant Expense Assistant")

# Sidebar for configuration & flexibility (Safe way to enter API Key)
st.sidebar.header("⚙️ Settings")
st.sidebar.info("Please paste your Gemini API Key below to activate AI.")
api_key = st.sidebar.text_input("Gemini API Key:", type="password")

# Initialize memory structures
if 'main_db' not in st.session_state:
    st.session_state.main_db = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [("assistant", "Jai Hind Sir! I am your AI Expense Assistant. Just type or use voice typing to tell me about any expense (e.g., 'आज 280 का चिकन लिया'). I will automatically correct spellings, translate it to English, and update your ledger!")]

# Display chat history like WhatsApp/Gemini
st.subheader("💬 Chat with Assistant")
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.write(text)

# Chat Input Box at the bottom
user_input = st.chat_input("Type or use Voice Typing here...")

if user_input:
    # Append user message to chat history
    st.session_state.chat_history.append(("user", user_input))
    
    if not api_key:
        st.session_state.chat_history.append(("assistant", "Sir, API Key missing! Please open the sidebar (top-left arrow ＞) and paste your Gemini API Key first."))
        st.rerun()
    else:
        current_date_str = datetime.today().strftime("%d-%m-%Y")
        
        # System Prompt instructing Gemini
        system_prompt = f"""You are an expert AI Accountant for a military Commandant's Expense Tracker.
        The user will input expense entries in Hindi, English, or Hinglish, often with spelling errors or shorthand.
        Your task is to analyze the input, correct any typos, translate the item name into clean professional English, and extract the core details.

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
        
        # Call Gemini API
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [{"text": system_prompt + f"\n\nUser Input: {user_input}"}]
                }]
            }
            response = requests.post(url, json=payload, timeout=10)
            res_json = response.json()
            
            ai_response_text = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
            
            if ai_response_text.startswith("
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1
http://googleusercontent.com/immersive_entry_chip/2

3. अब **Commit changes** पर क्लिक करें। इस बार गिटहब आपको नहीं रोकेगा!

### इसके बाद क्या करना है?
जब आपका ऐप खुलेगा, तो ऊपर बाईं तरफ आपको **एक छोटा सा तीर (＞) या साइडबार (Sidebar)** दिखेगा। उसे खोलकर वहाँ अपनी API Key पेस्ट कर दीजिएगा। उसके बाद ऐप हमेशा की तरह स्मार्ट तरीके से काम करने लगेगा! 

*(नोट: अगर API Key काम न करे, तो गूगल ने उसे गिटहब पर देखने की वजह से ब्लॉक कर दिया होगा, तब आपको उसी तरीके से एक नई API Key जनरेट करनी होगी।)*
