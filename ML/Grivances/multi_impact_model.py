import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, BertPreTrainedModel, BertModel, Trainer, TrainingArguments
import torch
import torch.nn as nn
from torch.utils.data import Dataset
import os
import pickle
from sklearn.preprocessing import LabelEncoder

# Define all targets to predict
PREDICTION_TARGETS = [
    'economicImpact',
    'environmentalImpact', 
    'socialImpact',
    'relatedPolicies',
    'subcategory',
    'departmentAssigned'
]

class CustomBertForMultiTaskClassification(BertPreTrainedModel):
    def __init__(self, config, num_labels_per_task):
        super().__init__(config)
        self.bert = BertModel(config)
        self.classifiers = nn.ModuleList([
            nn.Linear(config.hidden_size, num_labels) 
            for num_labels in num_labels_per_task
        ])
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.init_weights()

    def forward(self, input_ids, attention_mask=None, labels=None):
        outputs = self.bert(input_ids, attention_mask=attention_mask)
        pooled_output = outputs[1]
        pooled_output = self.dropout(pooled_output)

        logits = [classifier(pooled_output) for classifier in self.classifiers]
        
        loss = None
        if labels is not None:
            loss_fct = nn.CrossEntropyLoss()
            loss = sum(loss_fct(logit, labels[:, i]) for i, logit in enumerate(logits))

        return {'loss': loss, 'logits': logits} if loss is not None else {'logits': logits}

class MultiTargetDataset(Dataset):
    def __init__(self, dataframe, tokenizer, max_len):
        self.tokenizer = tokenizer
        self.data = dataframe
        self.max_len = max_len
        
        # Create label encoders for all target columns
        self.label_encoders = {}
        for target in PREDICTION_TARGETS:
            self.data[target] = self.data[target].fillna('unknown')
            self.data[target] = self.data[target].astype(str)
            le = LabelEncoder()
            self.data[f'{target}_encoded'] = le.fit_transform(self.data[target])
            self.label_encoders[target] = le

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        text = str(self.data.iloc[index]['input_text'])
        labels = [self.data.iloc[index][f'{target}_encoded'] for target in PREDICTION_TARGETS]
        
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
            'labels': torch.tensor(labels, dtype=torch.long)
        }

def train_model():
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
    train_dataset = MultiTargetDataset(train_df, tokenizer, max_len=256)
    test_dataset = MultiTargetDataset(test_df, tokenizer, max_len=256)
    
    # Get number of labels for each target
    num_labels_per_task = [
        len(train_dataset.label_encoders[target].classes_)
        for target in PREDICTION_TARGETS
    ]

    # Initialize custom model
    model = CustomBertForMultiTaskClassification.from_pretrained(
        'bert-base-multilingual-cased',
        num_labels_per_task=num_labels_per_task
    ).to(device)
    
    # Setup training arguments
    model_dir = 'E:/ML/Grivances/saved_model'
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
    print("Training model...")
    trainer.train()
    
    # Save model and label encoders
    trainer.save_model(model_dir)
    with open(os.path.join(model_dir, 'label_encoders.pkl'), 'wb') as f:
        pickle.dump(train_dataset.label_encoders, f)
    
    print(f"Model and label encoders saved to {model_dir}")
    return model_dir

def predict_all_impacts(text):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_dir = 'E:/ML/Grivances/saved_model'
    
    # Load label encoders first
    with open(os.path.join(model_dir, 'label_encoders.pkl'), 'rb') as f:
        label_encoders = pickle.load(f)
    
    # Now initialize model with correct number of labels
    model = CustomBertForMultiTaskClassification.from_pretrained(
        model_dir,
        num_labels_per_task=[
            len(label_encoders[target].classes_)
            for target in PREDICTION_TARGETS
        ]
    ).to(device)
    
    tokenizer = AutoTokenizer.from_pretrained('bert-base-multilingual-cased')
    
    # Prepare input
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=256)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Get predictions
    model.eval()
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = [logits.argmax(dim=-1) for logits in outputs['logits']]
    
    # Convert to labels
    results = {}
    for i, target in enumerate(PREDICTION_TARGETS):
        predicted_label = label_encoders[target].inverse_transform([predictions[i].item()])[0]
        results[target] = predicted_label
    
    return results

if __name__ == "__main__":
    # Train model
    train_model()
    
    # Test prediction
    text = "A complaint regarding water supply issues affecting local businesses and causing environmental concerns"
    predictions = predict_all_impacts(text)
    print("\nPredictions for test text:")
    for target, prediction in predictions.items():
        print(f"{target}: {prediction}")
