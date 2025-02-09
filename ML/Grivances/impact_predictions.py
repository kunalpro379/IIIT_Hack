import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import torch
from torch.utils.data import Dataset
import os
import pickle
from sklearn.preprocessing import LabelEncoder
import argparse

# Available prediction targets
PREDICTION_TARGETS = [
    'economicImpact',
    'environmentalImpact',
    'socialImpact',
    'relatedPolicies',
    'subcategory',
    'departmentAssigned'
]

class ImpactDataset(Dataset):
    def __init__(self, dataframe, tokenizer, max_len, target_column):
        self.tokenizer = tokenizer
        self.data = dataframe
        self.max_len = max_len
        self.target_column = target_column

        # Setup label encoder for the target column
        self.label_encoder = LabelEncoder()
        self.data[target_column] = self.data[target_column].fillna('unknown')
        self.data[target_column] = self.data[target_column].astype(str)
        self.data[f'{target_column}_encoded'] = self.label_encoder.fit_transform(self.data[target_column])
        self.num_labels = len(self.label_encoder.classes_)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        text = str(self.data.iloc[index]['input_text'])
        label = self.data.iloc[index][f'{self.target_column}_encoded']

        inputs = self.tokenizer.encode_plus(
            text,
            None,
            add_special_tokens=True,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        return {
            'input_ids': inputs['input_ids'].squeeze(),
            'attention_mask': inputs['attention_mask'].squeeze(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

def train_impact_model(target_column):
    # Setup
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load and prepare data
    df = pd.read_csv('gen_datasets/combined_data.csv')
    text_columns = ['complaint', 'title', 'description']
    df['input_text'] = df.apply(lambda row: ' '.join([str(row[col]) for col in text_columns if col in df.columns]), axis=1)
    
    # Split data
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    
    # Initialize tokenizer
    tokenizer = AutoTokenizer.from_pretrained('bert-base-multilingual-cased')
    
    # Create datasets
    train_dataset = ImpactDataset(train_df, tokenizer, max_len=256, target_column=target_column)
    test_dataset = ImpactDataset(test_df, tokenizer, max_len=256, target_column=target_column)
    
    # Initialize model
    model = AutoModelForSequenceClassification.from_pretrained(
        'bert-base-multilingual-cased',
        num_labels=train_dataset.num_labels
    ).to(device)
    
    # Setup training arguments
    model_dir = f'E:/ML/Grivances/impact_models/{target_column}'
    os.makedirs(model_dir, exist_ok=True)
    
    training_args = TrainingArguments(
        output_dir=model_dir,
        num_train_epochs=3,
        per_device_train_batch_size=8,
        evaluation_strategy="epoch",
        save_strategy="no",
        load_best_model_at_end=False,
        logging_steps=50
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset
    )
    
    # Train and save
    print(f"Training model for {target_column}...")
    trainer.train()
    
    # Save model and label encoder
    trainer.save_model(model_dir)
    with open(os.path.join(model_dir, 'label_encoder.pkl'), 'wb') as f:
        pickle.dump(train_dataset.label_encoder, f)
    
    print(f"Model saved to {model_dir}")
    return model_dir

def predict_impact(text, target_column, model_dir):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Load model and tokenizer
    model = AutoModelForSequenceClassification.from_pretrained(model_dir).to(device)
    tokenizer = AutoTokenizer.from_pretrained('bert-base-multilingual-cased')
    
    # Load label encoder
    with open(os.path.join(model_dir, 'label_encoder.pkl'), 'rb') as f:
        label_encoder = pickle.load(f)
    
    # Prepare input
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=256)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Get prediction
    model.eval()
    with torch.no_grad():
        outputs = model(**inputs)
        prediction = outputs.logits.argmax(dim=1)
    
    # Convert to label
    predicted_label = label_encoder.inverse_transform([prediction.item()])[0]
    return predicted_label

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', choices=PREDICTION_TARGETS, help='Target column to train model for')
    parser.add_argument('--predict', action='store_true', help='Make predictions using trained model')
    parser.add_argument('--text', type=str, help='Text to predict for')
    args = parser.parse_args()
    
    if args.train:
        model_dir = train_impact_model(args.train)
        print(f"Training completed for {args.train}")
    
    if args.predict:
        if not args.text:
            print("Please provide text to predict using --text")
            return
            
        for target in PREDICTION_TARGETS:
            model_dir = f'E:/ML/Grivances/impact_models/{target}'
            if os.path.exists(model_dir):
                prediction = predict_impact(args.text, target, model_dir)
                print(f"{target}: {prediction}")

if __name__ == "__main__":
    main()
