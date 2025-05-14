# ---------------------- Libraries ----------------------
import requests
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
from nfl_data_py import import_pbp_data
# ---------------------- Libraries ----------------------


# ---------------------- ADP Data ----------------------
def load_adp_data():
    # URL of the FantasyPros Best Ball ADP page
    url = 'https://www.fantasypros.com/nfl/adp/best-ball-overall.php'

    # Fetch the page content
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate the table containing the ADP data
    table = soup.find('table', {'id': 'data'})

    # Initialize a list to store player data
    players = []

    # Team abbreviations (used to parse out the team abbreviation from the player name in the table data scraped from FantasyPros)
    team_abbr = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX',
                 'KC', 'LV', 'LAC', 'LAR', 'MIA', 'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT', 'SF', 'SEA', 'TB', 'TEN', 'WAS']

    # Iterate over the table rows, skipping the header
    for row in table.tbody.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) >= 3:
            rank = cols[0].text.strip()
            player_info = cols[1].text.strip()
            pos = cols[2].text.strip()
            adp = cols[7].text.strip()

            # Extract player name and team from player_info
            player_name_parts = player_info.split()
            team = player_name_parts[-1] if player_name_parts[-1] in team_abbr else ''
            name = ' '.join(player_name_parts[:-1]) if team else player_info

            players.append({
                'rank': rank,
                'name': name,
                'pos': pos,
                'adp': adp
            })

    # Convert to DataFrame
    df = pd.DataFrame(players)

    # Normalize numeric columns
    for col in ['rank', 'adp']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with missing essential values
    df = df.dropna(subset=['name', 'adp'])

    # Sort by fantasy points descending
    df = df.sort_values(by='rank', ascending=True)

    return df.to_dict(orient='records')
# ---------------------- ADP Data ----------------------


# ---------------------- QB Season Projections ----------------------
def load_season_projections_qb():
    url = 'https://www.fantasypros.com/nfl/projections/qb.php?week=draft'

    # Fetch the page content
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate the table containing the QB projections
    table = soup.find('table', {'id': 'data'})

    players = []

    # NFL team abbreviations
    team_abbr = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX',
                 'KC', 'LV', 'LAC', 'LAR', 'MIA', 'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT', 'SF', 'SEA', 'TB', 'TEN', 'WAS']

    for row in table.tbody.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) > 1:
            player_info = cols[0].text.strip()
            pass_att = cols[1].text.strip()
            pass_cmp = cols[2].text.strip()
            pass_yds = cols[3].text.strip()
            pass_tds = cols[4].text.strip()
            ints = cols[5].text.strip()
            rush_att = cols[6].text.strip()
            rush_yds = cols[7].text.strip()
            rush_tds = cols[8].text.strip()
            fumbles = cols[9].text.strip()
            proj_points = cols[10].text.strip()

            # Extract player name and team from player_info
            player_name_parts = player_info.split()
            team = player_name_parts[-1] if player_name_parts[-1] in team_abbr else ''
            name = ' '.join(player_name_parts[:-1]) if team else player_info

            players.append({
                'name': name,
                'team': team,
                'pass_att': pass_att,
                'pass_cmp': pass_cmp,
                'pass_yds': pass_yds,
                'pass_tds': pass_tds,
                'ints': ints,
                'rush_att': rush_att,
                'rush_yds': rush_yds,
                'rush_tds': rush_tds,
                'fumbles': fumbles,
                'proj_points': proj_points
            })

    # Convert to DataFrame
    df = pd.DataFrame(players)

    # Normalize numeric columns
    for col in ['pass_att', 'pass_cmp', 'pass_yds', 'pass_tds', 'ints', 'rush_att', 'rush_yds', 'rush_tds', 'fumbles', 'proj_points']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with missing essential values
    df = df.dropna(subset=['name', 'proj_points'])

    # Sort by fantasy points descending
    df = df.sort_values(by='proj_points', ascending=False)

    return df.to_dict(orient='records')
# ---------------------- QB Season Projections ----------------------


