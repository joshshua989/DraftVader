# ---------------------- Libraries ----------------------
import os
import re
import streamlit as st
import psutil
import signal
from load_data import get_regular_season_totals, get_adp_data, get_season_projections_qb, get_season_projections_rb
from load_data import get_season_projections_wr, get_season_projections_te, get_season_projections_k
from load_data import get_season_projections_dst
# ---------------------- Libraries ----------------------

# Streamlit function call used to configure the page settings - sets up the page title and icon for the Streamlit app
# This function call should be placed at the very beginning of your Streamlit script.
st.set_page_config(
    page_title="DraftVader v1.0",
    page_icon="🤖"
)

# ---------------------- Data Functions ----------------------
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

# Loads Average Draft Position (ADP) data from FantasyPros, processes it, and caches the result to improve performance.
@st.cache_data # Subsequent calls with the same input will return the cached result instead of re-executing the function.
def load_adp_data():
    # Print to the console (or Streamlit’s log) the start of the data scraping process.
    print("---------------------------------------------------------------")
    print("⏳ Scraping ADP data from 'https://www.fantasypros.com/nfl/adp/best-ball-overall.php' ...")
    # Calls a function named get_adp_data() to scrape ADP data from FantasyPros.
    # adp_data is a list of dictionaries where each dictionary contains data about a player.
    adp_data = get_adp_data()
    # Check if data is empty or None
    if not adp_data:
        raise ValueError("No ADP data returned from the source.")
    for player in adp_data: # Iterates over the list of player data.
        # Uses the function get_primary_position() to standardize or clean up the player’s position field.
        player['pos'] = get_primary_position(player['pos'])
    # Print a message indicating that the ADP data has been successfully loaded.
    print("🧠 ADP data loaded!\n")
    print("Data summary:")
    # Displays a preview of the first 5 player records.
    for player in adp_data[:5]:
        print(player)
    print("---------------------------------------------------------------")
    return adp_data

@st.cache_data
def load_season_projections_qb():
    print("⏳ Scraping QB Season Projections from 'https://www.fantasypros.com/nfl/projections/qb.php?week=draft' ...")
    projections_qb = get_season_projections_qb()
    print("🧠 QB Season Projections loaded!\n")
    print("Data summary:")
    for qb in projections_qb[:5]:
        print(qb)
    print("---------------------------------------------------------------")
    return projections_qb

@st.cache_data
def load_season_projections_rb():
    print("⏳ Scraping RB Season Projections from 'https://www.fantasypros.com/nfl/projections/rb.php?week=draft&scoring=PPR&week=draft' ...")
    projections_rb = get_season_projections_rb()
    print("🧠 RB Season Projections loaded!\n")
    print("Data summary:")
    for rb in projections_rb[:5]:
        print(rb)
    print("---------------------------------------------------------------")
    return projections_rb

@st.cache_data
def load_season_projections_wr():
    print("⏳ Scraping WR Season Projections from 'https://www.fantasypros.com/nfl/projections/wr.php?week=draft&scoring=PPR&week=draft' ...")
    projections_wr = get_season_projections_wr()
    print("🧠 WR Season Projections loaded!\n")
    print("Data summary:")
    for wr in projections_wr[:5]:
        print(wr)
    print("---------------------------------------------------------------")
    return projections_wr

@st.cache_data
def load_season_projections_te():
    print("⏳ Scraping TE Season Projections from 'https://www.fantasypros.com/nfl/projections/te.php?week=draft&scoring=PPR&week=draft' ...")
    projections_te = get_season_projections_te()
    print("🧠 TE Season Projections loaded!\n")
    print("Data summary:")
    for te in projections_te[:5]:
        print(te)
    print("---------------------------------------------------------------")
    return projections_te

@st.cache_data
def load_season_projections_k():
    print("⏳ Scraping Kicker Season Projections from 'https://www.fantasypros.com/nfl/projections/k.php?week=draft' ...")
    projections_k = get_season_projections_k()
    print("🧠 Kicker Season Projections loaded!\n")
    print("Data summary:")
    for k in projections_k[:5]:
        print(k)
    print("---------------------------------------------------------------")
    return projections_k

@st.cache_data
def load_season_projections_dst():
    print("⏳ Scraping DST Season Projections from 'https://www.fantasypros.com/nfl/projections/dst.php?week=draft' ...")
    projections_dst = get_season_projections_dst()
    print("🧠 DST Season Projections loaded!\n")
    print("Data summary:")
    for dst in projections_dst[:5]:
        print(dst)
    print("---------------------------------------------------------------")
    return projections_dst

