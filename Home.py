# ---------------------- LIBRARIES ----------------------
import os
import psutil
import signal
import math
from datetime import datetime
import pandas as pd
import streamlit as st
from value_vs_adp import calculate_value_vs_adp
import spike_week_score
import rookie_rankings
import injury_reports
from age_curve import apply_age_curve
from load_data import get_adp_data, get_season_projections_qb, get_season_projections_rb
from load_data import get_season_projections_wr, get_season_projections_te
from positional_scarcity import (
    load_player_data,
    calculate_value_over_replacement,
    calculate_positional_tiers,
    get_scarcity_score
)
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
        #
        "drafted_players": []
    }
    # The for loop iterates over each key-value pair in the defaults dictionary:
    for key, value in defaults.items():
        if key not in st.session_state: # Checks if the key is already in st.session_state.
            st.session_state[key] = value # If not, it sets the key in the session state with the corresponding value.
# ---------------------- Initialize Session State ----------------------


# ---------------------- Style ----------------------
# def render_styled_transactions(df):
#
#     if df.empty:
#         st.write("No transactions found.")
#         return
#
#     # Basic CSS like FantasyPros
#     table_style = """
#         <style>
#             .fantasy-table {
#                 width: 100%;
#                 border-collapse: collapse;
#                 font-family: 'Segoe UI', sans-serif;
#                 box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
#                 border-radius: 8px;
#                 overflow: hidden;
#                 margin-top: 10px;
#             }
#             .fantasy-table thead {
#                 background-color: #4CAF50;
#                 color: white;
#                 font-size: 16px;
#             }
#             .fantasy-table th, .fantasy-table td {
#                 padding: 12px 16px;
#                 text-align: left;
#             }
#             .fantasy-table tbody tr:nth-child(even) {
#                 background-color: #f9f9f9;
#             }
#             .fantasy-table tbody tr:hover {
#                 background-color: #f1f1f1;
#             }
#             .fantasy-table td.date {
#                 font-weight: 600;
#                 color: #2d2d2d;
#                 width: 150px;
#             }
#             .fantasy-table td.desc {
#                 color: #444;
#                 line-height: 1.5;
#             }
#         </style>
#     """
#
#     table_html = f"{table_style}<table class='fantasy-table'><thead><tr><th>Date</th><th>Transaction</th></tr></thead><tbody>"
#
#     for _, row in df.iterrows():
#         date = row['Date']
#         transaction = row['Transaction']
#
#         # Clean spacing issues and common typos
#         transaction = re.sub(r'\s{2,}', ' ', transaction)
#         transaction = re.sub(r'seas\s+on', 'season', transaction, flags=re.IGNORECASE)
#         transaction = re.sub(r'Washingt\s+on', 'Washington', transaction)
#
#         table_html += f"""
#             <tr>
#                 <td class="date">{date}</td>
#                 <td class="desc">{transaction}</td>
#             </tr>
#         """
#
#     table_html += "</tbody></table>"
#
#     st.markdown(table_html, unsafe_allow_html=True)


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
    return f"<p style='font-size:16px; color: #0098f5; font-weight:bold;'>{label}:</p> <p style='font-size:14px;'>{value}</p>"

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
# Update player age
def update_player(df, this_year, data_year):
    # Calculate how many years to increment
    year_delta = this_year - data_year

    # Automatically increment age based on year difference
    df['age'] = df['age'] + year_delta

    return df

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
# TODO: Update initial defaults in session state

# Initialize session state variables to ensure they have default values before the user interacts with the app.
initialize_session_state()

# Get the current year (e.g., 2025)
current_year = datetime.now().year

# ---------------------- Historical Data - NFL Player Stats .csv files ----------------------
# ---------------------- Scrape Pro-Football-Reference ----------------------
# Scrape NFL Player stats from Pro-Football-Reference.com
# years = [2022, 2023, 2024]

# for year in years:
#     get_nfl_player_data(year, f"https://www.pro-football-reference.com/years/{year}/fantasy.htm")
# ---------------------- Scrape Pro-Football-Reference ----------------------

# ---------------------- 2024 NFL Player Stats .csv ----------------------
# Load the 2024 NFL Player stats .csv file - (must be above Player_Transactions.py data pulls)
nfl_player_stats_2024_df = pd.read_csv('data_files/nfl_player_stats_2024.csv')

