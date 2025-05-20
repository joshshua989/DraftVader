# ---------------------- LIBRARIES ----------------------
import streamlit as st
from schedules import get_schedules
# ---------------------- LIBRARIES ----------------------


# ---------------------- Season Schedule ----------------------
# TODO: determine year to use based on if schedule is out yet or not
# current_year = datetime.now().year
# current_month = datetime.now().month
year = "2025"
st.subheader(f"📅 {year} NFL Season Schedule")
schedules_df = get_schedules(year, f"https://www.pro-football-reference.com/years/{year}/games.htm")

# Optionally: Fix empty or duplicate names manually
schedules_df.columns = ['Day', 'Week', 'VisTm', 'VisPts', 'At', 'HomeTm', 'HomePts', 'Time']

st.dataframe(schedules_df, use_container_width=True, hide_index=True)
# ---------------------- Season Schedule ----------------------