# @st.cache_data # A Streamlit decorator that tells Streamlit to cache the output of the function.
# # The first time get_player_stats() runs, it fetches and stores the data.
# # On future runs, if the input hasn’t changed, Streamlit will return the cached result — instead of re-running the function.
# def load_player_stats(stat_str: str, seasons):
#     match stat_str:
#         case "totals":
#             return get_regular_season_totals(seasons)
#         case _:
#             print(f"Load Failure! Could not recognize stat code: {stat_str}")
#             st.markdown(f"Load Failure! Could not recognize stat code: {stat_str}")
#             return
# ---------------------- Data Functions ----------------------


# ---------------------- Style ----------------------
# customizes the visual appearance of all select boxes in the app by injecting CSS through the st.markdown() function.
def apply_selectbox_style():
    st.markdown( # Uses st.markdown() to insert raw HTML and CSS.
                 # i.e. st.markdown("""<style>...</style>""", unsafe_allow_html=True)
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

# function that creates a custom-styled header
def styled_header(title: str):
    st.markdown(
        f"<h1 style='text-align: center; font-size: 48px; color: #0076B6;'>{title}</h1>",
        unsafe_allow_html=True
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


# ---------------------- Script Functions ----------------------
def build_team_roster(team_picks):
    starters = {"QB": [], "RB": [], "WR": [], "TE": [], "FLEX": []}
    bench = []
    detailed_picks = []
    for p_name in team_picks:
        player_info = next((p for p in adp_dict if p['name'] == p_name), None)
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

# Ensures that the draft follows a snake format, where the draft order reverses after each round.
def get_pick_count():
    # st.session_state.pick_number is the current pick number in the draft.
    # len(st.session_state.pick_order) gives the total number of teams.
    # The // operator performs integer division to calculate the current round number.
    round_number = st.session_state.pick_number // len(st.session_state.pick_order) # determine round (i.e. round 1)
    # Uses the modulus operator % to find the position within the current round.
    # This effectively determines the index within the list of teams.
    pick_in_round = st.session_state.pick_number % len(st.session_state.pick_order) # determine the position
                                                                                    # (i.e. round 2, pick 4)
    # Checks whether the round number is even or odd.
    # If even, it returns the team from pick_order at the calculated index.
    # If odd, it returns the team from the reversed order ([::-1]) at the same index.
    # This logic ensures that the draft follows a snake format, where the order reverses after each round.
    if round_number % 2 == 0:
        return st.session_state.pick_order[pick_in_round] # Even round: normal order
    else:
        return st.session_state.pick_order[::-1][pick_in_round] # Odd round: reversed order

    # Example: If there are 4 teams (pick_order = [A, B, C, D]):
    # Round 1 (even): A -> B -> C -> D
    # Round 2 (odd): D -> C -> B -> A
    # Round 3 (even): A -> B -> C -> D
    # And so on...

# Function to get the primary position (e.g., "QB" from "QB1", "RB2", etc.)
def get_primary_position(position):
    # Use regular expression to capture the first part of the position (e.g., "QB", "RB", etc.)
    match = re.match(r"([A-Za-z]+)", position)
    return match.group(1) if match else position  # Default to the original position if no match
# ---------------------- Script Functions ----------------------


# ---------------------- Data Handling - BEGIN ----------------------
# initialize session state variables to ensure they have default values before the user interacts with the app.
initialize_session_state()

# calls load_adp_data() function and stores a list of dictionaries in the adp_dict variable
# [{'rank': rank, 'name': name, 'pos': pos, 'adp': adp}, ...]
adp_dict = load_adp_data()

# [{'name': name, 'team': team, 'pass_att': pass_att, 'pass_cmp': pass_cmp, 'pass_yds': pass_yds, 'pass_tds': pass_tds,
#     'ints': ints, 'rush_att': rush_att, 'rush_yds': rush_yds, 'rush_tds': rush_tds, 'fumbles': fumbles,
#     'proj_points': proj_points}]
season_projections_qb = load_season_projections_qb()
# [{'name': name, 'team': team, 'rush_att': rush_att, 'rush_yds': rush_yds, 'rush_tds': rush_tds, 'rec': rec,
#     'rec_yds': rec_yds, 'rec_tds': rec_tds, 'fumbles': fumbles, 'proj_points': proj_points}]
season_projections_rb = load_season_projections_rb()
# [{'name': name, 'team': team, 'rec': rec, 'rec_yds': rec_yds, 'rec_tds': rec_tds, 'rush_att': rush_att,
#     'rush_yds': rush_yds, 'rush_tds': rush_tds, 'fumbles': fumbles, 'proj_points': proj_points}]
season_projections_wr = load_season_projections_wr()
# [{'name': name, 'team': team, 'rec': rec, 'rec_yds': rec_yds, 'rec_tds': rec_tds, 'fumbles': fumbles,
#     'proj_points': proj_points}]
season_projections_te = load_season_projections_te()
# [{'name': name, 'team': team, 'fg': fg, 'fga': fga, 'xpt': xpt, 'proj_points': proj_points}]
season_projections_k = load_season_projections_k()
# [{'team': team, 'sack': sack, 'int': int, 'fr': fr, 'ff': ff, 'td': td, 'safety': safety, 'pa': pa,
#     'yds_agn': yds_agn, 'proj_points': proj_points}]
season_projections_dst = load_season_projections_dst()

# seasons = [2022, 2023, 2024]
# regular_season_totals = load_player_stats("totals", seasons)
# for stat_type, df in regular_season_totals.items():
#      filename = f"{stat_type.upper()}_STATS.csv"
#      df.to_csv(filename, index=False)
#      st.write(f"Exported {filename}")
# ---------------------- Data Handling - BEGIN ----------------------


# ---------------------- User Interface ----------------------
# calls styled_header() function to print styled header with arg "🏈 DraftVader v1.0 🤖"
styled_header("🤖 DRAFT VADER 1.0 🏈")

st.write("**Welcome to NFL Best Ball Draft 2025! I am you're AI assistant! Please make a pick to begin the draft!**")

# determines which team is currently making a draft pick in a snake draft format
pick_count = get_pick_count()

# create a string that represents the name of the team based on the current pick count.
# (i.e. pick_count = 1, current_team returns "Team 1")
current_team = f"Team {pick_count}"

current_round = (st.session_state.pick_number // len(st.session_state.pick_order))+1

with st.sidebar:
    st.write("**Team Rosters:**")
    st.write(st.session_state.teams)
    st.write(f"**Last Pick:** {st.session_state.last_pick}")
    st.write(f"**Last Team:** {st.session_state.last_team}")

st.subheader("🛠️ Draft Progress")
st.write("Teams: 12 | Format: Snake, full-PPR")
st.write(f"Round: {current_round}")
st.markdown(
    f"<h3 style='font-size:18px;'> 🕒 On the Clock: {current_team} | Pick Number: {st.session_state.pick_number+1}</h3>",
    unsafe_allow_html=True
)

# uses Streamlit to display a subheader with the text "🗳️ Pick Selection".
st.subheader("🗳️ Pick Selection")

# ----------------------------------- CONTINUE ---------------------------------------

# Extract the list of available players
available_players_list = [
    {"name": p['name'], "pos": p['pos']}
    for p in sorted(get_available_players(adp_dict), key=lambda p: p['adp'])
]

# Format the available players for the selectbox (only name and position)
formatted_players = [
    f"{player['name']} ({player['pos']})" for player in available_players_list
]

# Define the valid positions for the filter
valid_positions = ["All", "QB", "RB", "WR", "TE", "DST"]

# Filter by position
primary_positions = sorted(set(p['pos'] for p in available_players_list))
position_filter_options = ["All"] + [pos for pos in primary_positions if pos in valid_positions]

col1, col2 = st.columns(2)

# Apply the position filter and selectbox
with col1:
    player_choice = st.selectbox(
        "Select Player",
        formatted_players,  # Display player name and position (cleaned)
        index=None,
        placeholder="--- Select Player ---"
    )

with col2:
    position_filter_selection = st.selectbox(
        "Filter by Position:",
        position_filter_options  # Filter by cleaned primary positions
    )

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
                        st.markdown(f"{slot}: <span style='color: #FFFF00; font-weight: bold;'>{player['name']}</span>",
                                    unsafe_allow_html=True)
                    else:
                        st.write(f"{slot}: _Empty_")
            st.markdown("**Bench:**")
            if bench:
                for p in bench:
                    st.markdown(f"{slot}: <span style='color: #FFFF00; font-weight: bold;'>{player['name']}</span>",
                                    unsafe_allow_html=True)
            else:
                st.write("_No bench players yet._")
# ---------------------- User Interface ----------------------