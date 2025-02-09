import json
import csv
import glob
import random
from datetime import datetime
import pandas as pd

# Load the dataset
df = pd.read_csv('IN.csv')

# Print the column names to verify
print(df.columns)

# Filter for entries where the state is Uttar Pradesh
up_df = df[df['admin_name1'].str.strip().str.lower() == 'uttar pradesh']

# Create a list of dictionaries with relevant data
up_data = up_df.to_dict(orient='records')

def fetch_real_world_data(unique_id):
    # Randomly select an entry from the UP data
    selected_entry = random.choice(up_data)
    return {
        "status": random.choice(["Open", "Closed", "In Progress"]),
        "submissionDate": datetime.now().strftime("%Y-%m-%d"),
        "lastUpdatedDate": datetime.now().strftime("%Y-%m-%d"),
        "district": selected_entry.get('place_name', 'N/A'),
        "tehsil": 'N/A',  # 'tehsil' information is not available in the dataset
        "ward": 'N/A',  # 'ward' information is not available in the dataset
        "pincode": selected_entry.get('key', 'N/A').split('/')[1],
        "gpscoordinates_latitude": selected_entry.get('latitude', 'N/A'),
        "gpscoordinates_longitude": selected_entry.get('longitude', 'N/A'),
        "id": unique_id,
        "title": f"Sample Title {unique_id}",
        "contactNumber": f"{random.randint(6000000000, 9999999999)}",
        "email": f"example{unique_id}@gmail.com",
        "isAnonymous": random.choice([True, False]),
        "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "CreatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "estimated": random.randint(1, 100),
        "ResolutionTime": random.randint(1, 30)
    }

# Read all JSON files and combine the data
combined_data = []
unique_id = 1000
for file in glob.glob("dummy*.json"):
    with open(file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            if isinstance(data, dict) and "complaints" in data:
                data = data["complaints"]
            if isinstance(data, list):
                for entry in data:
                    entry.update(fetch_real_world_data(unique_id))
                    combined_data.append(entry)
                    unique_id += 1
            else:
                print(f"Skipping file {file} as it does not contain a list of entries")
        except json.JSONDecodeError as e:
            print(f"Skipping file {file} due to JSON decode error: {e}")
        except Exception as e:
            print(f"Skipping file {file} due to unexpected error: {e}")

# Ensure all dictionaries have the same keys
fieldnames = set()
for entry in combined_data:
    fieldnames.update(entry.keys())

# Write the combined data to a CSV file
if combined_data:
    with open("combined_data.csv", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(combined_data)

print("Data combined and saved to combined_data.csv")
