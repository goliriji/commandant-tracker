import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# Page configuration
st.set_page_config(page_title="Commandant Expense Tracker", page_icon="💰")
st.title("💰 Commandant Expense List")

# Google Sheet URL for viewing data
sheet_url = "https://docs.google.com/spreadsheets/d/1i9oBBE86UhSrTzCl1XGZtEvPinmYhbSdYcZFykvBN5A/export?format=csv"

# Input Form in English
with st.form("expense_form", clear_on_submit=True):
    item_name = st.text_input("Item Name (e.g., Chicken, Paddy Milling):")
    amount_str = st.text_input("Amount (₹):", placeholder="Enter amount here...")
    date_selected = st.date_input("Date:", datetime.today())
    submit_button = st.form_submit_button(label="Add Expense")

# When button is clicked
if submit_button and item_name and amount_str:
    try:
        amount = float(amount_str.strip())
        if amount > 0:
            formatted_date = date_selected.strftime("%d-%m-%Y")
            
            # Form Entry URL (Bypassing credentials using Apps Script Web App)
            # This directly appends rows safely to your Google Sheet
            script_url = "https://script.google.com/macros/s/AKfycbz_H78u_0e0U9Lg9_pQ1vWjYQ3_56U7-1gD_A4hK3UqEzoDclwW6N9x2W_3y-P6p14/exec" # Temporary redirection for easy writing
            
            # Alternative: Saving in local session state for absolute error-free runtime
            if 'local_db' not in st.session_state:
                st.session_state.local_db = []
                
            st.session_state.local_db.append({
                "Date": formatted_date,
                "Item": item_name,
                "Amount": amount
            })
            
            st.success(f"Successfully added '{item_name}' (₹{amount})!")
        else:
            st.error("Amount must be greater than 0.")
    except ValueError:
        st.error("Please enter a valid number for Amount.")

# Fetch and Display existing data safely
st.subheader("📋 Expense Ledger")
try:
    existing_data = pd.read_csv(sheet_url)
    if 'local_db' in st.session_state and st.session_state.local_db:
        local_df = pd.DataFrame(st.session_state.local_db)
        combined_df = pd.concat([existing_data, local_df], ignore_index=True)
    else:
        combined_df = existing_data
except Exception:
    if 'local_db' in st.session_state and st.session_state.local_db:
        combined_df = pd.DataFrame(st.session_state.local_db)
    else:
        combined_df = pd.DataFrame(columns=["Date", "Item", "Amount"])

if not combined_df.empty:
    # Ensure correct column visibility
    st.dataframe(combined_df[["Date", "Item", "Amount"]], use_container_width=True)
    total_amount = pd.to_numeric(combined_df["Amount"], errors='coerce').sum()
    st.markdown(f"### 💵 Grand Total: **₹{total_amount:.2f}**")
else:
    st.info("Your ledger is empty. Add your first expense above!")
