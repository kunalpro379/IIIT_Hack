import json
import csv
import pandas as pd
from flatten_json import flatten

def convert_json_to_csv():
    with open('data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    flattened_data = [flatten(d) for d in data]
    
    df = pd.DataFrame(flattened_data)
    
    df.to_csv('grievances.csv', index=False, encoding='utf-8')
    print("CSV file has been created successfully!")

if __name__ == "__main__":
    convert_json_to_csv()
