import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
# ---------------------- Libraries ----------------------


# ---------------------- Get Injury Reports ----------------------
@st.cache_data
def get_injury_reports(urls):

    # Check if the message has been shown before printing to terminal
    if 'injury_reports_shown' not in st.session_state:
        print("---------------------------------------------------------------")
        print(f"\n////////// Injury Reports //////////\n")
        print("---------------------------------------------------------------")
        st.session_state['injury_reports_shown'] = True

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    injury_data = []

    for url in urls:
        print(f"Scraping: {url}")
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        articles = soup.find_all("div", class_="player-news-item")

        for article in articles:
            try:
                # Headline
                headline_tag = article.find("div", class_="player-news-header").find("a")
                headline = headline_tag.text.strip() if headline_tag else None

                # Date
                date_tag = article.find("div", class_="player-news-header").find("p")
                date = date_tag.text.strip().split("By")[0].strip() if date_tag else None

                # Description: find the first <p> directly following the .player-news-header block
                ten_columns_div = article.find("div", class_="ten columns")
                p_tags = ten_columns_div.find_all("p", recursive=False)  # only direct children

                # We expect:
                # - p[0] is inside .player-news-header (author/date)
                # - p[1] is the description
                # - p[2] is the fantasy impact
                description = None
                fantasy_impact = None
                found_description = False

                for p in p_tags:
                    text = p.get_text(strip=True)
                    if not found_description and "Fantasy Impact" not in text and "By" not in text:
                        description = text
                        found_description = True
                    elif "Fantasy Impact" in text:
                        fantasy_impact = text.replace("Fantasy Impact:", "").strip()
                        break

                injury_data.append({
                    "headline": headline,
                    "date": date,
                    "description": description,
                    "fantasy_impact": fantasy_impact
                })

            except Exception as e:
                print(f"Error parsing article: {e}")

    # Convert to DataFrame
    df = pd.DataFrame(injury_data)

    # Extract player_name from the first two words of the headline
    def extract_player_name(headline):
        if pd.isna(headline):
            return None
        words = headline.split()
        return " ".join(words[:2]) if len(words) >= 2 else headline

    df.insert(0, 'player_name', df['headline'].apply(extract_player_name))

    print("")
    print(df.head())
    print("---------------------------------------------------------------")

    # Optional: Save to CSV
    # df.to_csv("fantasypros_injury_news.csv", index=False)

    return df
# ---------------------- Get Injury Reports ----------------------