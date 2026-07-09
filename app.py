import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Page layout
st.set_page_config(page_title="Commandant Expense Tracker", page_icon="💰")
st.title("💰 Commandant Expense List")

# Google Sheet URL provided by you
sheet_url = "https://docs.google.com/spreadsheets/d/1i9oBBE86UhSrTzCl1XGZtEvPinmYhbSdYcZFykvBN5A/edit?usp=drivesdk"

# Create a connection to your Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

# Read existing expenses from the sheet
try:
    existing_data = conn.read(spreadsheet=sheet_url, usecols=[0, 1, 2])
    existing_data = existing_data.dropna(how="all")
except Exception:
    existing_data = pd.DataFrame(columns=["Date", "Item", "Amount"])

# Input Form in English
with st.form("expense_form", clear_on_submit=True):
    item_name = st.text_input("Item Name (e.g., Chicken, Paddy Milling):")
    
    # CHANGED: Using text_input with a placeholder so it stays completely BLANK!
    amount_str = st.text_input("Amount (₹):", placeholder="Enter amount here...")
    
    date_selected = st.date_input("Date:", datetime.today())
    submit_button = st.form_submit_button(label="Add Expense")

# When you click the add button
if submit_button and item_name and amount_str:
    try:
        # Convert the text input into a clean number
        amount = float(amount_str.strip())
        
        if amount > 0:
            new_row = pd.DataFrame([{
                "Date": date_selected.strftime("%d-%m-%Y"),
                "Item": item_name,
                "Amount": amount
            }])
            
            # Combine old data with new data
            updated_data = pd.concat([existing_data, new_row], ignore_index=True)
            
            # Save back to your Google Sheet instantly
            conn.update(spreadsheet=sheet_url, data=updated_data)
            st.success(f"Successfully added '{item_name}' to Google Sheets!")
            st.rerun()
        else:
            st.error("Amount must be greater than 0.")
    except ValueError:
        st.error("Please enter a valid number for Amount.")

# Display the data directly fetched from Google Sheet
st.subheader("📋 Expense Ledger")
if not existing_data.empty:
    st.dataframe(existing_data, use_container_width=True)
    total_amount = pd.to_numeric(existing_data["Amount"], errors='coerce').sum()
    st.markdown(f"### 💵 Grand Total: **₹{total_amount:.2f}**")
else:
    st.info("Your Google Sheet is empty. Add your first expense above!")
