# ---------------------- LIBRARIES ----------------------
import os
import psutil
import signal
import math
import pandas as pd
import streamlit as st
from load_data import load_nfl_player_data, get_adp_data, get_season_projections_qb, get_season_projections_rb
from load_data import get_season_projections_wr, get_season_projections_te
import implied_points
import boom_bust_profile
# ---------------------- LIBRARIES ----------------------


# ---------------------- PAGE CONFIGURATION ----------------------
# Streamlit function call used to configure the page settings - sets up the page title and icon for the Streamlit app
# This function call should be placed at the very beginning of your Streamlit script.
st.set_page_config(
    page_title="DraftVader v1.0",
    page_icon="🤖"
)
# ---------------------- PAGE CONFIGURATION ----------------------


# ---------------------- SHUTDOWN (Development) ----------------------
def shutdown():
    pid = os.getpid()
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        child.send_signal(signal.SIGTERM)
    parent.send_signal(signal.SIGTERM)

# Use columns to center the shutdown button
col1, col2, col3 = st.columns([2, 1, 2])

# Add the shutdown button for local testing
with col2:
    if st.button("🔴 Shut Down"):
        st.warning("Shutting down the app...")
        shutdown()
# ---------------------- SHUTDOWN (Development) ----------------------


# ---------------------- Initialize Session State ----------------------
# function to initialize the session state variables
def initialize_session_state():
    defaults = {
        # Creates a dictionary with keys "Team 1" to "Team 12", each mapped to an empty list.
        # This represents the draft picks for each of the 12 teams.
        "teams": {f"Team {i+1}": [] for i in range(12)},
        # A list of integers from 1 to 12, representing the draft pick order.
        "pick_order": list(range(1, 13)),
        # An integer representing the current pick number, starting from 0.
        "pick_number": 0,
        # Stores the last drafted player, initially set to None.
        "last_pick": None,
        # Stores the last team that picked, initially set to None.
        "last_team": None,
    }
    # The for loop iterates over each key-value pair in the defaults dictionary:
    for key, value in defaults.items():
        if key not in st.session_state: # Checks if the key is already in st.session_state.
            st.session_state[key] = value # If not, it sets the key in the session state with the corresponding value.
# ---------------------- Initialize Session State ----------------------


# ---------------------- Style ----------------------
def apply_df_scrollbar_style():
    # Inject custom CSS for a high-contrast scrollbar
    st.markdown("""
        <style>
        /* Make the scrollbar wider */
        ::-webkit-scrollbar {
            width: 18px;
            height: 18px;
        }

        /* Track */
        ::-webkit-scrollbar-track {
            background: #333;  /* Dark background for contrast */
        }

        /* Handle */
        ::-webkit-scrollbar-thumb {
            background: #555;  /* Medium gray for visibility */
            border-radius: 10px;
            border: 3px solid #222;  /* Darker border for separation */
        }

        /* Handle on hover */
        ::-webkit-scrollbar-thumb:hover {
            background: #777;  /* Slightly lighter for hover effect */
        }
        </style>
    """, unsafe_allow_html=True)
    
# Define a function to format text with larger font size and bold label
def format_player_overview_stat(label, value):
    return f"<p style='font-size:16px; font-weight:bold;'>{label}:</p> <p style='font-size:14px;'>{value}</p>"

# customizes the visual appearance of all select boxes in the app by injecting CSS through the st.markdown() function.
def apply_selectbox_style():
    st.markdown( # Uses st.markdown() to insert raw HTML and CSS.
                 # e.g., "st.markdown("""<style>...</style>""", unsafe_allow_html=True)"
        """
        <style>
        .stSelectbox > div[data-baseweb="select"] {
            min-height: 35px;
            max-width: 300px;
        }
        .stSelectbox label {
            font-size: 14px;
            margin-bottom: 0.2rem;
        }
        </style>
        """,
        unsafe_allow_html=True # enable HTML rendering, which is disabled by default for security reasons.
    )
# ---------------------- Style Functions ----------------------


# ---------------------- HEADER ----------------------
# Print styled header
title = "🏈 DRAFT VADER 1.0" # 🗣
st.markdown(
        f"<h1 style='text-align: center; font-size: 48px; color: #0098f5;'>{title}</h1>",
        unsafe_allow_html=True
    )
st.write("")
st.markdown("<p style='color: lightblue;'>🤖 "
            "<strong>"
                "Welcome to NFL Best Ball Draft 2025!"
            "</strong></p>", unsafe_allow_html=True)
