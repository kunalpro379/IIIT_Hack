import pandas as pd
import os

def extract_parent_role():
    # Define file paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(base_dir, 'data', 'seeds', 'Authority_Merged.csv')
    output_path = os.path.join(base_dir, 'data', 'seeds', 'Authority_Parent_Role.csv')

    try:
        # Read the merged CSV file
        df = pd.read_csv(input_path)
        
        # Select only parentId and role columns
        parent_role_df = df[['parentId', 'role']].copy()
        
        # Remove rows where both parentId and role are empty
        parent_role_df = parent_role_df.dropna(how='all')
        
        # Remove duplicate combinations
        parent_role_df = parent_role_df.drop_duplicates()
        
        # Sort by role for better readability
        parent_role_df = parent_role_df.sort_values('role')
        
        # Save to new CSV file
        parent_role_df.to_csv(output_path, index=False)
        
        print(f"Successfully extracted parent-role relationships to: {output_path}")
        print(f"Total relationships extracted: {len(parent_role_df)}")
        print("\nUnique roles found:")
        for role in sorted(parent_role_df['role'].unique()):
            print(f"- {role}")

    except Exception as e:
        print(f"Error occurred while extracting parent-role relationships: {str(e)}")
        raise

if __name__ == "__main__":
    extract_parent_role()
