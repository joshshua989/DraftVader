# ---------------------- Libraries ----------------------
import os
import re
import pandas as pd
import streamlit as st
from scraper import load_adp_data, load_season_projections_qb, load_season_projections_rb, load_season_projections_wr
from scraper import load_season_projections_te, load_season_projections_k, load_season_projections_dst
# ---------------------- Libraries ----------------------


# ---------------------- Data Handling Functions ----------------------
# @st.cache_data
# def get_nfl_player_data(year, url):
#     print("---------------------------------------------------------------")
#     print(f"⏳ Scraping {year} NFL Player Data from '{url}' ...")
#     nfl_player_data = scrape_nfl_player_data(year, url)
#     print(f"🧠 {year} NFL Player Data Loaded!\n")
#     print("Data summary:")
#     for player in nfl_player_data[:5]:
#         print(player)
#     print("---------------------------------------------------------------")
#     return nfl_player_data

# Load data from CSV files
@st.cache_data
def load_nfl_player_data(data_folder, file_name):
    nfl_player_data = pd.read_csv(os.path.join(data_folder, file_name))
    print("---------------------------------------------------------------")
    print(nfl_player_data)
    return nfl_player_data

# Loads Average Draft Position (ADP) data from FantasyPros, processes it, and caches the result to improve performance.
@st.cache_data # Subsequent calls with the same input will return the cached result instead of re-executing the function.
def get_adp_data():
    print("⏳ Scraping ADP data from 'https://www.fantasypros.com/nfl/adp/best-ball-overall.php' ...")
    # adp_data is a list of dictionaries where each dictionary contains data about a player.
    adp_data = load_adp_data()
    # Check if data is empty or None
    if not adp_data:
        raise ValueError("No ADP data returned from the source.")
    for player in adp_data: # Iterates over the list of player data.
        # Use regular expression to capture the first part of the position (e.g., "QB", "RB", etc.)
        match = re.match(r"([A-Za-z]+)", player['pos'])
        # Uses the function get_primary_position() to standardize or clean up the player’s position field.
        player['pos'] = match.group(1) if match else player['pos']  # Default to the original position if no match=
    print("🧠 ADP data loaded!\n")
    print("Data summary:")
    for player in adp_data[:5]:
        print(player)
    print("---------------------------------------------------------------")
    return adp_data

@st.cache_data
def get_season_projections_qb():
    print("⏳ Scraping QB Season Projections from 'https://www.fantasypros.com/nfl/projections/qb.php?week=draft' ...")
    projections_qb = load_season_projections_qb()
    print("🧠 QB Season Projections loaded!\n")
    print("Data summary:")
    for qb in projections_qb[:5]:
        print(qb)
    print("---------------------------------------------------------------")
    return projections_qb

@st.cache_data
def get_season_projections_rb():
    print("⏳ Scraping RB Season Projections from 'https://www.fantasypros.com/nfl/projections/rb.php?week=draft&scoring=PPR&week=draft' ...")
    projections_rb = load_season_projections_rb()
    print("🧠 RB Season Projections loaded!\n")
    print("Data summary:")
    for rb in projections_rb[:5]:
        print(rb)
    print("---------------------------------------------------------------")
    return projections_rb

@st.cache_data
def get_season_projections_wr():
    print("⏳ Scraping WR Season Projections from 'https://www.fantasypros.com/nfl/projections/wr.php?week=draft&scoring=PPR&week=draft' ...")
    projections_wr = load_season_projections_wr()
    print("🧠 WR Season Projections loaded!\n")
    print("Data summary:")
    for wr in projections_wr[:5]:
        print(wr)
    print("---------------------------------------------------------------")
    return projections_wr

@st.cache_data
def get_season_projections_te():
    print("⏳ Scraping TE Season Projections from 'https://www.fantasypros.com/nfl/projections/te.php?week=draft&scoring=PPR&week=draft' ...")
    projections_te = load_season_projections_te()
    print("🧠 TE Season Projections loaded!\n")
    print("Data summary:")
    for te in projections_te[:5]:
        print(te)
    print("---------------------------------------------------------------")
    return projections_te

@st.cache_data
def get_season_projections_k():
    print("⏳ Scraping Kicker Season Projections from 'https://www.fantasypros.com/nfl/projections/k.php?week=draft' ...")
    projections_k = load_season_projections_k()
    print("🧠 Kicker Season Projections loaded!\n")
    print("Data summary:")
    for k in projections_k[:5]:
        print(k)
    print("---------------------------------------------------------------")
    return projections_k

@st.cache_data
def get_season_projections_dst():
    print("⏳ Scraping DST Season Projections from 'https://www.fantasypros.com/nfl/projections/dst.php?week=draft' ...")
    projections_dst = load_season_projections_dst()
    print("🧠 DST Season Projections loaded!\n")
    print("Data summary:")
    for dst in projections_dst[:5]:
        print(dst)
    print("---------------------------------------------------------------")
    return projections_dst
# ---------------------- Data Handling Functions ----------------------