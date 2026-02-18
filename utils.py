import pandas as pd
import os
from datetime import datetime
import streamlit as st
from streamlit_gsheets import GSheetsConnection

def load_data(filepath):
    """
    Loads data from Google Sheets if configured, otherwise falls back to CSV.
    Returns: (DataFrame, Source String, Error String)
    """
    try:
        # Try to connect to Google Sheets
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read()
        
        # Ensure timestamp is datetime
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='mixed', errors='coerce')
            
        return df, "Google Sheets", None
    except Exception as e:
        error_msg = str(e)
        # Fallback to CSV
        if not os.path.exists(filepath):
            return pd.DataFrame(columns=['Timestamp', 'Name', 'Happiness Score', 'Factors', 'Notes']), "Local CSV", error_msg
        
        try:
            df = pd.read_csv(filepath)
            if 'Timestamp' in df.columns:
                df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='mixed', errors='coerce')
            return df, "Local CSV", error_msg
        except Exception:
            return pd.DataFrame(columns=['Timestamp', 'Name', 'Happiness Score', 'Factors', 'Notes']), "Local CSV", error_msg

def save_entry(filepath, entry_dict):
    """
    Saves a new entry to Google Sheets if configured, otherwise falls back to CSV.
    """
    # Add timestamp
    entry_dict['Timestamp'] = datetime.now()
    new_entry_df = pd.DataFrame([entry_dict])
    
    # Try Google Sheets first
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        existing_data = conn.read()
        updated_df = pd.concat([existing_data, new_entry_df], ignore_index=True)
        conn.update(data=updated_df)
        return True
    except Exception as e:
        print(f"⚠️ Google Sheets Error: {e}")
        # Fallback to CSV logic
        if os.path.exists(filepath):
            try:
                existing_df = pd.read_csv(filepath)
                updated_df = pd.concat([existing_df, new_entry_df], ignore_index=True)
                updated_df.to_csv(filepath, index=False)
            except Exception:
                new_entry_df.to_csv(filepath, mode='a', header=False, index=False)
        else:
            new_entry_df.to_csv(filepath, mode='w', header=True, index=False)
        return False
