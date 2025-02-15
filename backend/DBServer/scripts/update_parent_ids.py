import pandas as pd
import os

def update_parent_ids():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    merged_path = os.path.join(base_dir, 'data', 'seeds', 'Authority_Merged.csv')
    hierarchy_path = os.path.join(base_dir, 'data', 'seeds', 'Authority_Hierarchy.csv')
    output_path = os.path.join(base_dir, 'data', 'seeds', 'Authority_Updated.csv')

    try:
        # Read the files
        df = pd.read_csv(merged_path)
        hierarchy = pd.read_csv(hierarchy_path)

        # Create a role to parent role mapping
        role_parent_map = dict(zip(hierarchy['role'], hierarchy['parentRole']))

        # Function to find parent ID
        def find_parent_id(row):
            parent_role = role_parent_map.get(row['role'])
            if pd.isna(parent_role):
                return ''
            
            # Find potential parents in the same jurisdiction/region
            potential_parents = df[
                (df['role'] == parent_role) & 
                (
                    (df['jurisdiction'].str.contains(row['assignedRegion'], na=False)) |
                    (df['assignedRegion'] == row['assignedRegion'])
                )
            ]

            if len(potential_parents) > 0:
                return potential_parents.iloc[0]['id']
            return ''

        # Add IDs if they don't exist
        if 'id' not in df.columns:
            df['id'] = [f'auth_{i:03d}' for i in range(1, len(df) + 1)]

        # Update parentIds based on hierarchy
        df['parentId'] = df.apply(find_parent_id, axis=1)

        # Save updated file
        df.to_csv(output_path, index=False)
        print(f"Successfully updated parent IDs. Output saved to: {output_path}")

    except Exception as e:
        print(f"Error occurred while updating parent IDs: {str(e)}")
        raise

if __name__ == "__main__":
    update_parent_ids()
