# ---------------------- LIBRARIES ----------------------
import pandas as pd
import streamlit as st
# ---------------------- LIBRARIES ----------------------


# Replacement-level starters per position in Best Ball
REPLACEMENT_RANK = {
    'QB': 18,
    'RB': 36,
    'WR': 48,
    'TE': 18,
}

TIER_DROP_THRESHOLDS = {
    'QB': 15,
    'RB': 12,
    'WR': 12,
    'TE': 10,
}

"""
Example Use Snapshot:

scarcity_score_df:
Name	        Pos	Proj_Pts	VoR 	Tier	ScarcityScore
Travis Kelce	TE	270	        90	    1	    9.5
TJ Hockenson	TE	200     	20	    2   	6.0
Jalen Hurts	    QB	340     	40	    1	    8.0
Chris Olave	    WR	220	        15	    3	    3.5

Summary of Use Cases in Draft Vader:
    Rank players more accurately across positions.
    Trigger draft alerts when tier cliffs are approaching.
    Drive optimal lineup constructions based on scarcity and VoR.
    Sort/filter recommendations by VoR or ScarcityScore instead of just projected points.
"""

def load_player_data(df):
    """ Takes a unified projections DataFrame and filters valid positions. """
    return df[df['pos'].isin(['QB', 'RB', 'WR', 'TE'])].reset_index(drop=True)

def calculate_value_over_replacement(df):
    """Adds a Value Over Replacement (VoR) column per position.

    🔹 VoR — Value over Replacement
    Definition: The difference between a player’s projected points and the baseline (replacement-level) player at their position.

    Why it matters: Raw fantasy points are misleading without context. For example:

    The QB1 may score 350 points, but the QB12 might score 320 — only a 30-point gap.

    Meanwhile, the TE1 might score 280, but TE12 scores just 180 — a 100-point difference.

    Use in draft strategy: Prioritize players who offer more relative value vs others at their position.

    """
    df = df.copy()
    vor_list = []

    for pos in df['pos'].unique():
        pos_df = df[df['pos'] == pos].sort_values(by='proj_points', ascending=False)
        replacement_level = REPLACEMENT_RANK.get(pos, 0)
        if replacement_level == 0 or len(pos_df) < replacement_level:
            replacement_score = pos_df['proj_points'].min()
        else:
            replacement_score = pos_df.iloc[replacement_level - 1]['proj_points']

        pos_df['VoR'] = pos_df['proj_points'] - replacement_score
        vor_list.append(pos_df)

    return pd.concat(vor_list).sort_values(by='VoR', ascending=False).reset_index(drop=True)

def calculate_positional_tiers(df):
    """Adds a Tier column by looking for steep drop-offs in points.

    🔹 Tier — Production Tier
    Definition: A grouping of players with similar projected output (often based on VoR or standard deviation gaps).

    Why it matters:

    Helps you identify where there’s a drop-off in value.

    For instance, there might be 3 elite TEs, then a steep drop. You’ll want to grab one before that cliff.

    Use in draft strategy:

    Avoid reaching for players in large tiers.

    Be aggressive when you’re near the end of a small, elite tier.
    """
    df = df.copy()
    tiered = []

    for pos in df['pos'].unique():
        pos_df = df[df['pos'] == pos].sort_values(by='proj_points', ascending=False).reset_index(drop=True)
        drop_threshold = TIER_DROP_THRESHOLDS.get(pos, 10)

        tiers = []
        tier = 1
        for i in range(len(pos_df)):
            if i == 0:
                tiers.append(tier)
                continue
            point_drop = pos_df.loc[i-1, 'proj_points'] - pos_df.loc[i, 'proj_points']
            if point_drop > drop_threshold:
                tier += 1
            tiers.append(tier)

        pos_df['Tier'] = tiers
        tiered.append(pos_df)

    return pd.concat(tiered).sort_values(by='VoR', ascending=False).reset_index(drop=True)

def get_scarcity_score(df, elite_tier_weight=1.25):
    """Returns scarcity score as a multiplier for boosting players in elite/sparse tiers.

    🔹 ScarcityScore — Positional Scarcity Metric
    Definition: A weighted score capturing how rare it is to find fantasy value at that position.

    Often factors in: starting lineup requirements, positional depth, drop-off steepness.

    Why it matters:

    It quantifies how “painful” it is to miss on a position.

    For example: in Best Ball, elite TEs and dual-threat QBs often carry high ScarcityScores.

    Use in draft strategy:

    Helps determine when to zig while others zag (e.g., take a TE early while others load up on WRs).

    Drives optimal roster construction (e.g., 3 RBs early, then pound WRs).
    """
    df = df.copy()

    # Simple rule: elite tier gets a boost; tier 3+ gets a mild downgrade
    def boost(row):
        if row['Tier'] == 1:
            return row['VoR'] * elite_tier_weight
        elif row['Tier'] <= 2:
            return row['VoR']
        else:
            return row['VoR'] * 0.9  # Mild penalty for deep tiers

    df['ScarcityScore'] = df.apply(boost, axis=1)

    df.sort_values(by='ScarcityScore', ascending=False).reset_index(drop=True)

    # Check if the message has been shown before printing to terminal
    if 'positional_scarcity_shown' not in st.session_state:
        print("---------------------------------------------------------------")
        print(f"\n////////// Positional Scarcity //////////\n")
        print("---------------------------------------------------------------")
        st.session_state['positional_scarcity_shown'] = True
    # Print DataFrame preview to terminal
    print("\n")
    print(df)
    print("---------------------------------------------------------------")

    return df