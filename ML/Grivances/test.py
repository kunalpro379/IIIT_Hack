import torch
from torch.utils.data import Dataset
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    Trainer,
    TrainingArguments
)
import pandas as pd
import numpy as np
import pickle

class GrievanceDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        # Tokenize the text
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

def prepare_data(file_path):
    # Load data
    df = pd.read_csv(file_path)
    
    # Extract categories and encode them
    categories = df['category'].unique()
    category_to_id = {cat: idx for idx, cat in enumerate(categories)}
    
    # Create features and labels
    texts = df['description'].tolist()
    labels = [category_to_id[cat] for cat in df['category']]
    
    return texts, labels, categories

def main():
    print("Loading data and preparing model...")
    
    # Load and prepare data
    texts, labels, categories = prepare_data('generated_grievances.csv')
    
    # Split into train/val
    indices = np.random.permutation(len(texts))
    split_point = int(len(indices) * 0.8)
    train_indices = indices[:split_point]
    val_indices = indices[split_point:]
    
    # Initialize tokenizer and model
    tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
    model = BertForSequenceClassification.from_pretrained(
        'bert-base-multilingual-cased',
        num_labels=len(categories)
    )
    
    # Create datasets
    train_dataset = GrievanceDataset(
        [texts[i] for i in train_indices],
        [labels[i] for i in train_indices],
        tokenizer
    )
    val_dataset = GrievanceDataset(
        [texts[i] for i in val_indices],
        [labels[i] for i in val_indices],
        tokenizer
    )
    
    # Define training arguments
    training_args = TrainingArguments(
        output_dir="./grievance_classifier",
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
        push_to_hub=False,
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
    )
    
    print("Starting training...")
    trainer.train()
    
    # Save model and categories using pickle
    print("Saving model and categories...")
    model_data = {
        "categories": categories,
        "category_to_id": {cat: idx for idx, cat in enumerate(categories)}
    }
    
    with open("model_data.pkl", "wb") as f:
        pickle.dump(model_data, f)
    
    # Save model
    trainer.save_model("./grievance_classifier_final")
    
    # Test prediction
    test_text = "सड़क में बहुत गड्ढे हैं need urgent repair"
    inputs = tokenizer(test_text, return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs)
    predicted_category = categories[outputs.logits.argmax().item()]
    print(f"\nTest prediction:")
    print(f"Text: {test_text}")
    print(f"Predicted category: {predicted_category}")

if __name__ == "__main__":
    main()
