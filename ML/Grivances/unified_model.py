import pandas as pd
from transformers import (
    AutoTokenizer, 
    AutoModel,
    BertPreTrainedModel, 
    Trainer, 
    TrainingArguments,
    EarlyStoppingCallback,
    TrainerCallback,  # Added TrainerCallback
    MarianMTModel,  # Added for translation
    MarianTokenizer,  # Added for translation
)
# ...existing imports...
from sklearn.model_selection import KFold, train_test_split
from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset
import os
import pickle
from sklearn.preprocessing import LabelEncoder
import random
from nltk.corpus import wordnet
import nltk
import shutil
from glob import glob  # Added glob import

# Simple augmentation setup
AUGMENTATION_AVAILABLE = False
try:
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')
    AUGMENTATION_AVAILABLE = True
except:
    print("NLTK WordNet not available. Running without augmentation...")

# Add deep-translator with proper error handling
TRANSLATOR_AVAILABLE = False
try:
    TRANSLATOR_AVAILABLE = True
except ImportError:
    print("deep-translator not installed. Install using: pip install deep-translator")
    print("Running without translation augmentation...")

class SimpleAugmenter:
    def __init__(self):
        self.enabled = AUGMENTATION_AVAILABLE
    
    def get_synonyms(self, word):
        synonyms = []
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                if lemma.name() != word:
                    synonyms.append(lemma.name())
        return list(set(synonyms))
    
    def augment_text(self, text):
        if not self.enabled:
            return text
        
        words = text.split()
        num_to_replace = max(1, len(words) // 10)  # Replace 10% of words
        indices = random.sample(range(len(words)), min(num_to_replace, len(words)))
        
        for idx in indices:
            word = words[idx]
            synonyms = self.get_synonyms(word)
            if synonyms:
                words[idx] = random.choice(synonyms)
        
        return ' '.join(words)

# Combined prediction targets
ALL_TARGETS = [
    'category',           
    'economicImpact',     
    'environmentalImpact',
    'socialImpact',
    'relatedPolicies',
    'ResolutionTime',
    'subcategory',
    'departmentAssigned',
    'complaint_type',
]

class HighAccuracyClassifier(BertPreTrainedModel):
    def __init__(self, config, num_labels_per_task):
        super().__init__(config)
        # Use XLM-RoBERTa-large as base
        self.transformer = AutoModel.from_pretrained('xlm-roberta-large')
        self.config = config
        
        # Enhanced architecture with correct dimensions
        hidden_size = self.transformer.config.hidden_size  # Get actual hidden size
        self.intermediate = nn.Sequential(
            nn.Linear(hidden_size, hidden_size * 2),
            nn.LayerNorm(hidden_size * 2),
            nn.Dropout(0.3),
            nn.GELU(),
            nn.Linear(hidden_size * 2, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.Dropout(0.2)
        )
        
        # Task-specific heads with correct dimensions
        self.classifiers = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_size, hidden_size),
                nn.LayerNorm(hidden_size),
                nn.Dropout(0.2),
                nn.GELU(),
                nn.Linear(hidden_size, hidden_size // 2),
                nn.LayerNorm(hidden_size // 2),
                nn.Dropout(0.1),
                nn.GELU(),
                nn.Linear(hidden_size // 2, num_labels)
            )
            for num_labels in num_labels_per_task
        ])

    def forward(self, input_ids, attention_mask=None, labels=None):
        # Get transformer outputs
        outputs = self.transformer(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=True
        )
        
        # Use pooler output if available, else use last hidden state mean
        if hasattr(outputs, 'pooler_output'):
            pooled_output = outputs.pooler_output
        else:
            pooled_output = torch.mean(outputs.last_hidden_state, dim=1)
        
        # Process through intermediate layer
        intermediate_output = self.intermediate(pooled_output)
        
        # Get predictions from each classifier
        logits = [classifier(intermediate_output) for classifier in self.classifiers]
        
        # Handle loss calculation if labels provided
        loss = None
        if labels is not None:
            loss_fct = nn.CrossEntropyLoss(label_smoothing=0.1)
            loss = sum(loss_fct(logit, labels[:, i]) for i, logit in enumerate(logits))
            
            # Add L2 regularization
            l2_lambda = 0.01
            l2_reg = torch.tensor(0., requires_grad=True).to(labels.device)
            for param in self.parameters():
                l2_reg = l2_reg + torch.norm(param)
            loss += l2_lambda * l2_reg

        return {'loss': loss, 'logits': logits} if loss is not None else {'logits': logits}

# Add memory management environment variable
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

# Add the TextTranslator class definition before EnhancedDataset
class TextTranslator:
    def __init__(self):
        try:
            # Initialize MarianMT models
            self.en_es_model = MarianMTModel.from_pretrained('Helsinki-NLP/opus-mt-en-es')
            self.en_es_tokenizer = MarianTokenizer.from_pretrained('Helsinki-NLP/opus-mt-en-es')
            self.es_en_model = MarianMTModel.from_pretrained('Helsinki-NLP/opus-mt-es-en')
            self.es_en_tokenizer = MarianTokenizer.from_pretrained('Helsinki-NLP/opus-mt-es-en')
            
            # Move models to GPU if available
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.en_es_model = self.en_es_model.to(device)
            self.es_en_model = self.es_en_model.to(device)
            self.device = device
            self.available = True
        except Exception as e:
            print(f"Translation models initialization failed: {e}")
            self.available = False
    
    def translate(self, text, source_lang="en", target_lang="es"):
        if not self.available or not text:
            return text
            
        try:
            # Select appropriate model and tokenizer
            if source_lang == "en" and target_lang == "es":
                model = self.en_es_model
                tokenizer = self.en_es_tokenizer
            elif source_lang == "es" and target_lang == "en":
                model = self.es_en_model
                tokenizer = self.es_en_tokenizer
            else:
                return text
            
            # Tokenize and translate
            inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True).to(self.device)
            translated = model.generate(**inputs)
            result = tokenizer.batch_decode(translated, skip_special_tokens=True)[0]
            
            return result
        except Exception as e:
            print(f"Translation error: {e}")
            return text

