import pandas as pd

test_data = pd.read_csv('test.csv')
print("Available columns:", test_data.columns.tolist())
