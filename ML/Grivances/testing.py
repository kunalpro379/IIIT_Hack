import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
import pickle
from tqdm import tqdm

def setup_device():
    """Set up the device for testing"""
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"Using device: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        print("Using device: CPU")
    return device

def load_model_and_tokenizer(model_dir):
    """Load the saved model, tokenizer, and label encoders"""
    try:
        print(f"Loading model from: {model_dir}")
        
        if not os.path.exists(model_dir):
            raise FileNotFoundError(f"Model directory not found at {model_dir}")

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained('bert-base-multilingual-cased')
        
        # Load model
        model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        
        # Load label encoders
        le_path = os.path.join(model_dir, 'label_encoders.pkl')
        with open(le_path, 'rb') as f:
            label_encoders = pickle.load(f)
            
        return model, tokenizer, label_encoders
    
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        raise

def predict_batch(texts, model, tokenizer, label_encoders, device):
    """Make predictions for a batch of texts"""
    model.eval()
    model = model.to(device)
    
    # Tokenize the texts
    inputs = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=256,
        return_tensors="pt"
    )
    
    # Move inputs to device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Get predictions
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Get predicted labels
    predictions = torch.argmax(outputs.logits, dim=1)
    
    # Convert to category names
    predicted_categories = label_encoders['category'].inverse_transform(predictions.cpu().numpy())
    
    return predicted_categories

def main():
    # Setup
    device = setup_device()
    model_dir = 'E:/ML/Grivances/saved_model'  # Updated model directory
    
    # Load test data
    test_df = pd.read_csv('test.csv')
    print(f"Loaded {len(test_df)} test samples")
    
    try:
        # Load model, tokenizer, and label encoders
        model, tokenizer, label_encoders = load_model_and_tokenizer(model_dir)
        
        # Prepare input texts (combine relevant columns)
        texts = test_df['Complaint'].fillna('').tolist()
        
        # Process in batches
        batch_size = 8
        all_predictions = []
        
        for i in tqdm(range(0, len(texts), batch_size)):
            batch_texts = texts[i:i + batch_size]
            predictions = predict_batch(batch_texts, model, tokenizer, label_encoders, device)
            all_predictions.extend(predictions)
        
        # Add predictions to dataframe
        test_df['Predicted_Category'] = all_predictions
        
        # Save results
        output_path = 'predictions_output.csv'
        test_df.to_csv(output_path, index=False)
        print(f"\nPredictions saved to {output_path}")
        
        # Print sample predictions
        print("\nSample predictions:")
        print(test_df[['Complaint', 'Category', 'Predicted_Category']].head())
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    main()
