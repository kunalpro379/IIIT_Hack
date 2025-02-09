import pandas as pd

def save_predictions():
    # Load the full results
    try:
        df = pd.read_csv('E:/ML/Grivances/test_results.csv')
        print(f"Loaded {len(df)} results")
        
        # Extract description (Complaint) and predicted columns
        columns_to_keep = ['Complaint']
        predicted_columns = [col for col in df.columns if col.startswith('Predicted_')]
        columns_to_keep.extend(predicted_columns)
        
        # Create new dataframe with only required columns
        prediction_df = df[columns_to_keep]
        
        # Save to new file
        output_path = 'E:/ML/Grivances/predictions_only.csv'
        prediction_df.to_csv(output_path, index=False)
        print(f"\nSaved predictions to: {output_path}")
        
        # Display sample
        print("\nSample of saved predictions:")
        print(prediction_df.head())
        
    except Exception as e:
        print(f"Error saving predictions: {e}")

if __name__ == "__main__":
    save_predictions()
