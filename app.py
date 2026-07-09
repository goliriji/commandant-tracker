import streamlit as st
import pandas as pd
from datetime import datetime
import dataframe_image as dfi
import io

# Page configuration
st.set_page_config(page_title="Commandant Expense Tracker", page_icon="💰")
st.title("💰 Commandant Expense List")

# Google Sheet URL for viewing data
sheet_url = "https://docs.google.com/spreadsheets/d/1i9oBBE86UhSrTzCl1XGZtEvPinmYhbSdYcZFykvBN5A/export?format=csv"

# Input Form
with st.form("expense_form", clear_on_submit=True):
    item_name = st.text_input("Item Name (e.g., Chicken, Paddy Milling):")
    amount_str = st.text_input("Amount (₹):", placeholder="Enter amount here...")
    date_selected = st.date_input("Date:", datetime.today())
    submit_button = st.form_submit_button(label="Add Expense")

if submit_button and item_name and amount_str:
    try:
        amount = float(amount_str.strip())
        if amount > 0:
            formatted_date = date_selected.strftime("%d-%m-%Y")
            
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

# Fetch and Display existing data
st.subheader("📋 Expense Ledger")
try:
    combined_df = pd.read_csv(sheet_url)
    if 'local_db' in st.session_state and st.session_state.local_db:
        local_df = pd.DataFrame(st.session_state.local_db)
        combined_df = pd.concat([combined_df, local_df], ignore_index=True)
except Exception:
    if 'local_db' in st.session_state and st.session_state.local_db:
        combined_df = pd.DataFrame(st.session_state.local_db)
    else:
        combined_df = pd.DataFrame(columns=["Date", "Item", "Amount"])

if not combined_df.empty:
    final_df = combined_df[["Date", "Item", "Amount"]].copy()
    st.dataframe(final_df, use_container_width=True)
    
    total_amount = pd.to_numeric(final_df["Amount"], errors='coerce').sum()
    st.markdown(f"### 💵 Grand Total: **₹{total_amount:.2f}**")
    
    # --- MAGIC IMAGE GENERATION CODE ---
    st.markdown("---")
    st.subheader("📸 Share to WhatsApp")
    
    # Create a nice summary row at the bottom of the dataframe for the final image
    summary_df = final_df.copy()
    summary_df.loc[len(summary_df)] = ["TOTAL", "---", f"₹{total_amount:.2f}"]
    
    # Styling the table so it looks like a beautiful bill image
    styled_df = summary_df.style.set_properties(**{
        'background-color': '#f8f9fa',
        'color': '#333333',
        'border-color': '#dee2e6',
        'font-size': '14px'
    }).set_table_styles([
        {'selector': 'th', 'props': [('background-color', '#075E54'), ('color', 'white'), ('font-weight', 'bold')]}
    ])
    
    # Convert dataframe to PNG image bytes
    try:
        img_bytes = dfi.export(styled_df, table_conversion='matplotlib')
        
        # Download Button for the Image
        st.download_button(
            label="📥 Download Bill as Image (PNG)",
            data=img_bytes,
            file_name=f"Expense_Report_{datetime.today().strftime('%d_%m_%Y')}.png",
            mime="image/png"
        )
        st.caption("Tip: After downloading, just open WhatsApp and share this image from your gallery directly to the Commandant!")
    except Exception as e:
        st.warning("Generating image button... please refresh if it takes too long.")
else:
    st.info("Your ledger is empty. Add your first expense above!")
