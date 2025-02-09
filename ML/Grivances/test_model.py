import pandas as pd
import torch
import os
import numpy as np
from tqdm import tqdm
from sklearn.metrics import classification_report, accuracy_score, f1_score
from unified_model import load_model_artifacts, ALL_TARGETS, EnhancedDataset

def test_saved_model(test_csv_path='E:/ML/Grivances/test.csv', batch_size=8):
    # Set up device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load saved model artifacts
    print("Loading model artifacts...")
    models, tokenizer, label_encoders = load_model_artifacts()
    
    # Move models to device
    models = [model.to(device) for model in models]
    
    # Load and prepare test data
    print("Loading test data...")
    test_df = pd.read_csv(test_csv_path)
    
    # Combine text columns for input
    text_columns = ['Complaint', 'Title']
    test_df['input_text'] = test_df.apply(
        lambda row: ' '.join([str(row[col]) for col in text_columns if col in test_df.columns and pd.notna(row[col])]), 
        axis=1
    )
    
    # Create test dataset
    test_dataset = EnhancedDataset(test_df, tokenizer, max_len=256, augment=False)
    
    # Prepare DataLoader
    from torch.utils.data import DataLoader
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0
    )
    
    # Initialize metrics storage
    all_predictions = {target: [] for target in ALL_TARGETS}
    all_labels = {target: [] for target in ALL_TARGETS}
    
    # Evaluation loop
    print("Starting evaluation...")
    for model in models:
        model.eval()
    
    with torch.no_grad():
        for batch in tqdm(test_loader, desc="Testing"):
            # Move batch to device
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            # Get ensemble predictions
            batch_predictions = []
            for model in models:
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                batch_predictions.append([logits.argmax(dim=-1) for logits in outputs['logits']])
            
            # Average ensemble predictions
            averaged_preds = torch.stack([torch.stack(model_preds) for model_preds in batch_predictions]).mean(0)
            final_preds = averaged_preds.argmax(dim=-1)
            
            # Store predictions and labels
            for i, target in enumerate(ALL_TARGETS):
                all_predictions[target].extend(final_preds[i].cpu().numpy())
                all_labels[target].extend(labels[:, i].cpu().numpy())
    
    # Calculate and print metrics
    print("\nEvaluation Results:")
    print("=" * 50)
    
    overall_accuracy = 0
    overall_f1 = 0
    
    for target in ALL_TARGETS:
        print(f"\nMetrics for {target}:")
        print("-" * 30)
        
        # Convert numeric predictions back to labels
        pred_labels = label_encoders[target].inverse_transform(all_predictions[target])
        true_labels = label_encoders[target].inverse_transform(all_labels[target])
        
        # Calculate metrics
        accuracy = accuracy_score(true_labels, pred_labels)
        f1 = f1_score(true_labels, pred_labels, average='weighted')
        
        overall_accuracy += accuracy
        overall_f1 += f1
        
        print(f"Accuracy: {accuracy:.4f}")
        print(f"F1 Score: {f1:.4f}")
        print("\nClassification Report:")
        print(classification_report(true_labels, pred_labels))
        
        # Save predictions to CSV
        results_df = pd.DataFrame({
            'True_Label': true_labels,
            'Predicted_Label': pred_labels
        })
        results_df.to_csv(f'E:/ML/Grivances/results_{target}.csv', index=False)
    
    # Print overall metrics
    print("\nOverall Metrics:")
    print("=" * 50)
    print(f"Average Accuracy: {overall_accuracy / len(ALL_TARGETS):.4f}")
    print(f"Average F1 Score: {overall_f1 / len(ALL_TARGETS):.4f}")

if __name__ == "__main__":
    # Set cache directories to E drive
    os.environ['TRANSFORMERS_CACHE'] = 'E:/ML/Grivances/cache'
    os.environ['HF_HOME'] = 'E:/ML/Grivances/cache'
    os.environ['TORCH_HOME'] = 'E:/ML/Grivances/torch'
    
    test_saved_model()
