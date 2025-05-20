# ---------------------- LIBRARIES ----------------------
from datetime import datetime
from datetime import date
import pandas as pd
import streamlit as st
from player_transactions import get_player_transactions
# ---------------------- LIBRARIES ----------------------


# ---------------------- Initialize Session State ----------------------
# 2024 NFL Player Stats DataFrame
if 'nfl_player_stats_2024_df' in st.session_state:
    nfl_player_stats_2024_df = st.session_state['nfl_player_stats_2024_df']
else:
    st.write("No DataFrame found in session_state.")
# ---------------------- Initialize Session State ----------------------


# -------------------------------------------- Player Transactions --------------------------------------------
st.subheader("📝 Player Transactions")

current_year = datetime.now().year
current_month_int = datetime.now().month

# Dictionary to hold monthly transactions
player_transactions_by_month = {}

# Build list of valid months up to current month for the current year
months_list = [datetime(current_year, m, 1).strftime('%B') for m in range(1, current_month_int + 1)]

current_month_name = datetime.now().strftime('%B')
try:
    default_index = months_list.index(current_month_name)
except ValueError:
    default_index = 0  # fallback

# Create four columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    today = date.today()
    st.write(today)
    selected_month = st.selectbox("Select a month:", months_list, index=default_index)

# Leave the other three columns blank
with col2:
    st.empty()
with col3:
    st.empty()
with col4:
    st.empty()

# Loop through valid months and load transactions
for month in range(1, current_month_int + 1):
    month_str = f"{month:02}"
    url = f"https://www.pro-football-reference.com/years/{current_year}/{month_str}_transactions.htm"
    transactions = get_player_transactions(month_str, url)
    month_name = datetime.strptime(month_str, "%m").strftime("%B")
    player_transactions_by_month[month_name] = transactions

# Get transactions for the selected month
selected_month_transactions = player_transactions_by_month.get(selected_month)
st.write(f"All player transactions for {selected_month}, {current_year}:")
st.dataframe(selected_month_transactions, use_container_width=True, hide_index=True)

# ---------------------- Relevant Transactions DataFrame ----------------------
# Filter to top 320 players by overall rank and positions QB, RB, WR, TE
filtered_df = nfl_player_stats_2024_df[nfl_player_stats_2024_df['pos'].isin(['QB', 'RB', 'WR', 'TE'])]
sorted_df = filtered_df.sort_values('ovr_rank').reset_index(drop=True)
top_320_players_df = sorted_df.head(320)

# Check if any player name appears in the selected transaction text
matched_transactions = []
top_player_names = top_320_players_df['player'].unique()

# Helper to extract core first and last name, ignoring suffixes
suffixes = {"jr", "sr", "ii", "iii", "iv", "v"}
def extract_first_last(name):
    parts = name.lower().split()
    parts = [part for part in parts if part.strip('.').lower() not in suffixes]
    if len(parts) >= 2:
        return parts[0], parts[-1]
    return parts[0], ""

# Process each transaction
for idx, row in selected_month_transactions.iterrows():
    transaction_text = row['Transaction']
    transaction_text_lower = transaction_text.lower()
    for player_name in top_player_names:
        first, last = extract_first_last(player_name)
        if first in transaction_text_lower and last in transaction_text_lower:
            matched_transactions.append(row)
            break

# Create and display relevant transactions, hide 'id' column
relevant_transactions_df = pd.DataFrame(matched_transactions)
st.write(f"Player transactions for {selected_month}, {current_year}, sorted for relevance:")
st.dataframe(relevant_transactions_df, use_container_width=True, hide_index=True)
# ---------------------- Relevant Transactions DataFrame ----------------------
# -------------------------------------------- Player Transactions --------------------------------------------