st.markdown("<p style='color: lightblue;'>🤖 "
            "<strong>I will be your personal AI assistant for the draft!</strong></p>", unsafe_allow_html=True)
st.write("---")
# ---------------------- HEADER ----------------------


# ---------------------- Button Callbacks ----------------------
def next_pick():
    st.session_state.last_pick = None
    st.session_state.last_team = None
    st.session_state.pick_number += 1

def undo_last_pick():
    if st.session_state.last_team and st.session_state.last_pick in st.session_state.teams[st.session_state.last_team]:
        st.session_state.teams[st.session_state.last_team].remove(st.session_state.last_pick)
        st.session_state.last_pick = None
        st.session_state.last_team = None
# ---------------------- Button Callbacks ----------------------


# ---------------------- Script Functions ----------------------
# Ensures that the draft follows a snake format, where the draft order reverses after each round.
def get_team_picking():
    # st.session_state.pick_number is the current pick number in the draft.
    # len(st.session_state.pick_order) gives the total number of teams.
    # The // operator performs integer division to calculate the current round number.
    round_number = st.session_state.pick_number // len(st.session_state.pick_order) # determine round (e.g., "round 1")
    # Uses the modulus operator % to find the position within the current round.
    # This effectively determines the index within the list of teams.
    pick_in_round = st.session_state.pick_number % len(st.session_state.pick_order) # determine the position
                                                                                    # (e.g., "round 2, pick 4")
    # Checks whether the round number is even or odd.
    # If even, it returns the team from pick_order at the calculated index.
    # If odd, it returns the team from the reversed order ([::-1]) at the same index.
    # This logic ensures that the draft follows a snake format, where the order reverses after each round.
    if round_number % 2 == 0:
        return st.session_state.pick_order[pick_in_round] # Even round: normal order
    else:
        return st.session_state.pick_order[::-1][pick_in_round] # Odd round: reversed order

def build_team_roster(team_picks):
    starters = {"QB": [], "RB": [], "WR": [], "TE": [], "FLEX": []}
    bench = []
    detailed_picks = []
    for p_name in team_picks:
        player_info = next((p for p in adp_rankings if p['name'] == p_name), None)
        if player_info:
            detailed_picks.append(player_info)

    detailed_picks.sort(key=lambda p: p['adp'])

    for player in detailed_picks:
        pos = player['pos']
        if pos == "QB" and len(starters["QB"]) < 1:
            starters["QB"].append(player)
        elif pos == "RB" and len(starters["RB"]) < 2:
            starters["RB"].append(player)
        elif pos == "WR" and len(starters["WR"]) < 3:
            starters["WR"].append(player)
        elif pos == "TE" and len(starters["TE"]) < 1:
            starters["TE"].append(player)
        elif pos in ["RB", "WR", "TE"] and len(starters["FLEX"]) < 1:
            starters["FLEX"].append(player)
        else:
            bench.append(player)
    return starters, bench

# creates and returns a list of players who have not been drafted yet, sorted by their ADP from high to low
def get_available_players(players_2025):
    taken = [p for picks in st.session_state.teams.values() for p in picks]
    return sorted(
        [p for p in players_2025 if p['name'] not in taken],
        key=lambda x: x['adp'], reverse=True
    )
    # Example: If there are 4 teams (pick_order = [A, B, C, D]):
    # Round 1 (even): A -> B -> C -> D
    # Round 2 (odd): D -> C -> B -> A
    # Round 3 (even): A -> B -> C -> D
    # And so on...
# ---------------------- Script Functions ----------------------


# -------------------------------------------- DATA HANDLING - (BEGIN) --------------------------------------------
# Initialize session state variables to ensure they have default values before the user interacts with the app.
initialize_session_state()

# Check if the Data Scraping message has been shown before PRINTING MESSAGE TO TERMINAL
if 'data_scraping_shown' not in st.session_state:
    print("\n////////// DATA SCRAPING //////////\n")
    st.session_state['data_scraping_shown'] = True

# Scrape NFL Player data from Pro-Football-Reference.com
# years = [2022, 2023, 2024]
# for year in years:
#     get_nfl_player_data(year, f"https://www.pro-football-reference.com/years/{year}/fantasy.htm")

