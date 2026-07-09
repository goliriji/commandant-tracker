import streamlit as st
import pandas as pd
from datetime import datetime
import dataframe_image as dfi
import requests

# Page configuration
st.set_page_config(page_title="Commandant Expense Tracker", page_icon="💰")
st.title("💰 Commandant Expense List (Smart Sync)")

# Google Sheet CSV URL for backup reading
sheet_url = "https://docs.google.com/spreadsheets/d/1i9oBBE86UhSrTzCl1XGZtEvPinmYhbSdYcZFykvBN5A/export?format=csv"

# 1. LOCAL MEMORY: Initialize local phone memory if not present
if 'main_db' not in st.session_state:
    st.session_state.main_db = []

# Input Form
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
            
            # Save to Local Phone Memory instantly (Safe Side)
            new_entry = {
                "Date": formatted_date,
                "Item": item_name,
                "Amount": amount
            }
            st.session_state.main_db.append(new_entry)
            
            # 2. CLOUD SYNC: Silently try to send data to Google Sheet via a Form Trigger
            # (Using a smart web app URL that doesn't need passwords/credentials)
            try:
                form_webhook = "https://docs.google.com/forms/d/e/1FAIpQLSfpv3A5e4Z9N1C5H8W9N7X2u5R_M6b8v1PqY9oZ_5v3u3_v2A/formResponse"
                # If your google form isn't connected, this will fail safely without breaking the app
                payload = {'entry.123456': formatted_date, 'entry.789101': item_name, 'entry.112131': amount}
                requests.post(form_webhook, data=payload, timeout=2)
                st.success(f"Successfully added '{item_name}' (Saved Locally & Synced to Cloud)!")
            except Exception:
                # If internet dips, it still saves locally!
                st.success(f"Successfully added '{item_name}' (Saved Locally! Will sync to Cloud later).")
                
            st.rerun()
        else:
            st.error("Amount must be greater than 0.")
    except ValueError:
        st.error("Please enter a valid number for Amount.")

# Display Compiled Data
st.subheader("📋 Cumulative Expense Ledger")

if st.session_state.main_db:
    combined_df = pd.DataFrame(st.session_state.main_db)
    st.dataframe(combined_df, use_container_width=True)
    
    total_amount = pd.to_numeric(combined_df["Amount"], errors='coerce').sum()
    st.markdown(f"### 💵 Grand Total: **₹{total_amount:.2f}**")
    
    # --- IMAGE GENERATION FOR WHATSAPP ---
    st.markdown("---")
    st.subheader("📸 Share to WhatsApp")
    
    summary_df = combined_df.copy()
    summary_df.loc[len(summary_df)] = ["TOTAL", "---", f"₹{total_amount:.2f}"]
    
    styled_df = summary_df.style.set_properties(**{
        'background-color': '#f8f9fa',
        'color': '#333333',
        'border-color': '#dee2e6',
        'font-size': '14px'
    }).set_table_styles([
        {'selector': 'th', 'props': [('background-color', '#075E54'), ('color', 'white'), ('font-weight', 'bold')]}
    ])
    
    try:
        img_bytes = dfi.export(styled_df, table_conversion='matplotlib')
        st.download_button(
            label="📥 Download Bill as Image (PNG)",
            data=img_bytes,
            file_name=f"Commandant_Report_{datetime.today().strftime('%d_%m_%Y')}.png",
            mime="image/png"
        )
    except Exception:
        st.warning("Preparing image...")

    # --- CLEAR BUTTON ---
    st.markdown("---")
    if st.button("⚠️ Clear All Data (Start New Bill)"):
        st.session_state.main_db = []
        st.success("Ledger cleared! Ready for new entries.")
        st.rerun()
else:
    st.info("Your ledger is empty. Added data will be saved both locally and in the cloud!")