# Remove + and * from player names
nfl_player_stats_2024_df['player'] = nfl_player_stats_2024_df['player'].str.replace(r'[\+\*]', '', regex=True)

# DataFrame saved in session_state
st.session_state['nfl_player_stats_2024_df'] = nfl_player_stats_2024_df
# ---------------------- 2024 NFL Player Stats .csv ----------------------

# ---------------------- 2023 NFL Player Stats .csv ----------------------
# Load the 2023 NFL Player stats CSV file
nfl_player_stats_2023_df = pd.read_csv('data_files/nfl_player_stats_2023.csv')

# Remove + and * from player names
nfl_player_stats_2023_df['player'] = nfl_player_stats_2023_df['player'].str.replace(r'[\+\*]', '', regex=True)
# ---------------------- 2023 NFL Player Stats .csv ----------------------

# ---------------------- 2022 NFL Player Stats .csv ----------------------
# Load the 2022 NFL Player stats CSV file
nfl_player_stats_2022_df = pd.read_csv('data_files/nfl_player_stats_2022.csv')

# Remove + and * from player names
nfl_player_stats_2022_df['player'] = nfl_player_stats_2022_df['player'].str.replace(r'[\+\*]', '', regex=True)
# ---------------------- 2022 NFL Player Stats .csv ----------------------
# ---------------------- Historical Data - NFL Player Stats .csv files ----------------------


# ---------------------- ADP Rankings ----------------------
# calls load_adp_data() function and stores a list of dictionaries in the adp_rankings variable
# [{'rank': rank, 'name': name, 'pos': pos, 'adp': adp}, ...]
adp_rankings = get_adp_data('https://www.fantasypros.com/nfl/adp/best-ball-overall.php')

# Filters the adp_rankings list of player dictionaries to create separate lists for each position (QB, RB, WR, TE).
adp_rankings_qb = [player for player in adp_rankings if player.get("pos") == "QB"]
# DataFrame saved in session_state
st.session_state['adp_data_qb'] = adp_rankings_qb

adp_rankings_rb = [player for player in adp_rankings if player.get("pos") == "RB"]
st.session_state['adp_data_rb'] = adp_rankings_rb

adp_rankings_wr = [player for player in adp_rankings if player.get("pos") == "WR"]
st.session_state['adp_data_wr'] = adp_rankings_wr

adp_rankings_te = [player for player in adp_rankings if player.get("pos") == "TE"]
st.session_state['adp_data_te'] = adp_rankings_te
# ---------------------- ADP Rankings ----------------------


# ---------------------- Season Projections ----------------------
# [{'name': name, 'team': team, 'pass_att': pass_att, 'pass_cmp': pass_cmp, 'pass_yds': pass_yds, 'pass_tds': pass_tds,
#     'ints': ints, 'rush_att': rush_att, 'rush_yds': rush_yds, 'rush_tds': rush_tds, 'fumbles': fumbles,
#     'proj_points': proj_points}]
season_projections_qb = get_season_projections_qb('https://www.fantasypros.com/nfl/projections/qb.php?week=draft')
# DataFrame saved in session_state
st.session_state['season_projections_qb'] = season_projections_qb

# [{'name': name, 'team': team, 'rush_att': rush_att, 'rush_yds': rush_yds, 'rush_tds': rush_tds, 'rec': rec,
#     'rec_yds': rec_yds, 'rec_tds': rec_tds, 'fumbles': fumbles, 'proj_points': proj_points}]
season_projections_rb = get_season_projections_rb('https://www.fantasypros.com/nfl/projections/rb.php?week=draft&scoring=PPR&week=draft')
st.session_state['season_projections_rb'] = season_projections_rb

# [{'name': name, 'team': team, 'rec': rec, 'rec_yds': rec_yds, 'rec_tds': rec_tds, 'rush_att': rush_att,
#     'rush_yds': rush_yds, 'rush_tds': rush_tds, 'fumbles': fumbles, 'proj_points': proj_points}]
season_projections_wr = get_season_projections_wr('https://www.fantasypros.com/nfl/projections/wr.php?week=draft&scoring=PPR&week=draft')
st.session_state['season_projections_wr'] = season_projections_wr