# ---------------------- RB Season Projections ----------------------
def load_season_projections_rb():
    url = 'https://www.fantasypros.com/nfl/projections/rb.php?week=draft&scoring=PPR&week=draft'

    # Fetch the page content
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate the table containing the QB projections
    table = soup.find('table', {'id': 'data'})

    players = []

    # NFL team abbreviations
    team_abbr = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX',
                 'KC', 'LV', 'LAC', 'LAR', 'MIA', 'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT', 'SF', 'SEA', 'TB', 'TEN', 'WAS']

    for row in table.tbody.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) > 1:
            player_info = cols[0].text.strip()
            rush_att = cols[1].text.strip()
            rush_yds = cols[2].text.strip()
            rush_tds = cols[3].text.strip()
            rec = cols[4].text.strip()
            rec_yds = cols[5].text.strip()
            rec_tds = cols[6].text.strip()
            fumbles = cols[7].text.strip()
            proj_points = cols[8].text.strip()

            # Extract player name and team from player_info
            player_name_parts = player_info.split()
            team = player_name_parts[-1] if player_name_parts[-1] in team_abbr else ''
            name = ' '.join(player_name_parts[:-1]) if team else player_info

            players.append({
                'name': name,
                'team': team,
                'rush_att': rush_att,
                'rush_yds': rush_yds,
                'rush_tds': rush_tds,
                'rec': rec,
                'rec_yds': rec_yds,
                'rec_tds': rec_tds,
                'fumbles': fumbles,
                'proj_points': proj_points
            })

    # Convert to DataFrame
    df = pd.DataFrame(players)

    # Normalize numeric columns
    for col in ['rush_att', 'rush_yds', 'rush_tds', 'rec', 'rec_yds', 'rec_tds', 'fumbles', 'proj_points']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with missing essential values
    df = df.dropna(subset=['name', 'proj_points'])

    # Sort by fantasy points descending
    df = df.sort_values(by='proj_points', ascending=False)

    return df.to_dict(orient='records')
# ---------------------- RB Season Projections ----------------------


# ---------------------- WR Season Projections ----------------------
def load_season_projections_wr():
    url = 'https://www.fantasypros.com/nfl/projections/wr.php?week=draft&scoring=PPR&week=draft'

    # Fetch the page content
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate the table containing the QB projections
    table = soup.find('table', {'id': 'data'})

    players = []

    # NFL team abbreviations
    team_abbr = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX',
                 'KC', 'LV', 'LAC', 'LAR', 'MIA', 'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT', 'SF', 'SEA', 'TB', 'TEN', 'WAS']

    for row in table.tbody.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) > 1:
            player_info = cols[0].text.strip()
            rec = cols[1].text.strip()
            rec_yds = cols[2].text.strip()
            rec_tds = cols[3].text.strip()
            rush_att = cols[4].text.strip()
            rush_yds = cols[5].text.strip()
            rush_tds = cols[6].text.strip()
            fumbles = cols[7].text.strip()
            proj_points = cols[8].text.strip()

            # Extract player name and team from player_info
            player_name_parts = player_info.split()
            team = player_name_parts[-1] if player_name_parts[-1] in team_abbr else ''
            name = ' '.join(player_name_parts[:-1]) if team else player_info

            players.append({
                'name': name,
                'team': team,
                'rec': rec,
                'rec_yds': rec_yds,
                'rec_tds': rec_tds,
                'rush_att': rush_att,
                'rush_yds': rush_yds,
                'rush_tds': rush_tds,
                'fumbles': fumbles,
                'proj_points': proj_points
            })

    # Convert to DataFrame
    df = pd.DataFrame(players)

    # Normalize numeric columns
    for col in ['rec', 'rec_yds', 'rec_tds', 'rush_att', 'rush_yds', 'rush_tds',  'fumbles', 'proj_points']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with missing essential values
    df = df.dropna(subset=['name', 'proj_points'])

    # Sort by fantasy points descending
    df = df.sort_values(by='proj_points', ascending=False)

    return df.to_dict(orient='records')
# ---------------------- WR Season Projections ----------------------


