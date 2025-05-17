# ---------------------- Libraries ----------------------
import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
# ---------------------- Libraries ----------------------


# ---------------------- Script Functions ----------------------
# Extract player name, team, and bye week from player_info
# def extract_player_info(player_info):
#     # Team abbreviations (used to parse out the team abbreviation from the player name in the table data scraped from FantasyPros)
#     team_abbr = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX',
#                  'KC', 'LV', 'LAC', 'LAR', 'MIA', 'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT', 'SF', 'SEA', 'TB',
#                  'TEN', 'WAS']
#
#     # Use regex to capture the player name, team, and bye week
#     match = re.match(r"^(.*?)\s+([A-Z]{2,3})\s*\((\d+)\)$", player_info)
#     if match:
#         name = match.group(1).strip()
#         team = match.group(2)
#         bye_week = int(match.group(3))
#     else:#
#         # Fallback if the pattern doesn't match
#         player_name_parts = player_info.split()
#         team = player_name_parts[-1] if player_name_parts[-1] in team_abbr else ''
#         name = ' '.join(player_name_parts[:-1]) if team else player_info
#         bye_week = None
#
#     return name, team, bye_week

def extract_player_info(player_info):
    # Try to match the player name, team, and bye week
    match = re.match(r"^(.*?)\s+([A-Z]{2,3})\s*\((\d+)\)$", player_info)
    if match:
        name = match.group(1).strip()
        team = match.group(2)
        bye_week = int(match.group(3))
    else:
        # Check if the string only contains the player's name without team/bye week
        name = player_info.strip()
        team = None
        bye_week = None
        print(f"Player without team/bye week: {player_info}")

    return name, team, bye_week
# ---------------------- Script Functions ----------------------


# ---------------------- NFL Player Data ----------------------
# def scrape_nfl_player_data(year, url):
#     try:
#         # Send a GET request to the specified URL:
#         response = requests.get(url)
#         # Check for HTTP errors:
#         response.raise_for_status()
#         # Parse the HTML content of the response:
#         soup = BeautifulSoup(response.text, 'html.parser')
#         # Find a specific HTML table:
#         table = soup.find('table', {'id': 'fantasy'})
#
#         # Check if the table exists
#         if not table:
#             print("Error: Table with id 'fantasy' not found.")
#             return None
#
#         # Find all table rows (<tr> tags) within a table:
#         rows = table.find_all('tr')
#         # Initialize an empty list to store data:
#         data = []
#
#         # Step 1: Extract Table Headers - headers contains the column names.
#         headers = [th.get_text() for th in rows[1].find_all('th')]
#         # Step 2: Extract Data from Remaining Rows - data contains the rows of the table, where each row is a list of cell values.
#         for row in rows[2:]:  # rows[1:]: Skips the first row (headers) and iterates through the remaining rows.
#             # find_all(['th', 'td']): Finds all data cells (both header and data cells) in the current row.
#             # td.get_text(): Extracts the text from each cell.
#             # cols: A list of all text values from the cells in the current row.
#             cols = [td.get_text() for td in row.find_all(['th', 'td'])]
#
#             # Only add the row if it matches the length of headers
#             if len(cols) == len(headers):
#                 data.append(cols)
#             else:
#                 print(f"Warning: Row length mismatch: {len(cols)} columns (expected {len(headers)})")
#
#         # Check if data was collected
#         if not data:
#             print("Error: No valid data found in the table.")
#             return None
#
#         # Create a DataFrame from the scraped data
#         df = pd.DataFrame(data, columns=headers)
#         # Save the DataFrame to a CSV file
#         df.to_csv(f'nfl_player_data_{year}.csv', index=False)
#         # Print a Confirmation Message
#         print(f"Data scraped and saved to nfl_player_data_{year}.csv")
#         return df.to_dict(orient='records')
#
#     except requests.RequestException as e:
#         print(f"HTTP request error: {e}")
#         return None
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#         return None
# ---------------------- NFL Player Data ----------------------


