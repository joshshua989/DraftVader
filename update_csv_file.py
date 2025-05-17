import pandas as pd

# Load the CSV file
file1 = pd.read_csv('nfl_player_data_2022.csv')
file2 = pd.read_csv('nfl_player_data_2023.csv')
file3 = pd.read_csv('nfl_player_data_2024.csv')

# Dictionary to map abbreviations to full team names
map = {
    'Michael Penix': 'Michael Penix Jr.',
    'Marvin Mims': 'Marvin Mims Jr.',
}

# # Replace team names using the dictionary
# file1['team'] = file1['team'].replace(map)
# file2['team'] = file2['team'].replace(map)
# file3['team'] = file3['team'].replace(map)

# Replace team names using the dictionary
file1['player'] = file1['player'].replace(map)
file2['player'] = file2['player'].replace(map)
file3['player'] = file3['player'].replace(map)

# Save the updated DataFrame to a new CSV file
file1.to_csv('nfl_player_data_2022.csv', index=False)
file2.to_csv('nfl_player_data_2023.csv', index=False)
file3.to_csv('nfl_player_data_2024.csv', index=False)

print("Team names updated and saved successfully!")