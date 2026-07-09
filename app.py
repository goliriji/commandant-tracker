import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import io

# Page configuration
st.set_page_config(page_title="Commandant Expense Tracker", page_icon="💰")
st.title("💰 Commandant Expense List (Super Fast)")

# Initialize session state for memory
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
            st.session_state.main_db.append({
                "Date": formatted_date,
                "Item": item_name,
                "Amount": amount
            })
            st.success(f"Successfully added '{item_name}' (₹{amount})!")
            st.rerun()
        else:
            st.error("Amount must be greater than 0.")
    except ValueError:
        st.error("Please enter a valid number for Amount.")

# Display Data
st.subheader("📋 Cumulative Expense Ledger")

if st.session_state.main_db:
    combined_df = pd.DataFrame(st.session_state.main_db)
    st.dataframe(combined_df, use_container_width=True)
    
    total_amount = pd.to_numeric(combined_df["Amount"], errors='coerce').sum()
    st.markdown(f"### 💵 Grand Total: **₹{total_amount:.2f}**")
    
    # --- NEW SUPER FAST IMAGE GENERATION CODE ---
    st.markdown("---")
    st.subheader("📸 Share to WhatsApp")
    
    try:
        # Create a clean image using Matplotlib (Lightning Fast)
        fig, ax = plt.subplots(figsize=(6, len(combined_df) * 0.5 + 1.5))
        ax.axis('tight')
        ax.axis('off')
        
        # Prepare data for the image table
        img_data = combined_df.copy()
        img_data.loc[len(img_data)] = ["TOTAL", "---", f"₹{total_amount:.2f}"]
        
        # Draw table
        table = ax.table(cellText=img_data.values, colLabels=img_data.columns, cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.2, 1.5)
        
        # Style headers with Dark Teal / Green Color
        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_text_props(weight='bold', color='white')
                cell.set_facecolor('#075E54')
            elif row == len(img_data):
                cell.set_text_props(weight='bold')
                cell.set_facecolor('#e9ecef')
        
        # Save table to bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=200)
        buf.seek(0)
        img_bytes = buf.getvalue()
        plt.close(fig)
        
        # Download Button (Appears Instantly!)
        st.download_button(
            label="📥 Download Bill as Image (PNG)",
            data=img_bytes,
            file_name=f"Commandant_Report_{datetime.today().strftime('%d_%m_%Y')}.png",
            mime="image/png"
        )
    except Exception as e:
        st.error("Error creating image. Please contact support.")

    # --- CLEAR BUTTON ---
    st.markdown("---")
    if st.button("⚠️ Clear All Data (Start New Bill)"):
        st.session_state.main_db = []
        st.success("Ledger cleared!")
        st.rerun()
else:
    st.info("Your ledger is empty. Added data will be saved here safely!")