# ---------------------- ADP Data ----------------------
def load_adp_data(url):
    try:
        # URL of the FantasyPros Best Ball ADP page
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Locate the table containing the ADP data
        table = soup.find('table', {'id': 'data'})

        # Initialize a list to store player data
        players = []

        # Iterate over the table rows, skipping the header
        for row in table.tbody.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 3:
                rank = cols[0].text.strip()
                player_info = cols[1].text.strip()
                pos = cols[2].text.strip()
                adp = cols[7].text.strip()

                name, team, bye_week = extract_player_info(player_info)

                players.append({
                    'rank': rank,
                    'name': name,
                    'team': team,
                    'pos': pos,
                    'bye_week': bye_week,
                    'adp': adp
                })

        # Convert to DataFrame
        df = pd.DataFrame(players)

        # Normalize numeric columns
        for col in ['rank', 'bye_week', 'adp']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Drop rows with missing essential values
        df = df.dropna(subset=['name', 'adp'])

        # Filter out defenses (DST)
        df = df[~df['pos'].str.contains('DST', na=False)]

        # Sort by fantasy points descending
        df = df.sort_values(by='rank', ascending=True)

        return df.to_dict(orient='records')

    except requests.RequestException as e:
        print(f"HTTP request error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
# ---------------------- ADP Data ----------------------


# ---------------------- QB Season Projections ----------------------
def load_season_projections_qb(url):
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
def load_season_projections_rb(url):
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
def load_season_projections_wr(url):
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
def load_season_projections_te(url):
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
# def load_season_projections_k(url):
#     # Fetch the page content
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')
#
#     # Locate the table containing the QB projections
#     table = soup.find('table', {'id': 'data'})
#
#     players = []
#
#     # NFL team abbreviations
#     team_abbr = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX',
#                  'KC', 'LV', 'LAC', 'LAR', 'MIA', 'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT', 'SF', 'SEA', 'TB', 'TEN', 'WAS']
#
#     for row in table.tbody.find_all('tr'):
#         cols = row.find_all('td')
#         if len(cols) > 1:
#             player_info = cols[0].text.strip()
#             fg = cols[1].text.strip()
#             fga = cols[2].text.strip()
#             xpt = cols[3].text.strip()
#             proj_points = cols[4].text.strip()
#
#             # Extract player name and team from player_info
#             player_name_parts = player_info.split()
#             team = player_name_parts[-1] if player_name_parts[-1] in team_abbr else ''
#             name = ' '.join(player_name_parts[:-1]) if team else player_info
#
#             players.append({
#                 'name': name,
#                 'team': team,
#                 'fg': fg,
#                 'fga': fga,
#                 'xpt': xpt,
#                 'proj_points': proj_points
#             })
#
#     # Convert to DataFrame
#     df = pd.DataFrame(players)
#
#     # Normalize numeric columns
#     for col in ['fg', 'fga', 'xpt', 'proj_points']:
#         df[col] = pd.to_numeric(df[col], errors='coerce')
#
#     # Drop rows with missing essential values
#     df = df.dropna(subset=['name', 'proj_points'])
#
#     # Sort by fantasy points descending
#     df = df.sort_values(by='proj_points', ascending=False)
#
#     return df.to_dict(orient='records')
# ---------------------- K Season Projections ----------------------


# ---------------------- DST Season Projections ----------------------
# def load_season_projections_dst(url):
#     # Fetch the page content
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')
#
#     # Locate the table containing the QB projections
#     table = soup.find('table', {'id': 'data'})
#
#     teams = []
#
#     for row in table.tbody.find_all('tr'):
#         cols = row.find_all('td')
#         if len(cols) > 1:
#             team = cols[0].text.strip()
#             sack = cols[1].text.strip()
#             int = cols[2].text.strip()
#             fr = cols[3].text.strip()
#             ff = cols[4].text.strip()
#             td = cols[5].text.strip()
#             safety = cols[6].text.strip()
#             pa = cols[7].text.strip()
#             yds_agn = cols[8].text.strip()
#             proj_points = cols[9].text.strip()
#
#             teams.append({
#                 'name': team,
#                 'sack': sack,
#                 'int': int,
#                 'fr': fr,
#                 'ff': ff,
#                 'td': td,
#                 'safety': safety,
#                 'pa': pa,
#                 'yds_agn': yds_agn,
#                 'proj_points': proj_points
#             })
#
#     # Convert to DataFrame
#     df = pd.DataFrame(teams)
#
#     # Normalize numeric columns
#     for col in ['sack', 'int', 'fr', 'ff', 'td', 'safety',  'pa', 'proj_points']:
#         df[col] = pd.to_numeric(df[col], errors='coerce')
#
#     # Drop rows with missing essential values
#     df = df.dropna(subset=['name', 'proj_points'])
#
#     # Sort by fantasy points descending
#     df = df.sort_values(by='proj_points', ascending=False)
#
#     return df.to_dict(orient='records')
# ---------------------- DST Season Projections ----------------------