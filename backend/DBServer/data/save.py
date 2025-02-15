import pandas as pd

# Load CSV file
file_path = "combined_data.csv"  # Replace with your actual file path
df = pd.read_csv(file_path)

# Extract unique departments
unique_departments = df["departmentAssigned"].dropna().unique()

# Save to a new CSV file
output_file = "unique_departments.csv"
pd.DataFrame(unique_departments, columns=["Department"]).to_csv(output_file, index=False)

print(f"Unique departments saved to {output_file}")
