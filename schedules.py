# ---------------------- Libraries ----------------------
import requests
import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
# ---------------------- Libraries ----------------------


# ---------------------- get_schedules() ----------------------
@st.cache_data
def get_schedules(year, url):

    # Check if the message has been shown before printing to terminal
    if 'nfl_schedule_shown' not in st.session_state:
        print("---------------------------------------------------------------")
        print(f"\n////////// {year} Season Schedule //////////\n")
        print("---------------------------------------------------------------")
        st.session_state['nfl_schedule_shown'] = True

    # Send a GET request to the webpage
    response = requests.get(url)
    response.raise_for_status()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    print(f"Scraping {year} Season Schedule from '{url}' ... ")

    # Find the main table containing the game data
    table = soup.find("table", {"id": "games"})

    # Extract table headers
    headers = [th.get_text() for th in table.find("thead").find_all("th")][1:]  # Skip the first empty header

    # Extract table rows
    rows = []
    for tr in table.find("tbody").find_all("tr"):
        # Skip rows that are just spacing or section headers
        if 'class' in tr.attrs and "thead" in tr['class']:
            continue
        # Extract individual cell data
        cells = [td.get_text() for td in tr.find_all("td")]
        if cells:
            rows.append(cells)

    # Convert to DataFrame
    df = pd.DataFrame(rows, columns=headers)

    print("Data Summary:")
    print(df.head())
    print("---------------------------------------------------------------")

    # # Save to CSV
    # df.to_csv(f"nfl_schedule_{year}.csv", index=False)
    # print(f"Scraping complete. Data saved to nfl_schedule_{year}.csv")

    return df
# ---------------------- get_schedules() ----------------------