# [{'name': name, 'team': team, 'rec': rec, 'rec_yds': rec_yds, 'rec_tds': rec_tds, 'fumbles': fumbles,
#     'proj_points': proj_points}]
season_projections_te = get_season_projections_te('https://www.fantasypros.com/nfl/projections/te.php?week=draft&scoring=PPR&week=draft')
st.session_state['season_projections_te'] = season_projections_te

# # [{'name': name, 'team': team, 'fg': fg, 'fga': fga, 'xpt': xpt, 'proj_points': proj_points}]
# season_projections_k = get_season_projections_k('https://www.fantasypros.com/nfl/projections/k.php?week=draft')

# # [{'team': team, 'sack': sack, 'int': int, 'fr': fr, 'ff': ff, 'td': td, 'safety': safety, 'pa': pa,
# #     'yds_agn': yds_agn, 'proj_points': proj_points}]
# season_projections_dst = get_season_projections_dst()

# TODO: Change the following code so that ['pos'] is added after ['team'] in the dataframe that is created

# Add 'Position' column to each DataFrame
season_projections_df_qb = pd.DataFrame(season_projections_qb)
season_projections_df_qb['pos'] = 'QB'
season_projections_df_rb = pd.DataFrame(season_projections_rb)
season_projections_df_rb['pos'] = 'RB'
season_projections_df_wr = pd.DataFrame(season_projections_wr)
season_projections_df_wr['pos'] = 'WR'
season_projections_df_te = pd.DataFrame(season_projections_te)
season_projections_df_te['pos'] = 'TE'

# Create a list of season projection dfs
season_projections_df_all = pd.concat([
    season_projections_df_qb,
    season_projections_df_rb,
    season_projections_df_wr,
    season_projections_df_te
], ignore_index=True)

# Optionally store it in session state
# st.session_state['season_projections_all'] = season_projections_all

# Optionally store cleaned DataFrame for export or debugging
# season_projections_all.to_csv("cleaned_projections.csv", index=False)
# ---------------------- Season Projections ----------------------


# ---------------------- Value vs ADP DataFrame ----------------------
# Calculates the implied points vs. ADP for each position (QB, RB, WR, TE) using a function called
# calculate_value_vs_adp() from the implied_points module.
value_vs_adp_df_qb = calculate_value_vs_adp("QB", adp_rankings_qb, season_projections_qb, False)
value_vs_adp_df_rb = calculate_value_vs_adp("RB", adp_rankings_rb, season_projections_rb, False)
value_vs_adp_df_wr = calculate_value_vs_adp("WR", adp_rankings_wr, season_projections_wr, False)
value_vs_adp_df_te = calculate_value_vs_adp("TE", adp_rankings_te, season_projections_te, False)

# Define a dictionary to map position to the corresponding value_vs_adp dataframe
value_vs_adp_df = {
    "QB": value_vs_adp_df_qb,
    "RB": value_vs_adp_df_rb,
    "WR": value_vs_adp_df_wr,
    "TE": value_vs_adp_df_te
}
# ---------------------- Value vs ADP DataFrame ----------------------


# ---------------------- Positional Scarcity ----------------------
positional_scarcity_df = load_player_data(season_projections_df_all)
positional_scarcity_df = calculate_value_over_replacement(positional_scarcity_df)
positional_scarcity_df = calculate_positional_tiers(positional_scarcity_df)
positional_scarcity_df = get_scarcity_score(positional_scarcity_df)

# Store positional_scarcity_df variable in session state
st.session_state['positional_scarcity_df'] = positional_scarcity_df
# ---------------------- Positional Scarcity ----------------------


# ---------------------- Boom-Bust DataFrame ----------------------
# Calculates the Boom-Bust DataFrame for players based on a list of seasons, specifically for the year
seasons = [2024]
boom_bust_df = spike_week_score.organize_by_condition(seasons)
# ---------------------- Boom-Bust DataFrame ----------------------


# ---------------------- Rookie Rankings DataFrame (must be above Player_Transactions.py data pulls) ----------------------
rookie_rankings_df = rookie_rankings.get_rookie_rankings("data_files/all_rookie_rankings_2025.csv")
st.session_state['rookie_rankings_df'] = rookie_rankings_df
# ---------------------- Rookie Rankings DataFrame (must be above Player_Transactions.py data pulls) ----------------------