class EnhancedDataset(Dataset):
    def __init__(self, dataframe, tokenizer, max_len, augment=False):
        # Create a copy of the dataframe to avoid warnings
        self.data = dataframe.copy()
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.augment = augment and AUGMENTATION_AVAILABLE
        self.augmenter = SimpleAugmenter() if augment else None
        self.translator = TextTranslator() if augment else None
        
        # Create label encoders for all target columns
        self.label_encoders = {}
        for target in ALL_TARGETS:
            # Fix DataFrame warnings using .loc
            self.data.loc[self.data[target].isna(), target] = 'unknown'
            self.data.loc[:, target] = self.data[target].astype(str)
            le = LabelEncoder()
            self.data.loc[:, f'{target}_encoded'] = le.fit_transform(self.data[target])
            self.label_encoders[target] = le
        
        # Add semantic sentence embeddings for better augmentation
        if augment:
            self.st_model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

    def augment_text(self, text):
        if not self.augment:
            return text
            
        augmented_texts = []
        
        # 1. Synonym replacement
        if hasattr(self, 'augmenter'):
            augmented_texts.append(self.augmenter.augment_text(text))
            
        # 2. Back translation using MarianMT
        if hasattr(self, 'translator') and self.translator.available:
            try:
                spanish = self.translator.translate(text, "en", "es")
                back_translated = self.translator.translate(spanish, "es", "en")
                if back_translated and back_translated != text:
                    augmented_texts.append(back_translated)
            except Exception as e:
                print(f"Translation augmentation error: {e}")
                
        # 3. Semantic similarity-based augmentation
        if hasattr(self, 'st_model'):
            embeddings = self.st_model.encode([text])[0]
            # Use embeddings to find similar sentences in training data
            # ...

        return random.choice(augmented_texts) if augmented_texts else text

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        text = str(self.data.iloc[index]['input_text'])
        if self.augment and random.random() < 0.3:  # 30% chance of augmentation
            text = self.augment_text(text)
        labels = [self.data.iloc[index][f'{target}_encoded'] for target in ALL_TARGETS]
        
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

# Add disk space management
def check_disk_space(path='E:/', required_gb=10):
    total, used, free = shutil.disk_usage(path)
    free_gb = free / (2**30)
    print(f"Free space on E drive: {free_gb:.2f} GB")
    return free_gb >= required_gb

