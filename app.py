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

# --- SECRETS MANAGEMENT: Automatically fetch API Key from Streamlit Vault ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = None
    st.error("⚠️ API Key not found in Streamlit Secrets! Please add it in App Settings > Secrets.")

# Initialize memory structures
if 'main_db' not in st.session_state:
    st.session_state.main_db = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [("assistant", "Jai Hind Sir! I am your AI Expense Assistant. Just type or use voice typing to tell me about any expense (e.g., 'आज 280 का चिकन लिया'). I will automatically correct spellings, translate it to English, and update your ledger!")]

# Display chat history
st.subheader("💬 Chat with Assistant")
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.write(text)

# Chat Input Box at the bottom
user_input = st.chat_input("Type or use Voice Typing here...")

if user_input:
    # Append user message
    st.session_state.chat_history.append(("user", user_input))
    
    if not api_key:
        st.session_state.chat_history.append(("assistant", "Sir, my API Key is missing from the Secrets Vault! I cannot process requests right now."))
        st.rerun()
    else:
        current_date_str = datetime.today().strftime("%d-%m-%Y")
        
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
            
            if ai_response_text.startswith("```json"): ai_response_text = ai_response_text[7:]
            if ai_response_text.startswith("```"): ai_response_text = ai_response_text[3:]
            if ai_response_text.endswith("```"): ai_response_text = ai_response_text[:-3]
            ai_response_text = ai_response_text.strip()
            
            data = json.loads(ai_response_text)
            
            if data.get("action") == "add" and data.get("amount", 0) > 0:
                st.session_state.main_db.append({
                    "Date": data.get("date", current_date_str),
                    "Item": data.get("item", "Unknown"),
                    "Amount": float(data.get("amount", 0))
                })
            
            st.session_state.chat_history.append(("assistant", data.get("reply", "Done Sir!")))
            st.rerun()
            
        except Exception:
            st.session_state.chat_history.append(("assistant", "Sorry Sir, I couldn't process that properly. Please try again."))
            st.rerun()

# Ledger & Image Output Section
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
    st.info("Your ledger is empty. Start chatting with the assistant above to add expenses!")
