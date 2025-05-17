import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the 2025 NFL games page
url = 'https://www.pro-football-reference.com/years/2025/games.htm'

# Send a GET request to the URL
response = requests.get(url)
response.raise_for_status()  # Raise an exception for HTTP errors

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Find the table containing the game data
table = soup.find('table', id='games')

# Check if the table was found
if table:
    # Read the table into a pandas DataFrame
    df = pd.read_html(str(table))[0]

    # Display the first few rows of the DataFrame
    print(df.head())
else:
    print("Game table not found on the page.")