# ---------------------- LIBRARIES ----------------------
import streamlit as st
# ---------------------- LIBRARIES ----------------------


# ---------------------- Rookie Rankings ----------------------
st.subheader("🎓 Rooking Rankings")

# Output as a dataframe:
st.dataframe(st.session_state.rookie_rankings_df, use_container_width=True, hide_index=True)
# ---------------------- Rookie Rankings ----------------------