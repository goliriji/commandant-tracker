```python
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
    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
    part_data = {"inlineData": {"mimeType": "audio/wav", "data": audio_b64}}
# Check if text was typed
elif user_input:
    input_received = True
    display_text = user_input
    part_data = {"text": f"User Input: {user_input}"}

if input_received:
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
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [{"text": system_prompt}, part_data]
                }]
            }
            response = requests.post(url, json=payload, timeout=15)
            res_json = response.json()
            
            ai_response_text = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
            
            # COPY-PASTE SAFE JSON CLEANING
            clean_text = ai_response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_text)
            
            if data.get("action") == "add" and data.get("amount", 0) > 0:
                st.session_state.main_db.append({
                    "Date": data.get("date", current_date_str),
                    "Item": data.get("item", "Unknown"),
                    "Amount": float(data.get("amount", 0))
                })
            
            st.session_state.chat_history.append(("assistant", data.get("reply", "Done Sir!")))
            st.rerun()
            
        except Exception as e:
            st.session_state.chat_history.append(("assistant", "Sorry Sir, I couldn't process that properly. Please try again."))
            st.rerun()

# --- LEDGER & WHATSAPP IMAGE OUTPUT ---
st.markdown("---")
st.subheader("📋 Cumulative Expense Ledger")

if st.session_state.main_db:
    combined_df = pd.DataFrame(st.session_state.main_db)
    st.dataframe(combined_df, use_container_width=True)
    
    total_amount = pd.to_numeric(combined_df["Amount"], errors='coerce').sum()
    st.markdown(f"### 💵 Grand Total: **₹{total_amount:.2f}**")
    
    st.markdown("---")
    st.subheader("📸 Share to WhatsApp")
    
    try:
        fig, ax = plt.subplots(figsize=(6, len(combined_df) * 0.5 + 1.5))
        ax.axis('tight')
        ax.axis('off')
        
        img_data = combined_df.copy()
        img_data.loc[len(img_data)] = ["TOTAL", "---", f"₹{total_amount:.2f}"]
        
        table = ax.table(cellText=img_data.values, colLabels=img_data.columns, cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.2, 1.5)
        
        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_text_props(weight='bold', color='white')
                cell.set_facecolor('#075E54')
            elif row == len(img_data):
                cell.set_text_props(weight='bold')
                cell.set_facecolor('#e9ecef')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=200)
        buf.seek(0)
        img_bytes = buf.getvalue()
        plt.close(fig)
        
        st.download_button(
            label="📥 Download Bill as Image (PNG)",
            data=img_bytes,
            file_name=f"Commandant_AI_Report_{datetime.today().strftime('%d_%m_%Y')}.png",
            mime="image/png"
        )
    except Exception:
        st.warning("Preparing image...")

    st.markdown("---")
    if st.button("⚠️ Clear All Data (Start New Bill)"):
        st.session_state.main_db = []
        st.session_state.chat_history = [st.session_state.chat_history[0]]
        st.success("Ledger cleared!")
        st.rerun()
else:
    st.info("Your ledger is empty. Tap the mic above or type below to add expenses!")


```
