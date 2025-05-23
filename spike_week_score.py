# ---------------------- Libraries ----------------------
import streamlit as st
import nfl_data_py as nfl
# ---------------------- Libraries ----------------------


# ---------------------- Script Functions ----------------------
# Function to count games above a given PPR threshold
def count_games_above_threshold(df, threshold):
    return (
        df[df['fantasy_points_ppr'] > threshold]
        .groupby('player_display_name')
        .size()
        .reset_index(name=f'over_{threshold}_ppr_count')
    )

# Function to count games below a given PPR threshold
def count_games_below_threshold(df, threshold):
    return (
        df[df['fantasy_points_ppr'] <= threshold]
        .groupby('player_display_name')
        .size()
        .reset_index(name=f'under_{threshold}_ppr_count')
    )

# Function to count total games played per player
def count_total_games(df):
    return (
        df.groupby('player_display_name')
        .size()
        .reset_index(name='total_games')
    )

# Function to calculate the Spike Week Score
def calculate_spike_score(row):
    # Assign weights for boom and bust week rates
    weights = {
        'boom_30': 3.0,
        'boom_25': 2.0,
        'boom_20': 1.0,
        'bust_5': -3.0,
        'bust_10': -2.0,
        'bust_15': -1.0,
    }

    # Calculate the weighted score
    spike_score = (
        weights['boom_30'] * row['over_30_ppr_percentage'] +
        weights['boom_25'] * row['over_25_ppr_percentage'] +
        weights['boom_20'] * row['over_20_ppr_percentage'] +
        weights['bust_5'] * row['under_5_ppr_percentage'] +
        weights['bust_10'] * row['under_10_ppr_percentage'] +
        weights['bust_15'] * row['under_15_ppr_percentage']
    )
    return spike_score
# ---------------------- Script Functions ----------------------


# ---------------------- Organize by Condition ----------------------
@st.cache_data
def organize_by_condition(years):
    print("---------------------------------------------------------------")
    print("\n////////// SPIKE WEEK SCORES //////////\n")
    print("---------------------------------------------------------------")
    print(f"⏳ Importing weekly NFL data from {years} ...")

    # Imports weekly NFL data for the specified years using the nfl library.
    weekly_data = nfl.import_weekly_data(years)

    # Calculate games over 20, 25, and 30 PPR points (Boom)
    over_20_ppr = count_games_above_threshold(weekly_data, 20)
    over_25_ppr = count_games_above_threshold(weekly_data, 25)
    over_30_ppr = count_games_above_threshold(weekly_data, 30)

    # Calculate games under 5, 10, and 15 PPR points (Bust)
    under_5_ppr = count_games_below_threshold(weekly_data, 5)
    under_10_ppr = count_games_below_threshold(weekly_data, 10)
    under_15_ppr = count_games_below_threshold(weekly_data, 15)

    # Calculate the total number of games played per player
    total_games = count_total_games(weekly_data)

    # Merge all dataframes
    merged = (
        total_games
        .merge(over_30_ppr, on='player_display_name', how='outer')
        .merge(over_25_ppr, on='player_display_name', how='outer')
        .merge(over_20_ppr, on='player_display_name', how='outer')
        .merge(under_15_ppr, on='player_display_name', how='outer')
        .merge(under_10_ppr, on='player_display_name', how='outer')
        .merge(under_5_ppr, on='player_display_name', how='outer')
        .fillna(0)
    )

    # Calculate percentages for each category with two decimal places (as floats)
    for threshold in [30, 25, 20]:
        merged[f'over_{threshold}_ppr_percentage'] = (
            (merged[f'over_{threshold}_ppr_count'] / merged['total_games'] * 100).round(2)
        )
    for threshold in [15, 10, 5]:
        merged[f'under_{threshold}_ppr_percentage'] = (
            (merged[f'under_{threshold}_ppr_count'] / merged['total_games'] * 100).round(2)
        )

    print("⏳ Calculating 'Spike Week' scores ...")
    # Calculate the Spike Week Score
    merged['spike_week_score'] = merged.apply(calculate_spike_score, axis=1)

    # Reorder columns to put 'spike_week_score' in the second position
    cols = list(merged.columns)
    cols.insert(1, cols.pop(cols.index('spike_week_score')))
    merged = merged[cols]

    # Sort the merged dataframe by Spike Week Score in descending order
    top_10 = merged.sort_values(by='spike_week_score', ascending=False).head(10)

    # Print the top 10 players with boom, bust, spike week scores, and total games played
    print("\nTop 10 Players by Spike Week Score:\n")
    for index, row in top_10.iterrows():
        print(f"{row['player_display_name']}: {int(row['total_games'])} total games\n"
              f"Spike Week Score: {row['spike_week_score']:.2f}\n"
              f"{int(row['over_20_ppr_count'])} games over 20, {int(row['over_25_ppr_count'])} over 25, "
              f"{int(row['over_30_ppr_count'])} over 30\n"
              f"{int(row['under_5_ppr_count'])} under 5, {int(row['under_10_ppr_count'])} under 10, "
              f"{int(row['under_15_ppr_count'])} under 15")
        print("---------------------------------------------------------------")

    return merged
# ---------------------- Organize by Condition ----------------------