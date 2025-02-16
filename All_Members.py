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

# Extract member details
def extract_member_details(members):
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
            # Calculate age only if birthday is known
            if birthday != 'Unknown':
                birth_date = datetime.strptime(birthday, "%Y-%m-%d")
                details['age'] = (datetime.now() - birth_date).days // 365
            else:
                details['age'] = 'Unknown'
            member_data.append(details)
    return member_data

# Main execution
existing_members, prev_members = fetch_members()  # Fetch members
all_members = existing_members + prev_members  # Combine lists

# Extract details for all members
all_member_data = extract_member_details(all_members)

# Create DataFrame from the extracted data
members_df = pd.DataFrame(all_member_data)

# Specify the path to save the CSV file
csv_file_path = '/Users/mathisschomacher/Documents/Thesis/Scraper Senators/notebooks/all_members_data.csv'

# Save the DataFrame to CSV
members_df.to_csv(csv_file_path, index=False)

print("CSV file has been saved successfully.")