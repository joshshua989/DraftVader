# ---------------------- Libraries ----------------------
import pandas as pd
import streamlit as st
# ---------------------- Libraries ----------------------


# ---------------------- Get Rookie Rankings - get_rookie_rankings(file_path) ----------------------
@st.cache_data
def get_rookie_rankings(file_path):

    # Check if the message has been shown before printing to terminal
    if 'rookie_rankings_shown' not in st.session_state:
        print("---------------------------------------------------------------")
        print(f"\n////////// Rookie Rankings //////////\n")
        print("---------------------------------------------------------------")
        st.session_state['rookie_rankings_shown'] = True

    # Define the expected headers
    expected_headers = ["RK", "PLAYER NAME", "TEAM", "POS", "AGE", "BEST", "WORST", "AVG.", "STD.DEV", "ECR VS. ADP"]

    # Load the CSV file
    df = pd.read_csv(file_path, names=expected_headers, header=0)

    # Show the first few rows
    print(df.head())
    print("---------------------------------------------------------------")

    return df
# ---------------------- Get Rookie Rankings - get_rookie_rankings(file_path) ----------------------