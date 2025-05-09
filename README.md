## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/joshshua989/DraftVader.git

# 🏈 Draft Vader v1.0 🤖

DraftVader is an AI-powered fantasy football draft assistant that leverages machine learning to make data-driven predictions and recommendations during fantasy drafts.

## 🚀 Features

* **Automated Draft Order:** Automatically tracks the draft order and current pick.
* **Player Recommendations:** Uses ADP data to suggest optimal picks.
* **Custom Team Management:** Easily track drafted players and team compositions.
* **User-Friendly Interface:** Intuitive and clean Streamlit UI.
* **Session Management:** Save and load draft sessions for easy resumption.

## 🛠️ Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/joshshua989/DraftVader.git
   cd DraftVader
   ```
2. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

## 🏃 Usage

1. Start the Streamlit app:

   ```bash
   streamlit run draft_vader-v1.0.py
   ```
2. Access the app in your browser at:

   ```
   ```

[http://localhost:8501](http://localhost:8501)

````
3. Log in to access the draft interface.

## 📝 How to Draft
- Use the dropdowns to select a player and team.
- Click the "Draft" button to add the player to the selected team.
- The draft board and team rosters update automatically.

## ⚙️ Configuration
- Customize the number of teams and rounds in the configuration section.
- Modify ADP scraping settings through the `load_adp_data()` function.

## 📂 File Structure
- `draft_vader-v1.0.py`: Main Streamlit application.
- `scraper.py`: Web scraping utilities.
- `load_stats.py`: Data loading and processing.
- `README.md`: This documentation file.

## 💡 Troubleshooting
- If ADP data fails to load, check your internet connection and try restarting the app.
- To reset the draft state, clear the Streamlit cache:
```bash
streamlit cache clear
````

## 📝 Contributing

Feel free to submit issues or pull requests to improve Draft Vader. Contributions are welcome!

## 📜 License

Draft Vader is licensed under the MIT License.

Happy drafting! 🎉
