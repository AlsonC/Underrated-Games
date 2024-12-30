import pandas as pd
import json

# Load the JSON data from the file
with open('Upcoming.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Extract the relevant fields and create a DataFrame
df = pd.DataFrame(data, columns=['title', 'steam_wishlists', 'steam_followers', 'developer', 'publisher']).sort_values(by='steam_followers', ascending=False)

# Print the first 10 rows of the DataFrame
print(df.head(10))
df.to_excel('UpcomingGames.xlsx', index=False, engine='openpyxl')