# ---------------------- TE Season Projections ----------------------
def load_season_projections_te():
    url = 'https://www.fantasypros.com/nfl/projections/te.php?week=draft&scoring=PPR&week=draft'

    # Fetch the page content
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate the table containing the QB projections
    table = soup.find('table', {'id': 'data'})

    players = []

    # NFL team abbreviations
    team_abbr = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX',
                 'KC', 'LV', 'LAC', 'LAR', 'MIA', 'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT', 'SF', 'SEA', 'TB', 'TEN', 'WAS']

    for row in table.tbody.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) > 1:
            player_info = cols[0].text.strip()
            rec = cols[1].text.strip()
            rec_yds = cols[2].text.strip()
            rec_tds = cols[3].text.strip()
            fumbles = cols[4].text.strip()
            proj_points = cols[5].text.strip()

            # Extract player name and team from player_info
            player_name_parts = player_info.split()
            team = player_name_parts[-1] if player_name_parts[-1] in team_abbr else ''
            name = ' '.join(player_name_parts[:-1]) if team else player_info

            players.append({
                'name': name,
                'team': team,
                'rec': rec,
                'rec_yds': rec_yds,
                'rec_tds': rec_tds,
                'fumbles': fumbles,
                'proj_points': proj_points
            })

    # Convert to DataFrame
    df = pd.DataFrame(players)

    # Normalize numeric columns
    for col in ['rec', 'rec_yds', 'rec_tds', 'fumbles', 'proj_points']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with missing essential values
    df = df.dropna(subset=['name', 'proj_points'])

    # Sort by fantasy points descending
    df = df.sort_values(by='proj_points', ascending=False)

    return df.to_dict(orient='records')
# ---------------------- TE Season Projections ----------------------


# ---------------------- K Season Projections ----------------------
def load_season_projections_k():
    url = 'https://www.fantasypros.com/nfl/projections/k.php?week=draft'

    # Fetch the page content
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate the table containing the QB projections
    table = soup.find('table', {'id': 'data'})

    players = []

    # NFL team abbreviations
    team_abbr = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX',
                 'KC', 'LV', 'LAC', 'LAR', 'MIA', 'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT', 'SF', 'SEA', 'TB', 'TEN', 'WAS']

    for row in table.tbody.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) > 1:
            player_info = cols[0].text.strip()
            fg = cols[1].text.strip()
            fga = cols[2].text.strip()
            xpt = cols[3].text.strip()
            proj_points = cols[4].text.strip()

            # Extract player name and team from player_info
            player_name_parts = player_info.split()
            team = player_name_parts[-1] if player_name_parts[-1] in team_abbr else ''
            name = ' '.join(player_name_parts[:-1]) if team else player_info

            players.append({
                'name': name,
                'team': team,
                'fg': fg,
                'fga': fga,
                'xpt': xpt,
                'proj_points': proj_points
            })

    # Convert to DataFrame
    df = pd.DataFrame(players)

    # Normalize numeric columns
    for col in ['fg', 'fga', 'xpt', 'proj_points']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with missing essential values
    df = df.dropna(subset=['name', 'proj_points'])

    # Sort by fantasy points descending
    df = df.sort_values(by='proj_points', ascending=False)

    return df.to_dict(orient='records')
# ---------------------- K Season Projections ----------------------


# ---------------------- DST Season Projections ----------------------
def load_season_projections_dst():
    url = 'https://www.fantasypros.com/nfl/projections/dst.php?week=draft'

    # Fetch the page content
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate the table containing the QB projections
    table = soup.find('table', {'id': 'data'})

    teams = []

    for row in table.tbody.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) > 1:
            team = cols[0].text.strip()
            sack = cols[1].text.strip()
            int = cols[2].text.strip()
            fr = cols[3].text.strip()
            ff = cols[4].text.strip()
            td = cols[5].text.strip()
            safety = cols[6].text.strip()
            pa = cols[7].text.strip()
            yds_agn = cols[8].text.strip()
            proj_points = cols[9].text.strip()

            teams.append({
                'name': team,
                'sack': sack,
                'int': int,
                'fr': fr,
                'ff': ff,
                'td': td,
                'safety': safety,
                'pa': pa,
                'yds_agn': yds_agn,
                'proj_points': proj_points
            })

    # Convert to DataFrame
    df = pd.DataFrame(teams)

    # Normalize numeric columns
    for col in ['sack', 'int', 'fr', 'ff', 'td', 'safety',  'pa', 'proj_points']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with missing essential values
    df = df.dropna(subset=['name', 'proj_points'])

    # Sort by fantasy points descending
    df = df.sort_values(by='proj_points', ascending=False)

    return df.to_dict(orient='records')
# ---------------------- DST Season Projections ----------------------