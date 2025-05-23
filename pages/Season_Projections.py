# ---------------------- LIBRARIES ----------------------
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
# ---------------------- LIBRARIES ----------------------

# ---------------------- Initialize Session State ----------------------
if 'positional_scarcity_df' in st.session_state:
    positional_scarcity_df = st.session_state['positional_scarcity_df']
else:
    st.warning("No DataFrame found in session_state.")
    st.stop()
# ---------------------- Initialize Session State ----------------------

# ---------------------- Tiered Fantasy Projections ----------------------
# What This Shows:
#     Players grouped by Tier, sorted by projected points within each Tier.
#     Visually highlights where value drops off (tier cliffs).
#     Works across positions or a single position like TE or WR.

# TODO: Highlight the user’s drafted players (if integrated with draft logic).

# TODO: Add a line plot of average VoR per tier to emphasize value gaps.
# TODO: Add positional scarcity bands or dropoff lines

# Plot tiers
st.subheader(f"📊 Tiered Fantasy Projections")

# Optional: narrow down to specific positions
position = st.selectbox("Select position to view tiers", ["ALL", "QB", "RB", "WR", "TE"])

if position != "ALL":
    df = positional_scarcity_df[positional_scarcity_df['pos'] == position]
else:
    df = positional_scarcity_df.copy()

# Sort by Tier then projected points
df = df.sort_values(by=['Tier', 'proj_points'], ascending=[True, False])

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(
    data=df,
    x='name',
    y='proj_points',
    hue='Tier',
    dodge=False,
    palette='Set2',
    ax=ax
)

plt.xticks(rotation=75, ha='right', fontsize=8)
plt.ylabel("Projected Points")
plt.xlabel("Player")
plt.title(f"{position} Tiers — Fantasy Points vs Tier")
plt.legend(title='Tier', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
st.pyplot(fig)
# ---------------------- Tiered Fantasy Projections ----------------------

# ---------------------- Section: Positional Scarcity Heatmap ----------------------
st.markdown("### 🔥 Positional Scarcity Overview")

scarcity_df = df.groupby(['pos', 'Tier']).agg({
    'VoR': 'mean',
    'proj_points': 'mean'
}).reset_index()

scarcity_pivot = scarcity_df.pivot(index="pos", columns="Tier", values="VoR")

fig2, ax2 = plt.subplots(figsize=(10, 4))
sns.heatmap(scarcity_pivot, annot=True, cmap="coolwarm", fmt=".1f", linewidths=0.5, ax=ax2)

ax2.set_title("Average Value over Replacement (VoR) by Position & Tier")
plt.tight_layout()
st.pyplot(fig2)
# ---------------------- End Heatmap ----------------------