# ---------------------- NFL Player Data CSV Files ----------------------
# Load the 2024 NFL Player data CSV file
nfl_player_data_2024 = pd.read_csv('nfl_player_data_2024.csv')
# Remove + and * from player names
nfl_player_data_2024['player'] = nfl_player_data_2024['player'].str.replace(r'[\+\*]', '', regex=True)

# Load the 2023 NFL Player data CSV file
nfl_player_data_2023 = pd.read_csv('nfl_player_data_2023.csv')
# Remove + and * from player names
nfl_player_data_2023['player'] = nfl_player_data_2023['player'].str.replace(r'[\+\*]', '', regex=True)

# Load the 2022 NFL Player data CSV file
nfl_player_data_2022 = pd.read_csv('nfl_player_data_2022.csv')
# Remove + and * from player names
nfl_player_data_2022['player'] = nfl_player_data_2022['player'].str.replace(r'[\+\*]', '', regex=True)
# ---------------------- NFL Player Data CSV Files ----------------------

# ---------------------- ADP Rankings ----------------------
# calls load_adp_data() function and stores a list of dictionaries in the adp_rankings variable
# [{'rank': rank, 'name': name, 'pos': pos, 'adp': adp}, ...]
adp_rankings = get_adp_data('https://www.fantasypros.com/nfl/adp/best-ball-overall.php')
# ---------------------- ADP Rankings ----------------------

# ---------------------- Season Projections ----------------------
# [{'name': name, 'team': team, 'pass_att': pass_att, 'pass_cmp': pass_cmp, 'pass_yds': pass_yds, 'pass_tds': pass_tds,
#     'ints': ints, 'rush_att': rush_att, 'rush_yds': rush_yds, 'rush_tds': rush_tds, 'fumbles': fumbles,
#     'proj_points': proj_points}]
season_projections_qb = get_season_projections_qb('https://www.fantasypros.com/nfl/projections/qb.php?week=draft')
# [{'name': name, 'team': team, 'rush_att': rush_att, 'rush_yds': rush_yds, 'rush_tds': rush_tds, 'rec': rec,
#     'rec_yds': rec_yds, 'rec_tds': rec_tds, 'fumbles': fumbles, 'proj_points': proj_points}]
season_projections_rb = get_season_projections_rb('https://www.fantasypros.com/nfl/projections/rb.php?week=draft&scoring=PPR&week=draft')
# [{'name': name, 'team': team, 'rec': rec, 'rec_yds': rec_yds, 'rec_tds': rec_tds, 'rush_att': rush_att,
#     'rush_yds': rush_yds, 'rush_tds': rush_tds, 'fumbles': fumbles, 'proj_points': proj_points}]
season_projections_wr = get_season_projections_wr('https://www.fantasypros.com/nfl/projections/wr.php?week=draft&scoring=PPR&week=draft')
# [{'name': name, 'team': team, 'rec': rec, 'rec_yds': rec_yds, 'rec_tds': rec_tds, 'fumbles': fumbles,
#     'proj_points': proj_points}]
season_projections_te = get_season_projections_te('https://www.fantasypros.com/nfl/projections/te.php?week=draft&scoring=PPR&week=draft')
# # [{'name': name, 'team': team, 'fg': fg, 'fga': fga, 'xpt': xpt, 'proj_points': proj_points}]
# season_projections_k = get_season_projections_k('https://www.fantasypros.com/nfl/projections/k.php?week=draft')
# # [{'team': team, 'sack': sack, 'int': int, 'fr': fr, 'ff': ff, 'td': td, 'safety': safety, 'pa': pa,
# #     'yds_agn': yds_agn, 'proj_points': proj_points}]
# season_projections_dst = get_season_projections_dst()
# ---------------------- Season Projections ----------------------

# ---------------------- Player Transactions ----------------------

# ---------------------- Player Transactions ----------------------
# -------------------------------------------- DATA HANDLING - (BEGIN) --------------------------------------------


# -------------------------------------------- SET STYLES --------------------------------------------
apply_df_scrollbar_style()
# -------------------------------------------- SET STYLES --------------------------------------------


# -------------------------------------------- DATA MANIPULATION --------------------------------------------
# Filters the adp_rankings list of player dictionaries to create separate lists for each position (QB, RB, WR, TE).
adp_data_qb = [player for player in adp_rankings if player.get("pos") == "QB"]
adp_data_rb = [player for player in adp_rankings if player.get("pos") == "RB"]
adp_data_wr = [player for player in adp_rankings if player.get("pos") == "WR"]
adp_data_te = [player for player in adp_rankings if player.get("pos") == "TE"]

