import google.generativeai as genai
from google.generativeai.types import Blob # यह इंपोर्ट जोड़ें

# ... (बाकी कोड वैसा ही रहेगा)

if audio or text_in:
    st.write("🔍 Processing...")
    try:
        prompt = 'Extract the expense item and amount in strictly JSON format: {"item": "Name", "amount": 0.0}'
        
        if audio:
            # बाइट्स को Blob में बदलें
            audio_blob = Blob(mime_type="audio/wav", data=audio)
            response = model.generate_content([prompt, audio_blob])
        else:
            response = model.generate_content([prompt, text_in])
        
        # रिस्पॉन्स को क्लीन करना
        raw_text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw_text)
        
        st.session_state.db.append(data)
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")
