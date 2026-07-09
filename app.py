import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Commandant Expense Tracker", page_icon="💰")
st.title("💰 कमांडेंस आइटम लिस्ट")

if 'expenses' not in st.session_state:
    st.session_state.expenses = []

with st.form("expense_form", clear_on_submit=True):
    item_name = st.text_input("आइटम का नाम (जैसे: चिकन, धान की मिलिंग):")
    amount = st.number_input("कीमत (₹):", min_value=0.0, step=1.0)
    date_selected = st.date_input("तारीख:", datetime.today())
    submit_button = st.form_submit_button(label="खर्चा जोड़ें")

if submit_button and item_name and amount > 0:
    st.session_state.expenses.append({
        "तारीख": date_selected.strftime("%d-%m-%Y"),
        "आइटम": item_name,
        "कीमत (₹)": amount
    })
    st.success(f"'{item_name}' लिस्ट में जोड़ दिया गया!")

if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)
    st.subheader("📋 खर्चों का हिसाब")
    st.dataframe(df, use_container_width=True)
    
    total_amount = df["कीमत (₹)"].sum()
    st.markdown(f"### 💵 कुल खर्च: **₹{total_amount:.2f}**")
else:
    st.info("अभी तक कोई खर्चा नहीं जोड़ा गया है। ऊपर फॉर्म भरकर आइटम जोड़ें।")
