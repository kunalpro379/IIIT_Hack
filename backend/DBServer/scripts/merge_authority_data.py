import pandas as pd
import os

def merge_authority_files():
    # Define file paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    authority_path = os.path.join(base_dir, 'data', 'seeds', 'Authority.csv')
    authority_data_path = os.path.join(base_dir, 'data', 'Authority_Data.csv')
    output_path = os.path.join(base_dir, 'data', 'seeds', 'Authority_Merged.csv')

    try:
        # Read the CSV files
        authority_df = pd.read_csv(authority_path)
        authority_data_df = pd.read_csv(authority_data_path)

        # Remove departmentId from Authority_Data.csv
        if 'departmentId' in authority_data_df.columns:
            authority_data_df['departmentId'] = ''

        # Convert columns to consistent types
        columns_to_string = ['contactNumber', 'wardNumber', 'blockJurisdiction', 
                           'panchayatArea', 'specialization', 'fieldArea']
        
        for col in columns_to_string:
            if col in authority_df.columns:
                authority_df[col] = authority_df[col].fillna('').astype(str)
            if col in authority_data_df.columns:
                authority_data_df[col] = authority_data_df[col].fillna('').astype(str)

        # Clean up the data
        for df in [authority_df, authority_data_df]:
            df.replace({'null': '', 'nan': '', 'None': ''}, inplace=True)
            df = df.replace(r'^\s*$', '', regex=True)

        # Use concat instead of merge
        combined_df = pd.concat([authority_df, authority_data_df], ignore_index=True)
        
        # Ensure departmentId is empty in final output
        if 'departmentId' in combined_df.columns:
            combined_df['departmentId'] = ''
        
        # Remove duplicate rows based on all columns
        merged_df = combined_df.drop_duplicates(subset=[
            'name', 'email', 'role', 'level', 'assignedRegion', 
            'jurisdiction', 'designation', 'contactNumber', 
            'officeAddress', 'isActive'
        ], keep='first')

        # Add timestamps if they don't exist
        current_time = pd.Timestamp.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        if 'createdAt' not in merged_df.columns:
            merged_df['createdAt'] = current_time
        if 'updatedAt' not in merged_df.columns:
            merged_df['updatedAt'] = current_time

        # Sort columns alphabetically for better readability
        merged_df = merged_df.reindex(sorted(merged_df.columns), axis=1)

        # Save the merged data
        merged_df.to_csv(output_path, index=False, na_rep='')
        print(f"Successfully merged files. Output saved to: {output_path}")
        print(f"Total records in merged file: {len(merged_df)}")
        print(f"Columns in merged file: {', '.join(merged_df.columns)}")

    except Exception as e:
        print(f"Error occurred while merging files: {str(e)}")
        raise

if __name__ == "__main__":
    merge_authority_files()
