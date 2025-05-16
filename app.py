# ---------------------- Libraries ----------------------
import os
import streamlit as st
import psutil
import signal
import math
from load_data import get_adp_data, get_season_projections_qb, get_season_projections_rb, get_season_projections_wr
from load_data import get_season_projections_te, get_season_projections_k, get_season_projections_dst
import implied_points
import boom_bust_profile
# ---------------------- Libraries ----------------------


# ---------------------- Page Configuration ----------------------
# Streamlit function call used to configure the page settings - sets up the page title and icon for the Streamlit app
# This function call should be placed at the very beginning of your Streamlit script.
st.set_page_config(
    page_title="DraftVader v1.0",
    page_icon="🤖"
)
# ---------------------- Page Configuration ----------------------


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


# ---------------------- Header ----------------------
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
            "<strong>"
                "I will be your personal AI assistant for the draft!"
            "</strong></p>", unsafe_allow_html=True)
# ---------------------- Header ----------------------


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
# ---------------------- Style ----------------------


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


# ---------------------- Data Handling - BEGIN ----------------------
# initialize session state variables to ensure they have default values before the user interacts with the app.
initialize_session_state()

# Check if the Data Scraping message has been shown before printing to terminal
if 'data_scraping_shown' not in st.session_state:
    print("\n////////// DATA SCRAPING //////////\n")
    st.session_state['data_scraping_shown'] = True

# calls load_adp_data() function and stores a list of dictionaries in the adp_rankings variable
# [{'rank': rank, 'name': name, 'pos': pos, 'adp': adp}, ...]
adp_rankings = get_adp_data()

# [{'name': name, 'team': team, 'pass_att': pass_att, 'pass_cmp': pass_cmp, 'pass_yds': pass_yds, 'pass_tds': pass_tds,
#     'ints': ints, 'rush_att': rush_att, 'rush_yds': rush_yds, 'rush_tds': rush_tds, 'fumbles': fumbles,
#     'proj_points': proj_points}]
season_projections_qb = get_season_projections_qb()
# [{'name': name, 'team': team, 'rush_att': rush_att, 'rush_yds': rush_yds, 'rush_tds': rush_tds, 'rec': rec,
#     'rec_yds': rec_yds, 'rec_tds': rec_tds, 'fumbles': fumbles, 'proj_points': proj_points}]
season_projections_rb = get_season_projections_rb()
# [{'name': name, 'team': team, 'rec': rec, 'rec_yds': rec_yds, 'rec_tds': rec_tds, 'rush_att': rush_att,
#     'rush_yds': rush_yds, 'rush_tds': rush_tds, 'fumbles': fumbles, 'proj_points': proj_points}]
season_projections_wr = get_season_projections_wr()
# [{'name': name, 'team': team, 'rec': rec, 'rec_yds': rec_yds, 'rec_tds': rec_tds, 'fumbles': fumbles,
#     'proj_points': proj_points}]
season_projections_te = get_season_projections_te()
# [{'name': name, 'team': team, 'fg': fg, 'fga': fga, 'xpt': xpt, 'proj_points': proj_points}]
season_projections_k = get_season_projections_k()
# [{'team': team, 'sack': sack, 'int': int, 'fr': fr, 'ff': ff, 'td': td, 'safety': safety, 'pa': pa,
#     'yds_agn': yds_agn, 'proj_points': proj_points}]
season_projections_dst = get_season_projections_dst()
# ---------------------- Data Handling - BEGIN ----------------------


# ---------------------- Data Manipulation ----------------------
# Filters the adp_rankings list of player dictionaries to create separate lists for each position (QB, RB, WR, TE).
adp_data_qb = [player for player in adp_rankings if player.get("pos") == "QB"]
adp_data_rb = [player for player in adp_rankings if player.get("pos") == "RB"]
adp_data_wr = [player for player in adp_rankings if player.get("pos") == "WR"]
adp_data_te = [player for player in adp_rankings if player.get("pos") == "TE"]

# Check if the message has been shown before printing to terminal
if 'value_vs_adp_shown' not in st.session_state:
    print("\n////////// VALUE VS. ADP - to gauge value picks. //////////\n")
    st.session_state['value_vs_adp_shown'] = True

# Calculates the implied points vs. ADP (Average Draft Position) for each position (QB, RB, WR, TE) using a function
# called calculate_value_vs_adp() from the implied_points module.
implied_points_df_qb = implied_points.calculate_value_vs_adp("QB", adp_data_qb, season_projections_qb)
implied_points_df_rb = implied_points.calculate_value_vs_adp("RB", adp_data_rb, season_projections_rb)
implied_points_df_wr = implied_points.calculate_value_vs_adp("WR", adp_data_wr, season_projections_wr)
implied_points_df_te = implied_points.calculate_value_vs_adp("TE", adp_data_te, season_projections_te)

# Check if the Boom-Bust message has been shown before printing to terminal
if 'boom_bust_profile_shown' not in st.session_state:
    print("---------------------------------------------------------------")
    print("\n////////// BOOM-BUST PROFILE -- prioritize spike-week players. //////////\n")
    st.session_state['boom_bust_profile_shown'] = True

# Calculates the Boom-Bust profile for players based on a list of seasons, specifically for the year
seasons = [2024]
boom_bust_df = boom_bust_profile.organize_by_condition(seasons)
# ---------------------- Data Manipulation ----------------------


# ---------------------- User Interface ----------------------
# determines which team is currently making a draft pick in a snake draft format
team_picking_int = get_team_picking()

# create a string that represents the name of the team based on the current pick count.
# (e.g., "pick_count = 1, current_team returns: Team 1")
current_team = f"Team {team_picking_int}"

current_round = (st.session_state.pick_number // len(st.session_state.pick_order))+1

with st.sidebar:
    st.write("**Team Rosters:**")
    st.write(st.session_state.teams)
    st.write(f"**Last Pick:** {st.session_state.last_pick}")
    st.write(f"**Last Team:** {st.session_state.last_team}")

st.markdown("<h3 style='color: #00ab41;'>🚩 Let's Begin!</h3>", unsafe_allow_html=True) # 🛠
st.write("- Teams: 12 | Format: Snake, Full-PPR")
st.write(f"- Round: {current_round}")
st.markdown(
    f"<h3 style='font-size:18px;'> 🕒 On the Clock: {current_team} | Pick Number: {st.session_state.pick_number+1}</h3>",
    unsafe_allow_html=True
)

# Uses Streamlit to display a subheader with the text "🚩️ Pick Selection".
st.markdown("<h3 style='color: #00ab41;'>✅ Pick Selection</h3>", unsafe_allow_html=True) # 🗳

st.markdown("<p style='color: lightblue;'>🤖 <strong>Please make the first pick!</strong></p>", unsafe_allow_html=True)

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
    valid_positions = ["All", "QB", "RB", "WR", "TE", "K", "DST"]
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
            f"<h3 style='color: #0098f5;'>Player Information: {player_info['name']}</h3>",
            unsafe_allow_html=True
        )

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
    else:
        st.write("Player not found.")

# ------------------------------------- CONTINUE -------------------------------------------

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

# Draft Board Filters
st.markdown("---")
st.markdown("<div style='font-size:18px; font-weight:Medium;'>📋 Draft Board Filters</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    selected_team = st.selectbox("Filter by Team:", ["All"] + list(st.session_state.teams.keys()))
with col2:
    selected_position = st.selectbox("Filter by Position:", ["All"] + sorted(set(p['pos'] for p in available_players_list)))

# Displaying Draft Board & Rosters
st.subheader("📋 Draft Board & Rosters")
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
# ---------------------- User Interface ----------------------