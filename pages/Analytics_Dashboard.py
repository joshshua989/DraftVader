# ---------------------- LIBRARIES ----------------------
import streamlit as st
import analytics_dashboard
# ---------------------- LIBRARIES ----------------------

# ---------------------- Initialize Session State ----------------------
positions = ['qb', 'rb', 'wr', 'te']
adp_data = {}
season_projections = {}

for pos in positions:
    adp_key = f'adp_data_{pos}'
    proj_key = f'season_projections_{pos}'

    if adp_key in st.session_state:
        adp_data[pos] = st.session_state[adp_key]
    else:
        st.warning(f"No {pos.upper()} ADP DataFrame found in session_state.")

    if proj_key in st.session_state:
        season_projections[pos] = st.session_state[proj_key]
    else:
        st.warning(f"No {pos.upper()} season projections DataFrame found in session_state.")
# ---------------------- Initialize Session State ----------------------

# ---------------------- Analytics Dashboard ----------------------
if 'value_vs_adp_shown' not in st.session_state:
    print("---------------------------------------------------------------")
    print("\n////////// VALUE VS. ADP - to gauge value picks. //////////\n")
    st.session_state['value_vs_adp_shown'] = True

st.subheader("📊 Analytics Dashboard")

tabs = st.tabs([pos.upper() for pos in positions])

for i, pos in enumerate(positions):
    with tabs[i]:
        if pos in adp_data and pos in season_projections:
            df = analytics_dashboard.calculate_value_vs_adp(pos.upper(), adp_data[pos], season_projections[pos])
            df = df[df['adp'] <= 300]  # Filter out players with ADP > 300
            df = df.sort_values(by='value_vs_adp', ascending=False).head(100)  # Keep top 100 players
            st.write("---")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.error(f"Missing data for {pos.upper()} - skipping analysis.")
# ---------------------- Analytics Dashboard ----------------------