import requests
import pandas as pd
from datetime import datetime

# Fetch JSON data for existing and previous members of Congress
def fetch_members():
    existing_member_url = 'https://theunitedstates.io/congress-legislators/legislators-current.json'
    prev_member_url = 'https://theunitedstates.io/congress-legislators/legislators-historical.json'
    
    existing_member_req = requests.get(existing_member_url)
    prev_member_req = requests.get(prev_member_url)
    
    existing_members = existing_member_req.json()
    prev_members = prev_member_req.json()
    
    return existing_members, prev_members

# Get member details using bioguide ID
def get_member_details(members):
    member_data = []
    for member in members:
        for term in member['terms']:
            # Use .get() to provide default values for missing keys
            birthday = member['bio'].get('birthday', 'Unknown')
            party = term.get('party', 'None')
            
            details = {
                'bioguide_id': member['id']['bioguide'],
                'full_name': member['name'].get('official_full', member['name']['first'] + ' ' + member['name']['last']),
                'first_name': member['name']['first'],
                'last_name': member['name']['last'],
                'birthday': birthday,
                'gender': member['bio']['gender'],
                'party': party,
                'state': term['state'],
                'term_start': term['start'],
                'term_end': term['end'],
                'type': term['type'],  # e.g., rep or sen
            }

# Add senator details to DataFrame
def add_senator_details(df, members):
    detail_columns = ['full_name', 'first_name', 'last_name', 'birthday', 'gender', 'party', 'state', 'term_start', 'term_end','type', 'age']
    for column in detail_columns:
        df[column] = None
    
    for index, row in df.iterrows():
        bioguide = row['bioguide']
        details = get_member_details(bioguide, members)
        for key, value in details.items():
            df.at[index, key] = value

    return df

# Main execution
existing_members, prev_members = fetch_members()  # Fetch members
all_members = existing_members + prev_members  # Combine lists

# Specify the path to your transactions CSV file
csv_file_path = '/Users/mathisschomacher/Documents/Thesis/Scraper Senators/notebooks/senators_new.csv'

# Read your transactions CSV file into a DataFrame using comma as the delimiter
transactions_df = pd.read_csv(csv_file_path, delimiter=',')

# Print the column names to verify
print("Columns in the DataFrame:", transactions_df.columns)

# Check if 'bioguide' column exists
if 'bioguide' not in transactions_df.columns:
    raise ValueError("The 'bioguide' column is missing from the CSV file. Please check the file and try again.")

# Add senator details to the DataFrame
transactions_df = add_senator_details(transactions_df, all_members)

# Save the updated DataFrame back to CSV
transactions_df.to_csv(csv_file_path, index=False)