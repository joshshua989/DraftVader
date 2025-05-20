# ---------------------- LIBRARIES ----------------------
from datetime import datetime
import pandas as pd
import streamlit as st
from schedules import get_schedules
# ---------------------- LIBRARIES ----------------------


# ---------------------- Season Schedule ----------------------
# TODO: determine year to use based on if schedule is out yet or not
# current_year = datetime.now().year
# current_month = datetime.now().month

year = "2025"
st.subheader(f"📅 {year} NFL Season Schedule")

# Get the raw schedule
schedules_df = get_schedules(year, f"https://www.pro-football-reference.com/years/{year}/games.htm")

# Rename columns to your standard names
schedules_df.columns = ['Day', 'Date', 'VisTm', 'VisPts', 'At', 'HomeTm', 'HomePts', 'Time']

# Filter out rows where Week is NaN (preseason or malformed rows)
schedules_df = schedules_df[schedules_df['Date'].notna()]

# Convert 'Date' to datetime format
schedules_df['Date'] = pd.to_datetime(schedules_df['Date'] + f" {year}")

# Define week mapping based on date ranges
week_map = [
    ("Pre-season Week 1", datetime(2025, 7, 31), datetime(2025, 7, 31)),
    ("Pre-season Week 2", datetime(2025, 8, 7), datetime(2025, 8, 10)),
    ("Pre-season Week 3", datetime(2025, 8, 14), datetime(2025, 8, 18)),
    ("Pre-season Week 4", datetime(2025, 8, 21), datetime(2025, 8, 23)),
    ("Regular Season Week 1", datetime(2025, 9, 4), datetime(2025, 9, 8)),
    ("Regular Season Week 2", datetime(2025, 9, 11), datetime(2025, 9, 15)),
    ("Regular Season Week 3", datetime(2025, 9, 18), datetime(2025, 9, 22)),
    ("Regular Season Week 4", datetime(2025, 9, 25), datetime(2025, 9, 29)),
    ("Regular Season Week 5", datetime(2025, 10, 2), datetime(2025, 10, 6)),
    ("Regular Season Week 6", datetime(2025, 10, 9), datetime(2025, 10, 13)),
    ("Regular Season Week 7", datetime(2025, 10, 16), datetime(2025, 10, 20)),
    ("Regular Season Week 8", datetime(2025, 10, 23), datetime(2025, 10, 27)),
    ("Regular Season Week 9", datetime(2025, 10, 30), datetime(2025, 11, 3)),
    ("Regular Season Week 10", datetime(2025, 11, 6), datetime(2025, 11, 10)),
    ("Regular Season Week 11", datetime(2025, 11, 13), datetime(2025, 11, 17)),
    ("Regular Season Week 12", datetime(2025, 11, 20), datetime(2025, 11, 24)),
    ("Regular Season Week 13", datetime(2025, 11, 27), datetime(2025, 12, 1)),
    ("Regular Season Week 14", datetime(2025, 12, 4), datetime(2025, 12, 8)),
    ("Regular Season Week 15", datetime(2025, 12, 11), datetime(2025, 12, 15)),
    ("Regular Season Week 16", datetime(2025, 12, 18), datetime(2025, 12, 22)),
    ("Regular Season Week 17", datetime(2025, 12, 25), datetime(2025, 12, 29)),
    ("Regular Season Week 18", datetime(2026, 1, 1), datetime(2026, 1, 5)),
]

# Assign week based on date
def assign_week(date):
    for week_label, start, end in week_map:
        if start <= date <= end:
            return week_label
    return "Unknown"

schedules_df['week'] = schedules_df['Date'].apply(assign_week)

# Get unique weeks and sort
unique_weeks = list(dict.fromkeys(schedules_df['week'].dropna()))  # preserve order, remove duplicates

# Generate week options
preseason_weeks = [f"Pre-season Week {i}" for i in range(1, 5)]
regular_season_weeks = [f"Regular Season Week {i}" for i in range(1, 19)]
all_weeks = preseason_weeks + regular_season_weeks

# Create selectbox with custom week labels
selected_week = st.selectbox("Select Week", unique_weeks)

# Filter the dataframe by the selected week
filtered_df = schedules_df[schedules_df['week'] == selected_week]

# Display filtered dataframe
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
# ---------------------- Season Schedule ----------------------