import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# URL of the transactions page
url = "https://www.pro-football-reference.com/years/2025/05_transactions.htm"

# Set headers to mimic a browser visit
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

try:
    # Send a GET request to the page
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate the main content div where transactions are listed
    content_div = soup.find('div', {'id': 'content'})

    # Initialize a list to store transactions
    transactions = []

    # Initialize current date to associate transactions with their respective dates
    current_date = None

    # Common position abbreviations in NFL transactions
    positions = [
        "QB", "RB", "WR", "TE", "DT", "DE", "LB", "CB", "S",
        "OT", "OG", "C", "FB", "K", "P", "LS", "DL", "DB", "OL"
    ]

    # Extract all relevant tags
    for elem in content_div.find_all(['h2', 'p']):
        text = elem.get_text(strip=True)

        # Check if the text is a date (format: Month Day, Year)
        if re.match(r"^[A-Za-z]+\s\d{1,2},\s\d{4}$", text):
            current_date = text

        # Check for transaction keywords and a current date
        elif current_date and any(word in text for word in ["signed", "waived", "claimed", "released"]):
            # Fix team and transaction spacing issues
            cleaned_text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

            # Fix player name and position spacing issues
            for pos in positions:
                # Separate the position from the player's name if stuck together
                cleaned_text = re.sub(rf'({pos})([A-Z])', r'\1 \2', cleaned_text)

            # Append the date and transaction to the list
            transactions.append({
                'Date': current_date,
                'Transaction': cleaned_text
            })

    # Convert the list to a DataFrame
    df = pd.DataFrame(transactions)

    # Display the cleaned DataFrame
    print(df)

except requests.RequestException as e:
    print(f"Error while fetching the page: {e}")
