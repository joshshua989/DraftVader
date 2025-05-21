# ---------------------- LIBRARIES ----------------------
import streamlit as st
from load_data import load_nfl_player_data
# ---------------------- LIBRARIES ----------------------


# ---------------------- NFL Player Data - loaded from .csv files ----------------------
st.subheader("🏛️ NFL Historical Data")

# Create four columns
col1, col2, col3, col4 = st.columns(4)

# Add the text input to the first column
with col1:
    # The specific selectbox
    selected_season = st.selectbox("Select Season:", ['2024', '2023', '2022'])

# Leave the other three columns blank
with col2:
    st.empty()
with col3:
    st.empty()
with col4:
    st.empty()

# Check if the Boom-Bust message has been shown before printing to terminal
if 'nfl_player_data_shown' not in st.session_state:
    print("---------------------------------------------------------------")
    print(f"\n////////// {selected_season} NFL Player Data //////////\n")
    st.session_state['nfl_player_data_shown'] = True

# Set the directory where the data files are located
data_folder = './'

# Load the appropriate file based on season
file_name = f"data_files/nfl_player_stats_{selected_season}.csv"

# Load and display the data
data = load_nfl_player_data(data_folder, file_name)

st.markdown(f"<p style='color: lightblue;'>🤖 "
            f"<strong>Displaying historical data for season: {selected_season}"
            f"</strong></p>", unsafe_allow_html=True)
st.write("")

# Display filtered data
display_headers = {
    'rank': 'Rank', 'player': 'Player', 'team': 'Team', 'pos': 'Pos', 'age': 'Age', 'games': 'Games',
    'games_started': 'Started', 'cmp': 'CMP', 'pass_att': 'Pass Att', 'pass_yds': 'Pass Yds', 'pass_td': 'Pass TDs',
    'int': 'Int', 'rush_att': 'Rush Att', 'rush_yds': 'Rush Yds', 'yds_per_att': 'Yds/Att', 'rush_td': 'Rush TDs',
    'tgt': 'Tgts', 'rec': 'Rec', 'rec_yds': 'Rec Yds', 'yds_per_rec': 'Yds/Rec', 'rec_td': 'Rec TDs', 'fmb': 'Fmb',
    'fmb_lost': 'Fmb Lost', 'total_td': 'Ttl TDs', 'two_pt_made': '2-Pt Made', 'two_pt_pass': '2-Pt Pass',
    'fantasy_pts': 'Fantasy Pts', 'ppr_pts': 'PPR Pts', 'draftkings_pts': 'DK Pts', 'fanduel_pts': 'FD Pts',
    'value_based_draft': 'Value Based Draft', 'pos_rank': 'Pos Rank', 'ovr_rank': 'Ovr Rank'
}

# Rename columns for display
data = data.rename(columns=display_headers)

# Create four columns
col1, col2, col3 = st.columns(3)

isResults = False

with col1:
    # Search for a player by name (example: 'Jared Goff')
    if data is not None:
        # Applying the CSS class to the text input
        player_name = st.text_input("Search for NFL players by name:", key="player_name",
                                    placeholder="Enter player name")

        if player_name:  # Only execute when input is not empty
            try:
                # Filter the DataFrame for rows where the player name contains the search term (case-insensitive)
                results = data[data['Player'].str.contains(player_name, case=False, na=False)]
                if not results.empty:
                    isResults = True
                else:
                    st.warning(f"No results found for '{player_name}'.")
            except KeyError:
                st.warning("The 'Player' column is not found in the data.")

# Leave the other two columns blank
with col2:
    st.empty()
with col3:
    st.empty()

if isResults:
    st.write(f"Found {len(results)} result(s) for '{player_name}':")

    # Base row height and buffer
    base_row_height = 35  # Estimate per row
    scrollbar_buffer = 60  # Extra space for scrollbar

    # Calculate dynamic height
    rows = len(results)
    raw_height = int(rows * base_row_height)
    padded_height = int(raw_height + scrollbar_buffer)

    st.dataframe(results, height=padded_height, use_container_width=True, hide_index=True)

# Display filtered data
st.dataframe(data, hide_index=True)

st.markdown('<p style="font-size:13px;">(*) Selected to Pro Bowl, (+) First-Team All-Pro</p>', unsafe_allow_html=True)
# ---------------------- NFL Player Data - loaded from .csv files ----------------------