import os
import requests
import re
import pandas as pd

# Get JSON of existing members
existing_member_req = requests.get('https://theunitedstates.io/congress-legislators/legislators-current.json')
existing_members = existing_member_req.json()

# Get JSON of previous members
prev_member_req = requests.get('https://theunitedstates.io/congress-legislators/legislators-historical.json')
prev_members = prev_member_req.json()

def bioid(first_name, last_name):
    regex = re.compile('[^a-zA-Z]')
    first_name = regex.sub('', first_name.split()[0].lower())
    last_name = regex.sub('', last_name.split()[0].lower())

    for member in existing_members + prev_members:
        if 'official_full' in member['name']:
            official_full = member['name']['official_full'].lower()
        else:
            official_full = f"{member['name']['first']} {member['name']['last']}".lower()

        if first_name in official_full and last_name in official_full:
            return member['id']['bioguide']

        if last_name == member['name']['last'].lower():
            return member['id']['bioguide']

    return None

def add_details_to_csv(file_path):
    try:
        # Read the CSV file, guessing the delimiter automatically, and handling bad lines by skipping them
        df = pd.read_csv(file_path, delimiter=None, engine='python', on_bad_lines='skip')

        # Print column names to verify
        print("Columns in CSV file:", df.columns)

        # Add a new column for the bioguide ID
        df['bioguide'] = df.apply(lambda row: bioid(row['First Name'], row['Last Name']), axis=1)
        
        # Check for any missing bioguide IDs
        if df['bioguide'].isnull().any():
            missing_ids = df[df['bioguide'].isnull()]
            print('FAILED TO FIND ID FOR THE FOLLOWING SENATORS')
            print(missing_ids[['First Name', 'Last Name']])
        
        # Save the updated DataFrame back to CSV
        df.to_csv(file_path, index=False)
    except Exception as e:
        print(f"An error occurred: {e}")

# Update the CSV file with bioguide IDs
csv_file_path = '/Users/mathisschomacher/Documents/Thesis/Scraper Senators/notebooks/senators_new.csv'
add_details_to_csv(csv_file_path)