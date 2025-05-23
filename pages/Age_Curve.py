# ---------------------- LIBRARIES ----------------------
import pandas as pd
import streamlit as st
from age_curve import apply_age_curve
# ---------------------- LIBRARIES ----------------------


# ---------------------- Initialize Session State ----------------------
# 2024 NFL Player Stats DataFrame
if 'age_curve_df' in st.session_state:
    age_curve_df = st.session_state['age_curve_df']
else:
    # Load the 2024 NFL Player stats .csv file - (must be above Player_Transactions.py data pulls)
    nfl_player_stats_2024_df = pd.read_csv('data_files/nfl_player_stats_2024.csv')
    # Remove + and * from player names
    nfl_player_stats_2024_df['player'] = nfl_player_stats_2024_df['player'].str.replace(r'[\+\*]', '', regex=True)
    age_curve_mult_df = apply_age_curve(nfl_player_stats_2024_df)
    st.session_state['age_curve_df'] = age_curve_mult_df
# ---------------------- Initialize Session State ----------------------

# ---------------------- Age Curve DataFrame ----------------------
st.subheader("🧮 Age Curve Multiplier")

# Display with friendly column names
display_df = st.session_state.age_curve_df.rename(columns={
    "player": "Player Name",
    "team": "Team",
    "pos": "Pos",
    "age": "Age",
    "age_curve_multiplier": "Multiplier",
    "age_risk_tag": "Risk Tag"
})

# Sort by age_curve_multiplier and reset index
display_df = display_df.sort_values(by='Multiplier', ascending=False)

# Output as a dataframe:
st.dataframe(display_df, use_container_width=True, hide_index=True)
# ---------------------- Age Curve DataFrame ----------------------