# Check if the message has been shown before printing to terminal
if 'value_vs_adp_shown' not in st.session_state:
    print("\n////////// VALUE VS. ADP - to gauge value picks. //////////\n")
    st.session_state['value_vs_adp_shown'] = True

st.subheader("📊 Analytics Dashboard")

# Calculates the implied points vs. ADP for each position (QB, RB, WR, TE) using a function called
# calculate_value_vs_adp() from the implied_points module.
implied_points_df_qb = implied_points.calculate_value_vs_adp("QB", adp_data_qb, season_projections_qb)
st.markdown("---")
implied_points_df_rb = implied_points.calculate_value_vs_adp("RB", adp_data_rb, season_projections_rb)
st.markdown("---")
implied_points_df_wr = implied_points.calculate_value_vs_adp("WR", adp_data_wr, season_projections_wr)
st.markdown("---")
implied_points_df_te = implied_points.calculate_value_vs_adp("TE", adp_data_te, season_projections_te)
st.markdown("---")

# Check if the Boom-Bust message has been shown before printing to terminal
if 'boom_bust_profile_shown' not in st.session_state:
    print("---------------------------------------------------------------")
    print("\n////////// BOOM-BUST PROFILE -- prioritize spike-week players. //////////\n")
    st.session_state['boom_bust_profile_shown'] = True

st.subheader("📈 Spike Week Score")

# Calculates the Boom-Bust profile for players based on a list of seasons, specifically for the year
seasons = [2024]
boom_bust_df = boom_bust_profile.organize_by_condition(seasons)
# -------------------------------------------- DATA MANIPULATION --------------------------------------------


# -------------------------------------------- USER INTERFACE --------------------------------------------

# ---------------------- NFL Player Data - loaded from .csv files ----------------------
# Check if the Boom-Bust message has been shown before printing to terminal
if 'nfl_player_data_shown' not in st.session_state:
    print("\n////////// NFL Player Data //////////\n")
    st.session_state['nfl_player_data_shown'] = True

# NFL Player Data
st.markdown("---")
st.subheader("📋 NFL Player Data")

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

# Set the directory where the data files are located
data_folder = './'

# Load the appropriate file based on season
file_name = f"nfl_player_data_{selected_season}.csv"

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
    st.dataframe(results)

# Display filtered data
st.dataframe(data)

st.markdown('<p style="font-size:13px;">(*) Selected to Pro Bowl, (+) First-Team All-Pro</p>', unsafe_allow_html=True)
# ---------------------- NFL Player Data - loaded from .csv files ----------------------

# ---------------------- Draft Controller ----------------------
# Determines which team is currently making a draft pick in a snake draft format.
team_picking_int = get_team_picking()

# Create a string that represents the name of the team based on the current pick count.
# (e.g., "pick_count = 1, current_team returns: Team 1")
current_team = f"Team {team_picking_int}"

