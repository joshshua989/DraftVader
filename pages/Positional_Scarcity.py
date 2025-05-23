# ---------------------- LIBRARIES ----------------------
import streamlit as st
import plotly.express as px
# ---------------------- LIBRARIES ----------------------


# ---------------------- Initialize Session State ----------------------
# Positional Scarcity DataFrame
if 'positional_scarcity_df' in st.session_state:
    positional_scarcity_df = st.session_state['positional_scarcity_df']
else:
    st.write("No DataFrame found in session_state.")
# ---------------------- Initialize Session State ----------------------


# ---------------------- Positional Spread Visualization ----------------------
# 📊 Purpose
#     The violin/box plot compares positional depth and distribution of fantasy value (either Projected Points or Value over Replacement [VoR]) across positions (QB, RB, WR, TE).
#
# 🧠 How to Read It
#     1. X-Axis = Positions
#         Each position (QB, RB, WR, TE) has its own distribution.
#
#     2. Y-Axis = Chosen Metric
#     Either:
#         Projected Points → Raw expected fantasy points.
#         Value over Replacement (VoR) → A player’s value relative to a "replacement-level" player at their position. Higher VoR = greater relative advantage.
#
#     3. Violin Plot (if selected):
#         Shows the full distribution shape of player values for each position.
#         Wider = more players with that value.
#         Long thin tails = rare high or low values.
#         Helps spot positional scarcity and upside distribution.
#     4. Box Plot (if selected):
#     Displays:
#         Median line (middle of the data)
#         Interquartile range (IQR) = the box
#         Whiskers = the spread
#         Outliers = top-end (e.g. Travis Kelce or CMC)
#
# 🔥 What to Look For
#     Insight	                            Meaning
#     Taller or fatter distributions	    Deeper positions with more viable options (e.g. WR)
#     Skinnier distributions	            Scarce positions (e.g. TE)
#     High VoR outliers	                Game-changing players (e.g. Kelce, Jefferson)
#     Position with highest median VoR	Often the one with the biggest edge to target early
#     Steep drop-off in VoR	            Indicates early positional scarcity (e.g. elite TEs)
#
# 🧭 How This Helps Draft Strategy
#     See where positional drop-offs occur (e.g., TE1 vs TE5 might be a chasm, while WR10–WR25 are close).
#     Target players with high VoR and scarcity to gain weekly edge.
#     Helps decide if TE3 is more valuable than WR12, for example.
#     Useful for planning early-round decisions and roster construction.

st.subheader("📈 Positional Spread Visualization")

# Axis + plot type selectors
y_axis_option = st.radio(
    "Select Y-axis metric:",
    ["Projected Points", "Value over Replacement"],
    key="y_axis_toggle"
)

plot_type = st.radio(
    "Select plot type:",
    ["Violin Plot", "Box Plot"],
    key="plot_type_toggle"
)

range_option = st.selectbox(
    "Player range:",
    ["All players", "Top 50 per position", "Top 15 per position", "Top 16–30 per position"],
    key="range_select"
)

# Choose column
y_col = "proj_points" if y_axis_option == "Projected Points" else "VoR"

# Filter based on range
def filter_by_range(df, option):
    if option == "All players":
        return df
    elif option == "Top 50 per position":
        return df.groupby("pos").apply(lambda x: x.nlargest(50, y_col)).reset_index(drop=True)
    elif option == "Top 15 per position":
        return df.groupby("pos").apply(lambda x: x.nlargest(15, y_col)).reset_index(drop=True)
    elif option == "Top 16–30 per position":
        return df.groupby("pos").apply(lambda x: x.nlargest(30, y_col).nsmallest(15, y_col)).reset_index(drop=True)

# Load and filter
df = filter_by_range(positional_scarcity_df, range_option)

# Plot
if plot_type == "Violin Plot":
    fig = px.violin(
        df,
        x="pos",
        y=y_col,
        color="pos",
        box=True,
        points="all",
        hover_data=["name", "team", "Tier"],
        title=f"{y_axis_option} Distribution by Position (Violin Plot)"
    )
else:
    fig = px.box(
        df,
        x="pos",
        y=y_col,
        color="pos",
        points="all",
        hover_data=["name", "team", "Tier"],
        title=f"{y_axis_option} Distribution by Position (Box Plot)"
    )

fig.update_layout(
    xaxis_title="Position",
    yaxis_title=y_axis_option,
    showlegend=False,
    height=600
)

st.plotly_chart(fig, use_container_width=True)
# ---------------------- Positional Spread Visualization ----------------------

# TODO: Update code so that the dataframe output matches the selected selectbox position ["ALL", "QB", "RB", "WR", "TE"]
st.dataframe(positional_scarcity_df)

