import pandas as pd
import torch
from tqdm import tqdm
from unified_model import load_model_artifacts, predict_all, ALL_TARGETS, HighAccuracyClassifier
import os
import pickle
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def run_testing():
    print("Starting model testing...")
    
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    try:
        print("Attempting to load model artifacts...")
        model_path = 'E:/ML/Grivances/saved_model'
        models, tokenizer, label_encoders = load_model_artifacts(model_path)
        models = [model.to(device) for model in models]
        
        # Update ALL_TARGETS to match available targets
        global ALL_TARGETS
        ALL_TARGETS = list(label_encoders.keys())
        print(f"\nUsing targets: {ALL_TARGETS}")
        
    except Exception as e:
        print(f"\nError loading model: {str(e)}")
        print("\nDebug information:")
        print(f"Model path exists: {os.path.exists(model_path)}")
        return
    
    # Load test data
    try:
        test_df = pd.read_csv('E:/ML/Grivances/test.csv')
        print(f"Loaded {len(test_df)} test samples")
    except Exception as e:
        print(f"Error loading test data: {e}")
        return
    
    # Prepare input texts
    test_df['input_text'] = test_df.apply(
        lambda row: ' '.join([
            str(row[col]) for col in ['Complaint', 'Title'] 
            if col in row and pd.notna(row[col])
        ]), 
        axis=1
    )
    
    # Make predictions
    all_predictions = []
    print("\nRunning predictions...")
    
    for idx, row in tqdm(test_df.iterrows(), total=len(test_df)):
        try:
            predictions = predict_all(row['input_text'], models, tokenizer, label_encoders)
            all_predictions.append(predictions)
        except Exception as e:
            print(f"Error predicting row {idx}: {e}")
            all_predictions.append({target: 'unknown' for target in label_encoders.keys()})
    
    # Ensure we have predictions before continuing
    if not all_predictions:
        print("No predictions were made!")
        return
        
    # Add predictions to dataframe
    available_targets = list(label_encoders.keys())
    for target in available_targets:
        test_df[f'Predicted_{target}'] = [pred.get(target, 'unknown') for pred in all_predictions]
    
    # Calculate detailed metrics for each target
    print("\nDetailed Evaluation Metrics:")
    print("=" * 50)
    
    overall_accuracy = 0
    total_targets = 0
    
    for target in available_targets:
        if target in test_df.columns:
            true_values = test_df[target].fillna('unknown')
            pred_values = test_df[f'Predicted_{target}'].fillna('unknown')
            
            try:
                # Calculate accuracy
                accuracy = accuracy_score(true_values, pred_values)
                overall_accuracy += accuracy
                total_targets += 1
                
                print(f"\nMetrics for {target}:")
                print("-" * 30)
                print(f"Accuracy: {accuracy:.4f}")
                
                # Print detailed classification report
                print("\nClassification Report:")
                print(classification_report(true_values, pred_values))
                
                # Save confusion matrix to CSV
                cm = confusion_matrix(true_values, pred_values)
                labels = sorted(set(true_values) | set(pred_values))
                cm_df = pd.DataFrame(
                    cm,
                    index=[f'True_{x}' for x in labels],
                    columns=[f'Pred_{x}' for x in labels]
                )
                cm_df.to_csv(f'E:/ML/Grivances/confusion_matrix_{target}.csv')
            except Exception as e:
                print(f"Error calculating metrics for {target}: {e}")
    
    # Print overall accuracy only if we have valid metrics
    if total_targets > 0:
        print("\nOverall Results:")
        print("=" * 50)
        print(f"Average Accuracy across all targets: {overall_accuracy/total_targets:.4f}")
    
    # Save results
    output_path = 'E:/ML/Grivances/test_results.csv'
    test_df.to_csv(output_path, index=False)
    print(f"\nResults saved to: {output_path}")

if __name__ == "__main__":
    # Set cache directories
    os.environ['TRANSFORMERS_CACHE'] = 'E:/ML/Grivances/cache'
    os.environ['HF_HOME'] = 'E:/ML/Grivances/cache'
    os.environ['TORCH_HOME'] = 'E:/ML/Grivances/torch'
    
    run_testing()
