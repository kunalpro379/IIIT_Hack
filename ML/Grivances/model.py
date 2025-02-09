import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import torch
from torch.utils.data import Dataset
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

df = pd.read_csv('gen_datasets/combined_data.csv')

target_columns = [
    'category',           
    'subcategory',        
    'departmentAssigned', 
    'urgencyLevel',       
    'emotion',            
    'socialImpact',       
    'economicImpact',     
    'environmentalImpact'  
]

print("Available columns:", df.columns.tolist())
print("Target columns present:", [col for col in target_columns if col in df.columns])

text_columns = ['complaint', 'title', 'description']

df['input_text'] = df.apply(lambda row: ' '.join([str(row[col]) for col in text_columns if col in df.columns]), axis=1)

class GrievanceDataset(Dataset):
    def __init__(self, dataframe, tokenizer, max_len):
        self.tokenizer = tokenizer
        self.data = dataframe
        self.max_len = max_len

        self.label_encoders = {}
        self.num_labels = {}
        for col in target_columns:
            if col in self.data.columns:
                self.data[col] = self.data[col].fillna('unknown')
                self.data[col] = self.data[col].astype(str)
                le = LabelEncoder()
                self.data[f'{col}_encoded'] = le.fit_transform(self.data[col])
                self.label_encoders[col] = le
                self.num_labels[col] = len(le.classes_)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        row = self.data.iloc[index]
        text = str(row['input_text'])

        inputs = self.tokenizer.encode_plus(
            text,
            None,
            add_special_tokens=True,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        labels = []
        for col in target_columns:
            if col in self.data.columns:
                labels.append(row[f'{col}_encoded'])
        
        labels = torch.tensor(labels[0], dtype=torch.long)  # Take first target for now

        return {
            'input_ids': inputs['input_ids'].squeeze(),
            'attention_mask': inputs['attention_mask'].squeeze(),
            'labels': labels
        }

tokenizer = AutoTokenizer.from_pretrained('bert-base-multilingual-cased')

train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

train_dataset = GrievanceDataset(train_df, tokenizer, max_len=512)
test_dataset = GrievanceDataset(test_df, tokenizer, max_len=512)

model = AutoModelForSequenceClassification.from_pretrained(
    'bert-base-multilingual-cased',
    num_labels=len(train_dataset.label_encoders[target_columns[0]].classes_),  # Use first target's classes
    problem_type="single_label_classification"
)

# Create checkpoints directory if it doesn't exist
os.makedirs('checkpoints', exist_ok=True)

# Modify training arguments to save checkpoints more frequently and handle interruptions
training_args = TrainingArguments(
    output_dir='./checkpoints',
    num_train_epochs=3,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    save_strategy="steps",
    save_steps=50,
    evaluation_strategy="steps",
    eval_steps=50,
    save_total_limit=3,  # Keep only last 3 checkpoints
    load_best_model_at_end=True,
    # Add fp16 for memory efficiency
    fp16=True if torch.cuda.is_available() else False,
)

# Try to resume from checkpoint
last_checkpoint = None
if os.path.exists('checkpoints'):
    checkpoints = [f for f in os.listdir('checkpoints') if f.startswith('checkpoint-')]
    if checkpoints:
        last_checkpoint = os.path.join('checkpoints', sorted(checkpoints)[-1])

# Initialize trainer with checkpoint handling
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
)

# Train with error handling
try:
    trainer.train(resume_from_checkpoint=last_checkpoint)
    # Save final model
    trainer.save_model('final_model')
except Exception as e:
    print(f"Training was interrupted: {e}")
    # Save checkpoint even on error
    trainer.save_model('interrupted_model')
    raise e

model.save_pretrained('./grievance_model')
tokenizer.save_pretrained('./grievance_model')