# ---------------------- Tiered Value Scatter Plot Visualization ----------------------
# """
# Projected Points alone doesn’t account for the positional context. A WR projected for 200 points sounds great — but if WRs 10–20 are all within 10 points, that 200-point WR isn’t as special as a TE projected for 160 when the next best TE has 120.
#
# 🔍 VoR gives you contextual value:
# Player	Position	Projected Points	Replacement Level	VoR
# WR1	WR	200	170	30
# TE1	TE	160	110	50
#
# TE1 has a higher VoR than WR1, meaning TE1 gives you a greater edge at their position.
#
# If you draft based on raw points, you might wrongly prioritize WR1.
#
# Drafting by VoR helps you exploit positional scarcity — TE1 is harder to replace than WR1.
#
# 🔄 Switching Y-axis to VoR:
# Highlights players that truly separate from the pack.
#
# Makes cross-positional comparisons more meaningful.
#
# Helps answer: “Who gives me the most edge over my league?”
# """

# Assume season_projections_df_all already exists with these columns:
# ['name', 'team', 'pos', 'proj_points', 'VoR', 'Tier']

st.header("📊 Tiered Value Visualization")

# Toggle for player range
range_option = st.selectbox(
    "Select player range to display:",
    ["All players", "Top 15 per position", "Top 16–30 per position"]
)

# Toggle for Y-axis metric
y_axis_option = st.radio(
    "Select Y-axis metric:",
    ["Projected Points", "Value over Replacement"]
)

# Select y-axis column
y_axis_col = "proj_points" if y_axis_option == "Projected Points" else "VoR"

# Filter based on selected range
def filter_by_range(df, range_option):
    if range_option == "All players":
        return df
    elif range_option == "Top 15 per position":
        return df.groupby('pos').apply(lambda x: x.nlargest(15, y_axis_col)).reset_index(drop=True)
    elif range_option == "Top 16–30 per position":
        return df.groupby('pos').apply(lambda x: x.nlargest(30, y_axis_col).nsmallest(15, y_axis_col)).reset_index(drop=True)

filtered_df = filter_by_range(positional_scarcity_df, range_option)

# Sort for better tier drawing
filtered_df = filtered_df.sort_values(by=["pos", "Tier", y_axis_col], ascending=[True, True, False])

# Plotting with tier-based color bands
fig = px.scatter(
    filtered_df,
    x="pos",
    y=y_axis_col,
    color="Tier",
    hover_data=["name", "team", "proj_points", "VoR"],
    symbol="pos",
    title="Positional Tiers by " + y_axis_option,
)

# Add dropoff lines between tiers
for pos in filtered_df['pos'].unique():
    tiers = filtered_df[filtered_df['pos'] == pos]['Tier'].unique()
    for tier in tiers:
        tier_df = filtered_df[(filtered_df['pos'] == pos) & (filtered_df['Tier'] == tier)]
        if not tier_df.empty:
            drop_y = tier_df[y_axis_col].min()
            fig.add_shape(
                type="line",
                x0=pos,
                x1=pos,
                y0=drop_y,
                y1=drop_y - 3,  # Dropoff bar size
                line=dict(color="gray", width=1, dash="dot"),
            )

fig.update_layout(
    xaxis_title="Position",
    yaxis_title=y_axis_option,
    height=600
)

st.plotly_chart(fig, use_container_width=True)
# ---------------------- Tiered Value Scatter Plot Visualization ----------------------

# ---------------------- Cross-Positional Tier Scatter Plot Visualization ----------------------
# Limit to top 15 players by projected points per position
N = 15
df_top = positional_scarcity_df.groupby("pos", group_keys=False).apply(lambda x: x.nlargest(N, "proj_points"))

# Ensure Tier is treated as a categorical value (helps with axis order)
df_top["Tier"] = df_top["Tier"].astype(str)

# Create Plotly scatter plot
fig = px.scatter(
    df_top,
    x="Tier",
    y="proj_points",
    color="pos",
    hover_data=["name", "team", "pos", "Tier", "proj_points", "VoR", "ScarcityScore"],
    title="Cross-Positional Tier Breakdown (Top 15 per Position)",
    labels={
        "proj_points": "Projected Points",
        "Tier": "Tier"
    },
    category_orders={"Tier": sorted(df_top["Tier"].unique(), key=lambda x: int(x))},
    height=600
)

fig.update_traces(marker=dict(size=10, opacity=0.7), selector=dict(mode='markers'))
fig.update_layout(legend_title_text='Position')

# Display in Streamlit
st.plotly_chart(fig, use_container_width=True)
# ---------------------- Cross-Positional Tier Scatter Plot Visualization ----------------------
# ---------------------- (MOVE-TO) Positional_Scarcity.py ----------------------