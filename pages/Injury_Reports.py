# ---------------------- LIBRARIES ----------------------
import pandas as pd
import streamlit as st
# ---------------------- LIBRARIES ----------------------


# ---------------------- Initialize Session State ----------------------
# 2024 NFL Player Stats DataFrame
if 'nfl_player_stats_2024_df' in st.session_state:
    nfl_player_stats_2024_df = st.session_state['nfl_player_stats_2024_df']
else:
    st.write("No DataFrame found in session_state.")

# Rookie Rankings DataFrame
if 'rookie_rankings_df' in st.session_state:
    rookie_rankings_df = st.session_state['rookie_rankings_df']
    rookie_names = rookie_rankings_df['PLAYER NAME'].dropna().unique()
    rookie_name_set = set(name.lower() for name in rookie_names)
else:
    rookie_names = []
    rookie_name_set = set()
    st.warning("No rookie rankings data found in session_state.")
# ---------------------- Initialize Session State ----------------------


# ---------------------- All Injuries DataFrame ----------------------
st.subheader("🏥 All Injury Reports")

# Display with friendly column names
display_df = st.session_state.injury_reports_df.rename(columns={
    "player_name": "Player Name",
    "headline": "Headline",
    "date": "Date",
    "description": "News Summary",
    "fantasy_impact": "Fantasy Impact"
})

# Output as a dataframe:
st.dataframe(display_df, use_container_width=True, hide_index=True)
# ---------------------- All Injuries DataFrame ----------------------

# ---------------------- Relevant Injuries DataFrame ----------------------
# Custom CSS for clean card layout
st.markdown("""
<style>
.news-card {
    background-color: #f9f9f9;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    border: 1px solid #eee;
    font-family: 'Segoe UI', sans-serif;
}
.news-title {
    font-size: 18px;
    font-weight: bold;
    color: #333;
}
.news-date {
    font-size: 14px;
    color: #888;
    margin-bottom: 10px;
}
.news-description {
    font-size: 16px;
    color: #444;
    margin-bottom: 8px;
}
.news-impact {
    font-size: 15px;
    font-style: italic;
    color: #555;
}
</style>
""", unsafe_allow_html=True)

# Filter to top 320 players by overall rank and positions QB, RB, WR, TE
filtered_df = nfl_player_stats_2024_df[nfl_player_stats_2024_df['pos'].isin(['QB', 'RB', 'WR', 'TE'])]
sorted_df = filtered_df.sort_values('ovr_rank').reset_index(drop=True)
top_320_players_df = sorted_df.head(320)

# Combine top 320 player names and rookie names
top_player_names = top_320_players_df['player'].dropna().unique()
all_relevant_player_names = list(set(top_player_names) | set(rookie_names))

# Filter the injury reports to only include rows where the player name is in all_relevant_player_names
# Assuming the injury_reports_df has a 'player_name' or similar column for matching players

# First, check if 'player_name' column exists in injury_reports_df
if 'player_name' in st.session_state.injury_reports_df.columns:
    relevant_injuries_df = st.session_state.injury_reports_df[
        st.session_state.injury_reports_df['player_name'].str.lower().isin([name.lower() for name in all_relevant_player_names])
    ].reset_index(drop=True)
else:
    # If no player_name column, display warning and empty dataframe
    st.warning("Injury reports DataFrame does not have a 'player_name' column to filter relevant players.")
    relevant_injuries_df = pd.DataFrame()

# Display the filtered dataframe with renamed columns for clarity
display_relevant_df = relevant_injuries_df.rename(columns={
    "headline": "Headline",
    "date": "Date",
    "description": "News Summary",
    "fantasy_impact": "Fantasy Impact"
})

st.subheader("🩹 Relevant Injury Reports for QB, RB, WR, TE & Rookies")

if not relevant_injuries_df.empty:
    for _, row in relevant_injuries_df.iterrows():
        st.markdown(f"""
        <div class="news-card">
            <div class="news-title">{row['headline']}</div>
            <div class="news-date">{row['date']}</div>
            <div class="news-description">{row['description']}</div>
            <div class="news-impact">Fantasy Impact: {row['fantasy_impact']}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No relevant injury news for top players or rookies at this time.")
# ---------------------- Relevant Injuries DataFrame ----------------------