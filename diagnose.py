import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import sys

st.title("GSheets Diagnosis")

try:
    with st.spinner("Connecting..."):
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read()
        st.success("SUCCESS! Connected to Google Sheets.")
        st.write("Row count:", len(df))
        st.dataframe(df)
        print("DIAGNOSIS_SUCCESS")
except Exception as e:
    st.error(f"FAILURE: {e}")
    print(f"DIAGNOSIS_FAILURE: {e}")
