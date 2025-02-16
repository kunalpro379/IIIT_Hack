import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, TrainerCallback
import torch
from torch.utils.data import Dataset
import os
import pickle
from sklearn.preprocessing import LabelEncoder
import torch.multiprocessing as mp
from torch.nn.parallel import DistributedDataParallel as DDP
import torch.distributed as dist
import shutil
import psutil

# Configure device and CUDA settings
def setup_device():
    """Optimized device setup for RTX 4050"""
    try:
        if torch.cuda.is_available():
            n_gpu = torch.cuda.device_count()
            print(f"Found {n_gpu} GPU(s)")
            
            # Configure for RTX 4050
            torch.cuda.set_device(0)
            device = torch.device("cuda:0")
            
            # Optimize CUDA settings for RTX 4050
            torch.backends.cudnn.benchmark = True
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            
            # Set memory management for 6GB VRAM
            torch.cuda.empty_cache()
            
            print(f"Using GPU: {torch.cuda.get_device_name(0)}")
            print(f"Available Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
            return device, n_gpu
    except Exception as e:
        print(f"GPU Error: {str(e)}")
    
    return torch.device("cpu"), 0

# Optimize batch sizes for 6GB VRAM
BATCH_SIZE = 12  # Increased from 8
MAX_LENGTH = 256
GRADIENT_ACCUMULATION = 2  # Reduced from 4

# Load the dataset
df = pd.read_csv('gen_datasets/combined_data.csv')

# Define the target columns for prediction
target_columns = ['category', 'departmentAssigned']

# Concatenate the text columns into one input_text column
text_columns = ['complaint', 'title', 'description']
df['input_text'] = df.apply(lambda row: ' '.join([str(row[col]) for col in text_columns if col in df.columns]), axis=1)

# Custom Dataset class for grievance data
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
        try:
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

            label = row[f'{target_columns[0]}_encoded']
            
            # Return tensors on CPU, let trainer handle device movement
            return {
                'input_ids': inputs['input_ids'].squeeze(),
                'attention_mask': inputs['attention_mask'].squeeze(),
                'labels': torch.tensor(label, dtype=torch.long)
            }
        except Exception as e:
            print(f"Error processing index {index}: {str(e)}")
            return None

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained('bert-base-multilingual-cased')

# Split the dataset into train and test sets
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# Create datasets for training and testing
train_dataset = GrievanceDataset(train_df, tokenizer, max_len=MAX_LENGTH)
test_dataset = GrievanceDataset(test_df, tokenizer, max_len=MAX_LENGTH)

def create_model(num_labels, device):
    model = AutoModelForSequenceClassification.from_pretrained(
        'bert-base-multilingual-cased',
        num_labels=num_labels,
        problem_type="single_label_classification"
    ).to(device)
    
    # Remove automatic FP16 conversion
    return model

def check_disk_space(path, required_gb=10):
    """Check if there's enough disk space"""
    total, used, free = shutil.disk_usage(path)
    free_gb = free / (2**30)  # Convert to GB
    print(f"Free disk space: {free_gb:.2f} GB")
    return free_gb >= required_gb

def cleanup_output_dir(output_dir):
    """Clean up old checkpoints and logs"""
    if os.path.exists(output_dir):
        try:
            shutil.rmtree(output_dir)
            print(f"Cleaned up {output_dir}")
        except Exception as e:
            print(f"Error cleaning up {output_dir}: {e}")
    os.makedirs(output_dir, exist_ok=True)

def main():
    device, n_gpu = setup_device()
    
    # Simplify to single output directory
    model_dir = 'E:/ML/Grivances/saved_model'
    os.makedirs(model_dir, exist_ok=True)
    
    # Check disk space
    if not check_disk_space('E:/'): 
        raise RuntimeError("Not enough disk space available (need at least 10GB)")
    
    # Updated training arguments to save only final model
    training_args = TrainingArguments(
        output_dir=model_dir,
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir=os.path.join(model_dir, 'logs'),
        logging_steps=50,
        save_strategy="no",  # Don't save checkpoints
        evaluation_strategy="epoch",
        load_best_model_at_end=False,  # Don't load best model
        fp16=False,
        bf16=True if torch.cuda.is_available() else False,
        gradient_accumulation_steps=4,
        dataloader_num_workers=0,
        remove_unused_columns=True,
        report_to="none",
        no_cuda=False,
    )
    
    # Create datasets with memory-optimized settings
    train_dataset = GrievanceDataset(
        train_df, 
        tokenizer, 
        max_len=MAX_LENGTH
    )
    test_dataset = GrievanceDataset(
        test_df, 
        tokenizer, 
        max_len=MAX_LENGTH
    )
    
    # Initialize model with half precision
    model = create_model(
        len(train_dataset.label_encoders[target_columns[0]].classes_),
        device
    )
    
    # Add custom memory management
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
    )
    
    # Add memory optimization callback
    class MemoryCallback(TrainerCallback):
        def on_epoch_end(self, args, state, control, **kwargs):
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            print(f"Epoch {state.epoch} completed")
    
    trainer.add_callback(MemoryCallback())
    
    # Train with error handling
    try:
        print("Starting training...")
        trainer.train()
        print("Training completed. Saving final model...")
        
        # Save only the final model
        trainer.save_model(model_dir)
        
        # Save label encoders with the model
        with open(os.path.join(model_dir, 'label_encoders.pkl'), 'wb') as f:
            pickle.dump(train_dataset.label_encoders, f)
            
        print(f"Model and label encoders saved to {model_dir}")
        
    except Exception as e:
        print(f"Error during training/saving: {str(e)}")
        raise

def predict_grievance(text, device):
    """Updated prediction function with E drive path"""
    try:
        # Use E drive path
        model_dir = 'E:/ML/Grivances/model_output/grievance_model/final_model'
        
        if not os.path.exists(model_dir):
            raise ValueError(f"Model directory not found at {model_dir}")
        
        # Load model and move to device
        model = AutoModelForSequenceClassification.from_pretrained(model_dir).to(device)
        model.eval()  # Set to evaluation mode
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_dir)
        
        # Load label encoders
        le_path = os.path.join(model_dir, 'label_encoders.pkl')
        with open(le_path, 'rb') as f:
            label_encoders = pickle.load(f)
        
        # Prepare input
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=MAX_LENGTH)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Get predictions
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Process predictions
        predictions = {}
        for i, col in enumerate(target_columns):
            pred = outputs.logits[0][i].argmax().item()
            predictions[col] = label_encoders[col].inverse_transform([pred])[0]
        
        return predictions
        
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        return None

if __name__ == "__main__":
    # Run training
    main()
    
    # Wait a moment to ensure model is saved
    import time
    time.sleep(2)
    
    # Test prediction with correct path
    device, _ = setup_device()
    text = "A complaint regarding the delayed response from customer service."
    predictions = predict_grievance(text, device)
    
    if predictions:
        print(f"Predicted grievance details: {predictions}")
    else:
        print("Prediction failed")
