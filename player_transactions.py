import requests
import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import re

@st.cache_data
def get_player_transactions(month, url):
    """
            Fetches and parses NFL player transactions from the specified URL.

            Args:
                month (str): Month for which transactions are being fetched (used for display context).
                url (str): URL to the NFL transaction page.

            Returns:
                pd.DataFrame: A DataFrame containing transaction dates and descriptions.
            """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        content_div = soup.find('div', {'id': 'content'})

        transactions = []
        current_date = None

        positions = [
            "QB", "RB", "WR", "TE", "DT", "DE", "LB", "CB", "S",
            "OT", "OG", "G", "C", "FB", "K", "P", "LS", "DL", "DB", "OL"
        ]

        keywords = ["Signed", "Re-Signed", "Waived", "Claimed", "Released", "Activated", "Placed", "Traded"]

        for elem in content_div.find_all(['h2', 'p']):
            text = elem.get_text(strip=True)

            if re.match(r"^[A-Za-z]+\s\d{1,2},\s\d{4}$", text):
                current_date = text

            elif current_date and any(word.lower() in text.lower() for word in keywords):
                # Fix "TheBaltimore" → "The Baltimore"
                text = re.sub(r'(The)([A-Z])', r'\1 \2', text)

                # Fix missing space between lowercase and keyword (e.g. "Ravenssigned")
                for keyword in keywords:
                    text = re.sub(rf'([a-z])({keyword})', r'\1 \2', text, flags=re.IGNORECASE)

                # Fix position abbreviation glued to player name, excluding "CB"
                for pos in positions:
                    text = re.sub(rf'({pos})([A-Z])', r'\1 \2', text)

                # Fix player last name glued to "to", "on", "from" but exclude "season"
                # This avoids splitting "2025 season"
                def fix_glued(match):
                    word = match.group(2)
                    if word.lower() == "season":
                        return match.group(1) + word
                    else:
                        return match.group(1) + " " + word

                text = re.sub(r'([a-zA-Z])(?=(to|on|from|season)\b)', r'\1 ',
                              text)  # add space before to/on/from/season first
                # Then correct "season" back to no space (undo)
                text = re.sub(r'([a-zA-Z])\s(season\b)', fix_glued, text, flags=re.IGNORECASE)

                # Fix "theTeam" → "the Team"
                text = re.sub(r'\b(the)([A-Z])', r'\1 \2', text, flags=re.IGNORECASE)

                transactions.append({
                    'Date': current_date,
                    'Transaction': text
                })

        df = pd.DataFrame(transactions)
        return df

    except requests.RequestException as e:
        print(f"Error while fetching the page: {e}")
        return pd.DataFrame()