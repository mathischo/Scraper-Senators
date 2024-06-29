import os
import requests
import json
import yaml
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
    # First parameter is the replacement, second parameter is your input string
    first_name = regex.sub('', first_name.split()[0].lower())
    last_name = regex.sub('', last_name.split()[0].lower())

    for member in existing_members:
        if 'official_full' not in member['name'].keys():
            member['name']['official_full'] = f"{member['name']['first']} {member['name']['last']}"

        if first_name in member['name']['official_full'].lower() and last_name in member['name']['official_full'].lower():
            return member['id']['bioguide']

    for member in prev_members:
        if first_name in member['name']['first'].lower() and last_name in member['name']['last'].lower():
            return member['id']['bioguide']

    # Some members have nickname first names like William Cassidy.
    # when that is that case just hope to match a last name...
    for member in existing_members:
        if last_name == member['name']['last'].lower() or last_name in member['name']['official_full'].lower():
            return member['id']['bioguide']

    for member in prev_members:
        if last_name in member['name']['last'].lower():
            return member['id']['bioguide']

    return None

def add_details_to_csv(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path, delimiter='\t')
    
    # Add a new column for the bioguide ID
    df['bioguide'] = df.apply(lambda row: bioid(row['First Name'], row['Last Name']), axis=1)
    
    # Check for any missing bioguide IDs
    if df['bioguide'].isnull().any():
        missing_ids = df[df['bioguide'].isnull()]
        print('FAILED TO FIND ID FOR THE FOLLOWING SENATORS')
        print(missing_ids[['First Name', 'Last Name']])
    
    # Save the updated DataFrame back to CSV
    df.to_csv(file_path, index=False, sep='\t')

def files_to_yaml():
    files = []
    data_path = '/Users/mathisschomacher/Documents/Thesis/Politicians Scraper/senator-filings-master/notebooks/data'
    aggregate_path = '/Users/mathisschomacher/Documents/Thesis/Politicians Scraper/senator-filings-master/notebooks/aggregate'
    
    for filename in os.listdir(data_path):
        if filename.endswith(".json"):
            files.append(os.path.join(data_path, filename))
    for filename in os.listdir(aggregate_path):
        if filename.endswith(".json"):
            files.append(os.path.join(aggregate_path, filename))

    for file in files:
        with open(file, "r") as read_file:
            file_data = json.load(read_file)

            with open(f"{file}.yaml", 'w') as write_file:
                write_file.write(yaml.dump(file_data))

# Update the CSV file with bioguide IDs
csv_file_path = '/Users/mathisschomacher/Documents/Thesis/Politicians Scraper/senator-filings-master/notebooks/your_file.csv'
add_details_to_csv(csv_file_path)

# Convert existing JSON files to YAML
files_to_yaml()