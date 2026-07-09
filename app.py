import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Page configuration
st.set_page_config(page_title="Commandant Expense Tracker", page_icon="💰")
st.title("💰 Commandant Expense List")

# Google Sheet Link provided by you
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1i9oBBE86UhSrTzCl1XGZtEvPinmYhbSdYcZFykvBN5A/edit?usp=drivesdk"

# Basic session state to preview added items
if 'preview_list' not in st.session_state:
    st.session_state.preview_list = []

# Simple Form in English
with st.form("expense_form", clear_on_submit=True):
    item_name = st.text_input("Item Name (e.g., Chicken, Paddy Milling):")
    amount = st.number_input("Amount (₹):", min_value=0.0, step=1.0)
    date_selected = st.date_input("Date:", datetime.today())
    submit_button = st.form_submit_button(label="Add Expense")

if submit_button and item_name and amount > 0:
    new_data = {
        "Date": date_selected.strftime("%d-%m-%Y"),
        "Item": item_name,
        "Amount (₹)": amount
    }
    st.session_state.preview_list.append(new_data)
    st.success(f"'{item_name}' successfully added! (Connecting to Sheet...)")
    
    # Note: To write directly into the sheet from Streamlit Cloud, 
    # we need to share the sheet with a Google Service Account email.
    st.info("To enable direct saving into Google Sheets, please let me know if you want to set up the Secrets configuration next.")

# Display the preview table
if st.session_state.preview_list:
    df = pd.DataFrame(st.session_state.preview_list)
    st.subheader("📋 Expense Ledger (Current Session)")
    st.dataframe(df, use_container_width=True)
    
    total_amount = df["Amount (₹)"].sum()
    st.markdown(f"### 💵 Grand Total: **₹{total_amount:.2f}**")