# Calculates the current draft round based on the current pick number and the number of teams (or picks per round).
current_round = (st.session_state.pick_number // len(st.session_state.pick_order))+1

# Creates a sidebar section in a Streamlit app and displays some information there.
with st.sidebar:
    st.write("**Team Rosters:**")
    st.write(st.session_state.teams)
    st.write(f"**Last Pick:** {st.session_state.last_pick}")
    st.write(f"**Last Team:** {st.session_state.last_team}")

# Display some styled and dynamic draft-related info in the Streamlit app.
st.markdown("---")
st.markdown("<h3 style='color: #0098f5;'>🚩 Let's Begin!</h3>", unsafe_allow_html=True) # 🛠
st.write("- Teams: 12 | Format: Snake, Full-PPR")
st.write(f"- Round: {current_round}")
st.markdown(
    f"<h3 style='font-size:18px;'> 🕒 On the Clock: {current_team} | Pick Number: {st.session_state.pick_number+1}</h3>",
    unsafe_allow_html=True
)

# Uses Streamlit to display a subheader with the text "✅️ Pick Selection".
st.markdown("<h3 style='color: #0098f5;'>✅ Pick Selection</h3>", unsafe_allow_html=True) # 🗳

st.markdown("<p style='color: lightblue;'>🤖 <strong>Please make the first pick!</strong></p>", unsafe_allow_html=True)

# Creates a list of available players with selected info, sorted by ADP (Average Draft Position).
available_players_list = [
    {
        "name": p['name'],
        "pos": p['pos'],
        "adp": p.get('adp', None),
        "team": p.get('team', None),
        "bye_week": p.get('bye_week', None)
    }
    for p in sorted(get_available_players(adp_rankings), key=lambda p: p['adp'])
]

# Creates two equal-width columns side by side in the Streamlit app.
col1, col2 = st.columns(2)

# Creates a list of formatted player strings from a list of available players.
formatted_players = [
    f"{player['name']} ({player['pos']})" for player in available_players_list  # e.g., "Ja'Marr Chase (WR)"
]

# Places the following UI elements inside col2.
with col2:
    # Creates a list called valid_positions that contains the valid positions available for filtering
    valid_positions = ["All", "QB", "RB", "WR", "TE"]
    # Creates a sorted list of player positions from the available players and combines it with a default "All" option.
    primary_positions = sorted(set(p['pos'] for p in available_players_list))
    position_filter_options = ["All"] + [pos for pos in primary_positions if pos in valid_positions]
    # Creates a dropdown (select box) inside column 2
    position_filter_selection = st.selectbox(
        "Filter by Position:",  # Displayed as the label above the select box.
        position_filter_options  # A list of available position options for filtering.
    )

# Dynamically filter formatted_players based on the selected position
if position_filter_selection != "All":
    filtered_players = [
        f"{p['name']} ({p['pos']})" for p in available_players_list if p['pos'] == position_filter_selection
    ]
else:
    filtered_players = formatted_players  # Show all players if "All" is selected

# Player selection dropdown in the first column with filtered players
with col1:
    player_choice = st.selectbox(
        "Select Player",
        filtered_players,  # Use filtered players list
        index=None,
        placeholder="--- Select Player ---"
    )
# ---------------------- Draft Controller ----------------------

# ---------------------- Player Overview ----------------------
# Display player information when selected
if player_choice:
    # Extract player name from the formatted string (e.g., "Ja'Marr Chase (WR)")
    selected_name = player_choice.split(" (")[0]

    # Find the player dictionary in the available_players_list
    player_info = next((p for p in available_players_list if p['name'] == selected_name), None)

    # Define a dictionary to map position to the corresponding implied points DataFrame
    implied_points_dfs = {
        "QB": implied_points_df_qb,
        "RB": implied_points_df_rb,
        "WR": implied_points_df_wr,
        "TE": implied_points_df_te
    }

    if player_info:
        st.markdown(
            f"<h3 style='color: #00ab41;'>Player Overview: {player_info['name']}</h3>",
            unsafe_allow_html=True
        )

        # Create three columns
        col1, col2, col3, = st.columns(3)

        # ---------------------- Player Overview - Column 1.1 ----------------------
        with col1:
            code_text = '''
                    Player Overview:
                    '''
            st.markdown(f"```python\n{code_text}\n```")

            st.write(f"ADP: {player_info['adp']}")
            st.write(f"Team: {player_info['team']}")
            st.write(f"Position: {player_info['pos']}")

            # Display bye week, handling cases where the value is NaN
            if player_info['bye_week'] is not None and not math.isnan(player_info['bye_week']):
                st.write(f"Bye Week: {int(player_info['bye_week'])}")
            else:
                st.write("Bye Week: Not available")
        # ---------------------- Player Overview - Column 1.1 ----------------------


        # ---------------------- Player Overview - Column 2.1 ----------------------
        with col2:
            code_text = '''
                    Value vs. ADP Analysis:
                    '''
            st.markdown(f"```python\n{code_text}\n```")

            # Retrieve implied points DataFrame based on position
            implied_points_df = implied_points_dfs.get(player_info['pos'])
            if implied_points_df is not None:
                matched = implied_points_df.loc[
                    implied_points_df['name'] == player_info['name'],
                    ['proj_points', 'implied_points', 'value_vs_adp']
                ]
                if not matched.empty:
                    proj_points = matched['proj_points'].values[0]
                    implied_points = matched['implied_points'].values[0]
                    st.write(f"Projected Points: {proj_points:.2f}")
                    st.write(f"Implied Points: {implied_points:.2f}")

                    # Display value_vs_adp if available
                    if 'value_vs_adp' in matched.columns:
                        value_vs_adp = matched['value_vs_adp'].values[0]
                        sign = "+" if value_vs_adp > 0 else ""
                        st.write(f"Value vs. ADP: {sign}{value_vs_adp:.2f}")
                    else:
                        st.write("Value vs. ADP: Not available")

                else:
                    st.write("Projected Points: Not available")
                    st.write("Implied Points: Not available")
                    st.write("Value vs. ADP: Not available")
            else:
                st.write("Projected Points: Not available")
                st.write("Implied Points: Not available")
                st.write("Value vs. ADP: Not available")
        # ---------------------- Player Overview - Column 2.1 ----------------------

        # ---------------------- Player Overview - Column 3.1 ----------------------
        with col3:
            code_text = '''
                    Spike Week Score:
                    '''
            st.markdown(f"```python\n{code_text}\n```")

            # Retrieve spike_week_score from the boom_bust_df DataFrame
            spike_week_score = boom_bust_df.loc[
                boom_bust_df['player_display_name'] == player_info['name'], 'spike_week_score'
            ]
            if not spike_week_score.empty:
                st.write(f"Spike Week Score: {spike_week_score.values[0]:.2f}")
            else:
                st.write("Spike Week Score: Not available")
        # ---------------------- Player Overview - Column 3.1 ----------------------

        # ---------------------- Player Overview - Column 1.2 ----------------------
        # Player Overview - Column 1.2 - 2024 Regular Season Stats
        st.write("")
        code_text = '''
                                    2024 REG Stats:
                                    '''
        st.markdown(f"```python\n{code_text}\n```")

        # Variables to match
        player_name = player_info['name']
        team_name = player_info['team']
        position_name = player_info['pos']

        # Filter DataFrame based on all three conditions
        matched_player = nfl_player_data_2024[(nfl_player_data_2024['player'] == player_name) &
                                              (nfl_player_data_2024['pos'] == position_name)]

        # Check if a match was found
        if not matched_player.empty:
            print("Match found:")
            print(matched_player)
        else:
            print("No match found!")
            print(f"player_info['name']: {player_info['name']}")
            print(f"player_info['team']: {player_info['team']}")
            print(f"player_info['pos']: {player_info['pos']}")
        # ---------------------- Player Overview - Column 1.2 ----------------------

        if not matched_player.empty:

            # Create three columns
            col1, col2, col3, = st.columns(3)

            # ---------------------- Player Overview Column 1.3 ----------------------
            with col1:
                # Get the text value from the columns
                st.markdown(format_player_overview_stat(
                    "Rank", matched_player['rank'].values[0]), unsafe_allow_html=True
                )
                st.markdown(format_player_overview_stat(
                    "Age", matched_player['age'].values[0]), unsafe_allow_html=True
                )
                st.markdown(format_player_overview_stat(
                    "Games", matched_player['games'].values[0]), unsafe_allow_html=True
                )
                st.markdown(format_player_overview_stat(
                    "Games Started", matched_player['games_started'].values[0]),  unsafe_allow_html=True
                )

                if matched_player['pos'].values[0] == "QB":
                    st.markdown(format_player_overview_stat(
                        "Completions", matched_player['cmp'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "Pass Attempts", matched_player['pass_att'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "Pass Yards", matched_player['pass_yds'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "Pass TDs", matched_player['pass_td'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "Interceptions", matched_player['int'].values[0]), unsafe_allow_html=True
                    )

                if matched_player['pos'].values[0] in ("QB", "RB", "WR"):
                    st.markdown(format_player_overview_stat(
                        "Rush Attempts", matched_player['rush_att'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "Rush Yards", matched_player['rush_yds'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "Yards/Att", matched_player['yds_per_att'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "Rushing TDs", matched_player['rush_td'].values[0]), unsafe_allow_html=True
                    )
            # ---------------------- Player Overview Column 1.3 ----------------------

            # ---------------------- Player Overview Column 2.3 ----------------------
            with col2:
                if matched_player['pos'].values[0] in ("QB", "RB", "WR", "TE"):
                    st.markdown(format_player_overview_stat(
                        "Targets", matched_player['tgt'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "Receptions", matched_player['rec'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "Receiving Yards", matched_player['rec_yds'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "Yards/Rec", matched_player['yds_per_rec'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "Receiving TDs", matched_player['rec_td'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "Fumbles", matched_player['fmb'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "Fumbles Lost", matched_player['fmb_lost'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "Total TDs", matched_player['total_td'].values[0]), unsafe_allow_html=True
                    )
            # ---------------------- Player Overview Column 2.3 ----------------------

            # ---------------------- Player Overview Column 3.3 ----------------------
            with col3:
                if matched_player['pos'].values[0] in ("QB", "RB", "WR", "TE"):
                    st.markdown(format_player_overview_stat(
                        "2PT Made", matched_player['two_pt_made'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "2PT Pass", matched_player['two_pt_pass'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "Fantasy Pts", matched_player['fantasy_pts'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "PPR Pts", matched_player['ppr_pts'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "DraftKings Pts", matched_player['draftkings_pts'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "Fanduel Pts", matched_player['fanduel_pts'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "Value Based Draft", matched_player['value_based_draft'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "Position Rank", matched_player['pos_rank'].values[0]), unsafe_allow_html=True
                    )
                    st.markdown(format_player_overview_stat(
                        "Overall Rank", matched_player['ovr_rank'].values[0]), unsafe_allow_html=True
                    )
            # ---------------------- Player Overview Column 3.3 ----------------------

        # elif isRookie: TODO - Build out isRookie logic.
        #     print("TODO - Build out college data logic.")
        #     st.write("This player is a rookie. There is no historical professional overview.")
        else:
            st.write("Something went wrong. Is this player a rookie? Please try another player.")

    else:
         st.write("Player not found.")
    # ---------------------- Player Overview ----------------------

# ---------------------- Draft Button ----------------------
# Draft Buttons: Next Pick and Undo Last Pick
if st.session_state.last_pick:
    st.success(f"✅ {st.session_state.last_pick} drafted to {st.session_state.last_team}!")

    col_next, col_undo = st.columns(2)

    with col_next:
        if st.button("➡️ Next Pick >>>", on_click=next_pick):
            st.rerun()

    with col_undo:
        if st.button("↩️ Undo Last Pick", on_click=undo_last_pick):
            st.rerun()

else:
    if st.button("Draft Player"):
        if player_choice:
            selected_name = player_choice.split(" (")[0]  # Extract just the name
            if selected_name not in [p for picks in st.session_state.teams.values() for p in picks]:
                st.session_state.teams[current_team].append(selected_name)
                st.session_state.last_pick = selected_name
                st.session_state.last_team = current_team
                st.rerun()
            else:
                st.error("⚠️ Player already taken!")
# ---------------------- Draft Button ----------------------

# ---------------------- Draft Board & Rosters ----------------------
st.markdown("---")
st.subheader("📋 Draft Board & Rosters")

# Draft Board Filters
st.markdown("<div style='font-size:18px; font-weight:Medium;'>📋 Draft Board Filters</div>", unsafe_allow_html=True)

# Create four columns
col1, col2, col3 = st.columns(3)

with col1:
    selected_team = st.selectbox("Filter by Team:", ["All"] + list(st.session_state.teams.keys()))

# Leave the other two columns blank
with col2:
    st.empty()
with col3:
    st.empty()

# Displaying Draft Board & Rosters
teams = list(st.session_state.teams.items())
if selected_team != "All":
    teams = [(selected_team, st.session_state.teams[selected_team])]

for i in range(0, len(teams), 4):
    cols = st.columns(4)
    for idx, (team_name, picks) in enumerate(teams[i:i+4]):
        with cols[idx]:
            st.markdown(f"<h3 style='color:#0076B6;'>{team_name}</h3>", unsafe_allow_html=True)
            starters, bench = build_team_roster(picks)  # You may need to adjust this function
            st.markdown("**Starting Lineup:**")
            required_slots = {"QB": 1, "RB": 2, "WR": 3, "TE": 1, "FLEX": 1}
            for slot, required_count in required_slots.items():
                current_players = starters.get(slot, [])
                for i in range(required_count):
                    if i < len(current_players):
                        player = current_players[i]
                        st.markdown(f"{slot}: <span style='color: #00ab41; font-weight: bold;'>{player['name']}</span>",
                                    unsafe_allow_html=True)
                    else:
                        st.write(f"{slot}: _Empty_")
            st.markdown("**Bench:**")
            if bench:
                for p in bench:
                    st.markdown(f"{slot}: <span style='color: #00ab41; font-weight: bold;'>{player['name']}</span>",
                                    unsafe_allow_html=True)
            else:
                st.write("_No bench players yet._")
# ---------------------- Draft Board & Rosters ----------------------

# -------------------------------------------- USER INTERFACE --------------------------------------------