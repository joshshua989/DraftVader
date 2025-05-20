# ---------------------- LIBRARIES ----------------------
import streamlit as st
import spike_week_score
# ---------------------- LIBRARIES ----------------------


st.subheader("📈 Spike Week Score")

# Calculates the Boom-Bust profile for players based on a list of seasons, specifically for the year
seasons = [2024]
df = spike_week_score.organize_by_condition(seasons)

# ---------------------- Display Cleanup Logic for UI ----------------------
# Format the percentage columns for display
formatted_merged = df.copy()
for col in formatted_merged.columns:
    if '_ppr_percentage' in col:
        formatted_merged[col] = formatted_merged[col].astype(str) + '%'

# Create a copy for display
display_df = formatted_merged.copy()

# Define a dictionary to rename columns for display
rename_dict = {
    'player_display_name': 'Player Name',
    'spike_week_score': 'Spike Score',
    'total_games': 'GP',
    'over_30_ppr_count': '>30 Pt Gm',
    'over_25_ppr_count': '>25 Pt Gm',
    'over_20_ppr_count': '>20 Pt Gm',
    'under_15_ppr_count': '<15 Pt Gm',
    'under_10_ppr_count': '<10 Pt Gm',
    'under_5_ppr_count': '<5 Pt Gm',
    'over_30_ppr_percentage': '>30 PPR %',
    'over_25_ppr_percentage': '>25 PPR %',
    'over_20_ppr_percentage': '>20 PPR %',
    'under_15_ppr_percentage': '<15 PPR %',
    'under_10_ppr_percentage': '<10 PPR %',
    'under_5_ppr_percentage': '<5 PPR %'
}

# Rename columns in the copy for display only
display_df.rename(columns=rename_dict, inplace=True)

# Display the formatted DataFrame
st.dataframe(display_df.sort_values(by='Spike Score', ascending=False), use_container_width=True, hide_index=True)

st.markdown("<p style='color: lightblue;'>🤖 "
            "<strong>DataFrame: All-Position 'Spike Week Score'</strong></p>", unsafe_allow_html=True)
# ---------------------- Display Cleanup Logic for UI ----------------------