def cleanup_old_models(model_dir):
    """Clean up old model files and cache"""
    paths_to_clean = [
        model_dir,
        'E:/ML/Grivances/cache',
        os.path.join(os.path.expanduser('~'), '.cache/huggingface')
    ]
    
    for path in paths_to_clean:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                print(f"Cleaned up: {path}")
            except Exception as e:
                print(f"Error cleaning {path}: {e}")
    
    # Recreate necessary directories
    for path in paths_to_clean[:2]:  # Only recreate model_dir and cache
        os.makedirs(path, exist_ok=True)

def cleanup_cuda_memory():
    """Clean up CUDA memory"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()

def train_unified_model():
    # Check disk space first
    if not check_disk_space():
        raise RuntimeError("Not enough disk space on E drive (need at least 10GB)")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load and prepare data
    df = pd.read_csv('gen_datasets/combined_data.csv')
    text_columns = ['complaint', 'title', 'description']
    df['input_text'] = df.apply(lambda row: ' '.join([str(row[col]) for col in text_columns if col in df.columns]), axis=1)
    
    # Split data
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    
    # Initialize tokenizer and datasets
    tokenizer = AutoTokenizer.from_pretrained('xlm-roberta-large')
    train_dataset = EnhancedDataset(train_df, tokenizer, max_len=256, augment=True)
    test_dataset = EnhancedDataset(test_df, tokenizer, max_len=256, augment=False)
    
    # Get number of labels for each target
    num_labels_per_task = [
        len(train_dataset.label_encoders[target].classes_)
        for target in ALL_TARGETS
    ]

    # Use E drive for all storage
    model_dir = 'E:/ML/Grivances/unified_model'
    cache_dir = 'E:/ML/Grivances/cache'  # New cache directory
    os.makedirs(cache_dir, exist_ok=True)
    
    # Set environment variable for transformers cache
    os.environ['TRANSFORMERS_CACHE'] = cache_dir
    os.environ['HF_HOME'] = cache_dir
    
    # Add memory cleanup before training
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        
    # Initialize model with smaller size
    model = HighAccuracyClassifier.from_pretrained(
        'xlm-roberta-base',  # Changed from large to base
        num_labels_per_task=num_labels_per_task,
        cache_dir=cache_dir
    ).to(device)
    
    # Modified training arguments for better memory management
    training_args = TrainingArguments(
        output_dir=model_dir,
        num_train_epochs=5,  # Reduced epochs
        per_device_train_batch_size=2,  # Reduced from 4
        per_device_eval_batch_size=4,   # Reduced from 8
        evaluation_strategy="steps",
        eval_steps=100,
        save_strategy="steps",     # Match with evaluation_strategy
        save_steps=100,           # Match with eval_steps
        save_total_limit=1,      # Keep only best model
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        learning_rate=1e-5,
        warmup_ratio=0.1,
        weight_decay=0.01,
        gradient_accumulation_steps=16,  # Increased from 8
        fp16=True,
        dataloader_num_workers=0,
        remove_unused_columns=True,
        report_to="none",
        logging_steps=50,
        hub_token=None,
        save_safetensors=True,
        # Add memory optimization settings
        optim='adamw_torch_fused',
        gradient_checkpointing=True,
    )

    # Use a custom cleanup callback
    class CleanupCallback(TrainerCallback):
        def on_save(self, args, state, control, **kwargs):
            cleanup_old_checkpoints(args.output_dir)
            cleanup_cuda_memory()
            
        def on_epoch_end(self, args, state, control, **kwargs):
            cleanup_cuda_memory()
    
    # Define MemoryEfficientTrainer class
    class MemoryEfficientTrainer(Trainer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
        def _wrap_model(self, model):
            if hasattr(model, 'module'):
                return model
            return super()._wrap_model(model)
            
        def compute_loss(self, model, inputs, return_outputs=False):
            # Free memory from last step
            if hasattr(self, '_last_outputs'):
                del self._last_outputs
            outputs = super().compute_loss(model, inputs, return_outputs)
            if return_outputs:
                self._last_outputs = outputs
            return outputs
    
    # Initialize trainer with cleanup
    trainer = MemoryEfficientTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        callbacks=[
            EarlyStoppingCallback(early_stopping_patience=3),
            CleanupCallback()
        ]
    )
    
    # Setup k-fold cross validation
    n_splits = 5
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    # Train ensemble of models
    models = []
    for fold, (train_idx, val_idx) in enumerate(kf.split(df)):
        print(f"\nTraining fold {fold + 1}/{n_splits}")
        
        # Prepare train and validation datasets for the current fold
        train_fold_df = df.iloc[train_idx]
        val_fold_df = df.iloc[val_idx]
        
        train_fold_dataset = EnhancedDataset(train_fold_df, tokenizer, max_len=256, augment=True)
        val_fold_dataset = EnhancedDataset(val_fold_df, tokenizer, max_len=256, augment=False)
        
        # Initialize Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_fold_dataset,
            eval_dataset=val_fold_dataset,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
        )
        
        # Train the model
        trainer.train()
        
        # Save the trained model
        trained_model = model
        models.append(trained_model)
    
    return models, tokenizer, train_dataset.label_encoders

def cleanup_old_checkpoints(output_dir):
    """Clean up old checkpoints while keeping the best one"""
    try:
        checkpoints = glob(os.path.join(output_dir, 'checkpoint-*'))
        if len(checkpoints) > 1:
            # Sort by modification time
            checkpoints.sort(key=lambda x: os.path.getmtime(x))
            # Keep the latest checkpoint
            for checkpoint in checkpoints[:-1]:
                shutil.rmtree(checkpoint)
                print(f"Removed checkpoint: {checkpoint}")
    except Exception as e:
        print(f"Error cleaning checkpoints: {e}")

def predict_all(text, models, tokenizer, label_encoders):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Prepare input
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=256)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Ensemble prediction
    all_predictions = []
    
    for model in models:
        # Get predictions from each model
        model.eval()
        with torch.no_grad():
            outputs = model(**inputs)
            # Move logits to CPU before converting to numpy
            predictions = [logits.cpu().argmax(dim=-1).numpy() for logits in outputs['logits']]
            all_predictions.append(predictions)
    
    # Convert predictions to numpy arrays
    all_predictions = np.array(all_predictions)
    final_predictions = np.mean(all_predictions, axis=0)
    
    # Convert to labels
    results = {}
    available_targets = list(label_encoders.keys())  # Use actual available targets
    
    for i, target in enumerate(available_targets):
        pred_idx = int(np.argmax(final_predictions[i]))  # Convert to int
        predicted_label = label_encoders[target].inverse_transform([pred_idx])[0]
        results[target] = predicted_label
    
    return results

def load_model_artifacts(base_path='E:/ML/Grivances/saved_model'):
    """Load the trained model and associated artifacts"""
    try:
        print("Loading model artifacts from:", base_path)
        
        # Load label encoders first to get num_labels_per_task
        le_path = os.path.join(base_path, 'label_encoders.pkl')
        if not os.path.exists(le_path):
            raise FileNotFoundError(f"Label encoders not found at {le_path}")
            
        print("Loading label encoders...")
        with open(le_path, 'rb') as f:
            label_encoders = pickle.load(f)
        
        # Calculate num_labels_per_task
        num_labels_per_task = []
        available_targets = list(label_encoders.keys())
        print(f"Available targets: {available_targets}")
        
        for target in available_targets:
            n_labels = len(label_encoders[target].classes_)
            print(f"{target}: {n_labels} labels")
            num_labels_per_task.append(n_labels)
        
        # Load model
        print(f"\nLoading model from: {base_path}")
        model = HighAccuracyClassifier.from_pretrained(
            base_path,
            num_labels_per_task=num_labels_per_task
        )
        
        # Load tokenizer
        print("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained('xlm-roberta-large')
        
        print("Successfully loaded all artifacts")
        return [model], tokenizer, label_encoders
        
    except Exception as e:
        print(f"Error loading artifacts: {str(e)}")
        raise

if __name__ == "__main__":
    # Train model
    models, tokenizer, label_encoders = train_unified_model()
    
    # Test prediction
    test_text = "A complaint regarding water supply issues affecting local businesses and causing environmental concerns"
    predictions = predict_all(test_text, models, tokenizer, label_encoders)
    
    print("\nUnified Predictions:")
    for target, prediction in predictions.items():
        print(f"{target}: {prediction}")