def predict_grievance(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    outputs = model(**inputs)
    
    predictions = {}
    for i, col in enumerate(target_columns):
        pred = outputs.logits[0][i].argmax().item()
        predictions[col] = train_dataset.label_encoders[col][pred]
    
    return predictions

print("Model training complete and saved to './grievance_model'")

class GrievancePriorityPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.label_encoders = {}
        self.scaler = StandardScaler()
        
    def preprocess_data(self, df):
        df_processed = df.copy()
        
        date_columns = ['CreatedAt', 'lastUpdatedDate', 'date', 'submissionDate', 'updatedAt']
        for col in date_columns:
            if col in df_processed.columns:
                df_processed[col] = pd.to_datetime(df_processed[col])
                df_processed[f'{col}_year'] = df_processed[col].dt.year
                df_processed[f'{col}_month'] = df_processed[col].dt.month
                df_processed[f'{col}_day'] = df_processed[col].dt.day
                df_processed.drop(col, axis=1, inplace=True)

        if 'ResolutionTime' in df_processed.columns:
            df_processed['ResolutionTime'] = pd.to_numeric(df_processed['ResolutionTime'], errors='coerce')

        if 'isAnonymous' in df_processed.columns:
            df_processed['isAnonymous'] = df_processed['isAnonymous'].astype(int)

        categorical_columns = [
            'complaint_type', 'location', 'citizenName', 'category', 
            'economicImpact', 'environmentalImpact', 'emotion', 'tehsil',
            'complaintType', 'socialImpact', 'status', 'district',
            'subcategory', 'urgencyLevel', 'ward', 'departmentAssigned'
        ]

        for col in categorical_columns:
            if col in df_processed.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df_processed[col] = self.label_encoders[col].fit_transform(df_processed[col].astype(str))
                else:
                    df_processed[col] = self.label_encoders[col].transform(df_processed[col].astype(str))

        numeric_columns = df_processed.select_dtypes(include=['float64', 'int64']).columns
        if not hasattr(self, 'numeric_columns'):
            self.numeric_columns = numeric_columns

        df_processed[numeric_columns] = self.scaler.fit_transform(df_processed[numeric_columns])

        return df_processed

    def train(self, X, y):
        X_processed = self.preprocess_data(X)
        
        self.model.fit(X_processed, y)
        
        y_pred = self.model.predict(X_processed)
        mse = mean_squared_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        
        print(f"Training MSE: {mse}")
        print(f"Training R2 Score: {r2}")

    def predict(self, X):
        X_processed = self.preprocess_data(X)
        
        return self.model.predict(X_processed)

    def save_model(self, filepath):
        """Save the trained model and preprocessors"""
        model_data = {
            'model': self.model,
            'label_encoders': self.label_encoders,
            'scaler': self.scaler,
            'numeric_columns': self.numeric_columns if hasattr(self, 'numeric_columns') else None
        }
        joblib.dump(model_data, filepath)

    @classmethod
    def load_model(cls, filepath):
        """Load a trained model and preprocessors"""
        model_data = joblib.load(filepath)
        predictor = cls()
        predictor.model = model_data['model']
        predictor.label_encoders = model_data['label_encoders']
        predictor.scaler = model_data['scaler']
        predictor.numeric_columns = model_data['numeric_columns']
        return predictor

def calculate_priority_score(row):
    """Calculate a base priority score based on various factors"""
    score = 0
    
    impact_weights = {
        'High': 30,
        'Medium': 20,
        'Low': 10
    }
    
    if 'economicImpact' in row:
        score += impact_weights.get(row['economicImpact'].split(' ')[0], 0)
    if 'environmentalImpact' in row:
        score += impact_weights.get(row['environmentalImpact'].split(' ')[0], 0)
    if 'socialImpact' in row:
        score += impact_weights.get(row['socialImpact'].split(' ')[0], 0)
    
    if 'urgencyLevel' in row:
        urgency_weights = {'High': 30, 'Medium': 20, 'Low': 10}
        score += urgency_weights.get(row['urgencyLevel'], 0)
    
    if 'status' in row:
        status_weights = {'Open': 10, 'In Progress': 5, 'Closed': 0}
        score += status_weights.get(row['status'], 0)
    
    if 'ResolutionTime' in row:
        try:
            resolution_time = float(row['ResolutionTime'])
            if resolution_time > 20:  # If resolution time is high
                score += 10
        except (ValueError, TypeError):
            pass

    score = min(100, max(0, score))
    return score

def main():
    df = pd.read_csv('/c:/Users/kunal/OneDrive/CODE FOR LIFE/IIITHack/ML/Grivances/gen_datasets/combined_data.csv')
    
    df['priorityScore'] = df.apply(calculate_priority_score, axis=1)
    
    feature_columns = [col for col in df.columns if col not in ['priorityScore']]
    X = df[feature_columns]
    y = df['priorityScore']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    predictor = GrievancePriorityPredictor()
    predictor.train(X_train, y_train)
    
    y_pred = predictor.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Test MSE: {mse}")
    print(f"Test R2 Score: {r2}")
    
    predictor.save_model('grievance_priority_model.joblib')

if __name__ == "__main__":
    main()
