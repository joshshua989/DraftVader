# ---------------------- LIBRARIES ----------------------
import pandas as pd
import streamlit as st
# ---------------------- LIBRARIES ----------------------


# ---------------------- Age Curve Multiplier and Risk Tag DataFrame ----------------------
@st.cache_data
def apply_age_curve(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies an age-based curve to NFL player stats based on position norms.

    Adds two columns:
        - 'Age Curve Multiplier': Multiplier to apply to projections based on age.
        - 'Age Risk Tag': Human-readable tag describing age-based risk or upside.

    Args:
        nfl_player_stats_df (pd.DataFrame): Input DataFrame with at least ['Player', 'Team', 'Pos', 'Age'] columns.

    Returns:
        pd.DataFrame: Updated DataFrame with age curve info.
    """

    def get_age_curve_multiplier(pos, age):
        # Define age multipliers based on research and Best Ball data trends
        if pos == "RB":
            if age < 24:
                return 0.95
            elif age <= 26:
                return 1.0
            elif age <= 28:
                return 0.97
            elif age <= 30:
                return 0.92
            else:
                return 0.85
        elif pos == "WR":
            if age < 24:
                return 0.90
            elif age <= 26:
                return 1.05  # breakout window
            elif age <= 29:
                return 1.0
            elif age <= 32:
                return 0.95
            else:
                return 0.88
        elif pos == "TE":
            if age < 25:
                return 0.90
            elif age <= 28:
                return 1.0
            elif age <= 31:
                return 0.97
            else:
                return 0.9
        elif pos == "QB":
            if age < 25:
                return 0.9
            elif age <= 30:
                return 1.0
            elif age <= 34:
                return 1.02
            elif age <= 38:
                return 0.95
            else:
                return 0.88
        else:
            return 1.0  # default

    def get_age_tag(pos, age):
        # Tag players by age-related phases
        if pos == "RB":
            if age > 28:
                return "Decline"
            elif age < 24:
                return "Upside"
            else:
                return "Prime"
        elif pos == "WR":
            if age < 24:
                return "Raw Upside"
            elif 24 <= age <= 26:
                return "Breakout"
            elif 27 <= age <= 29:
                return "Prime"
            else:
                return "Decline"
        elif pos == "TE":
            if age < 25:
                return "Upside"
            elif 25 <= age <= 30:
                return "Prime"
            else:
                return "Decline"
        elif pos == "QB":
            if age < 25:
                return "Upside"
            elif 25 <= age <= 34:
                return "Prime"
            else:
                return "Decline"
        else:
            return "Unknown"

    df['age_curve_multiplier'] = df.apply(lambda row: get_age_curve_multiplier(row['pos'], row['age']), axis=1)
    df['age_risk_tag'] = df.apply(lambda row: get_age_tag(row['pos'], row['age']), axis=1)

    # Select only the desired columns
    age_curve_mult_df = df[['player', 'team', 'pos', 'age', 'age_curve_multiplier', 'age_risk_tag']]

    return age_curve_mult_df
# ---------------------- Age Curve Multiplier and Risk Tag DataFrame ----------------------