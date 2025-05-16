# ---------------------- Libraries ----------------------
import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
# ---------------------- Libraries ----------------------


# ---------------------- Data Manipulation Functions ----------------------
@st.cache_data
def calculate_value_vs_adp(position, adp, projected_fpts):
    """
    Calculate ADP implied points based on historical data using linear regression.

    Parameters:
        adp_df (pd.DataFrame): DataFrame containing 'player_name' and 'adp'.
        points_df (pd.DataFrame): DataFrame containing 'player_name' and 'fantasy_points'.

    Returns:
        pd.DataFrame: DataFrame with player name, ADP, and implied points.
    """

    # Checks the data type of the variables adp and projected_fpts.
    # If adp is a list, it converts the list into a Pandas DataFrame.
    if isinstance(adp, list):
        adp = pd.DataFrame(adp)
    # If projected_fpts is a list, it converts it into a Pandas DataFrame.
    if isinstance(projected_fpts, list):
        projected_fpts = pd.DataFrame(projected_fpts)
    # Further... This is useful when the input data can come in different formats (like a list or a DataFrame).
    # Further... Ensures consistency in data processing by always working with DataFrames after these checks.

    print("---------------------------------------------------------------")
    print(f"⏳ Merging ADP dataframe (x) and {position} Season Projections dataframe (y) ...")
    # Merge ADP and points data on player name
    data = pd.merge(adp, projected_fpts, on="name")

    # Reshape data for linear regression
    X = data['adp'].values.reshape(-1, 1)  # ADP as independent variable
    y = data['proj_points'].values  # Fantasy points as dependent variable

    print("⏳ Fitting a linear regression model ...")
    # Fit a linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict implied points based on ADP
    data['implied_points'] = model.predict(X)

    print("⏳ Plotting the regression line ...")
    # Plotting the regression line
    plt.figure(figsize=(8, 5))
    plt.scatter(data['adp'], data['proj_points'], color='blue', label=f"{position} Data")
    plt.plot(data['adp'], data['implied_points'], color='red', label='Regression Line (Implied Points)')
    plt.xlabel('ADP')
    plt.ylabel('2025 Projected Fantasy Points')
    plt.title(f"ADP Implied Fantasy Points Study - {position}")
    plt.legend()

    # Display the scatter plot graphs
    st.markdown(f"<p style='color: lightblue;'>🤖 <strong>{position} Value vs. ADP Analysis:</strong></p>", unsafe_allow_html=True)
    st.pyplot(plt.gcf()) # Display the plot in Streamlit

    data['value_vs_adp'] = y - data['implied_points']

    print(f"🧠 {position} Value vs. ADP data saved to memory!\n")
    print("Data Summary:")
    print(f"{data[['name', 'adp', 'proj_points', 'implied_points', 'value_vs_adp']].head()}")

    return data[['name', 'adp', 'proj_points', 'implied_points', 'value_vs_adp']]
# ---------------------- Data Manipulation Functions ----------------------