# ---------------------- Injury Reports DataFrame ----------------------
# List of pages to scrape
urls = [
    "https://www.fantasypros.com/nfl/injury-news.php",
    "https://www.fantasypros.com/nfl/injury-news.php?page=2",
    "https://www.fantasypros.com/nfl/injury-news.php?page=3",
]
injury_reports_df = injury_reports.get_injury_reports(urls)
st.session_state['injury_reports_df'] = injury_reports_df
# ---------------------- Injury Reports DataFrame ----------------------


# ---------------------- Age Curve DataFrame ----------------------
# Update player age
updated_stats_df = update_player(nfl_player_stats_2024_df, current_year, 2024)

age_curve_df = apply_age_curve(updated_stats_df)

# DataFrame saved in session_state
st.session_state['age_curve_df'] = age_curve_df
# ---------------------- Age Curve DataFrame ----------------------
# -------------------------------------------- DATA HANDLING - (BEGIN) --------------------------------------------


# -------------------------------------------- SET STYLES --------------------------------------------
apply_df_scrollbar_style()
# -------------------------------------------- SET STYLES --------------------------------------------


# -------------------------------------------- USER INTERFACE --------------------------------------------
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
            implied_points_df = value_vs_adp_df.get(player_info['pos'])
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
                                    2024 Regular Season Stats:
                                    '''
        st.markdown(f"```python\n{code_text}\n```")

        # Variables to match
        player_name = player_info['name']
        team_name = player_info['team']
        position_name = player_info['pos']

        # Filter DataFrame based on all three conditions
        matched_player = nfl_player_stats_2024_df[(nfl_player_stats_2024_df['player'] == player_name) &
                                                  (nfl_player_stats_2024_df['pos'] == position_name)]

        # Check if a match was found
        if not matched_player.empty:
            print("---------------------------------------------------------------")
            print("MATCH FOUND:\n")
            # Assuming matched_player is a DataFrame with one row
            headers = [
                'rank', 'player', 'team', 'pos', 'age', 'games', 'games_started', 'cmp',
                'pass_att', 'pass_yds', 'pass_td', 'int', 'rush_att', 'rush_yds', 'yds_per_att',
                'rush_td', 'tgt', 'rec', 'rec_yds', 'yds_per_rec', 'rec_td', 'fmb', 'fmb_lost',
                'total_td', 'two_pt_made', 'two_pt_pass', 'fantasy_pts', 'ppr_pts',
                'draftkings_pts', 'fanduel_pts', 'value_based_draft', 'pos_rank', 'ovr_rank'
            ]

            # Build a dictionary of non-zero fields
            output_data = {}
            for field in headers:
                value = matched_player[field].values[0]
                if isinstance(value, str) or value != 0:
                    # Keep field names lowercase with spaces (no capitalization)
                    display_name = field.replace('_', ' ')
                    output_data[display_name] = value

            # Convert to DataFrame for easy display (e.g., in Streamlit or Jupyter)
            output_df = pd.DataFrame.from_dict(output_data, orient='index', columns=['Value'])

            # Optional: Reset index if you want it to look more like a 2-column table
            output_df.reset_index(inplace=True)
            output_df.columns = ['Field', 'Value']

            fields_per_line = 4
            total_fields = len(output_df)

            # Print dataframe row to terminal with bold fields
            for i in range(0, total_fields, fields_per_line):
                line_items = []
                for j in range(i, min(i + fields_per_line, total_fields)):
                    field = output_df.Field.values[j]
                    value = output_df.Value.values[j]
                    bold_field = f"\033[1m{field}\033[0m"
                    line_items.append(f"{bold_field}: {value}")
                print(" | ".join(line_items))

            print("---------------------------------------------------------------")
        else:
            print("---------------------------------------------------------------")
            print("NO MATCH FOUND!")
            print(f"player_info['name']: {player_info['name']}")
            print(f"player_info['team']: {player_info['team']}")
            print(f"player_info['pos']: {player_info['pos']}")
            print("---------------------------------------------------------------")
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