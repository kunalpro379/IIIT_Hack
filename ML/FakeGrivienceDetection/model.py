import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from nltk.tokenize import word_tokenize
import nltk

# Download correct NLTK resources
try:
    print("Downloading required NLTK resources...")
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')  # Use this instead of averaged_perceptron_tagger_eng
    nltk.download('universal_tagset')
    print("NLTK resources downloaded successfully.")
except Exception as e:
    print(f"Error downloading NLTK resources: {str(e)}")
    print("Please run python and execute:")
    print("import nltk")
    print("nltk.download('punkt')")
    print("nltk.download('averaged_perceptron_tagger')")
    print("nltk.download('universal_tagset')")

class ImprovedGrievanceVerifier:
    def __init__(self):
        # Initialize models
        self.toxic_detector = pipeline(
            "text-classification",
            model="unitary/toxic-bert",
            tokenizer="unitary/toxic-bert"
        )
        
        self.hate_detector = pipeline(
            "text-classification",
            model="Hate-speech-CNERG/dehatebert-mono-english",
            tokenizer="Hate-speech-CNERG/dehatebert-mono-english"
        )
        
        self.fake_detector = pipeline(
            "text-classification",
            model="roberta-base-openai-detector",
            tokenizer="roberta-base-openai-detector"
        )
        
        # Initialize additional classifiers
        self.tfidf = TfidfVectorizer(max_features=1000)
        self.rf_classifier = RandomForestClassifier(n_estimators=100)
        
    def extract_features(self, text):
        """Extract linguistic features from text"""
        features = {}
        try:
            # Basic text features
            features['length'] = len(text)
            features['word_count'] = len(text.split())
            features['avg_word_length'] = sum(len(word) for word in text.split()) / len(text.split()) if text else 0
            
            # Linguistic features - simplified POS tagging
            try:
                tokens = word_tokenize(text)
                pos_tags = nltk.pos_tag(tokens)  # Using default English tagger
                features['noun_count'] = sum(1 for _, tag in pos_tags if tag.startswith('NN'))
                features['verb_count'] = sum(1 for _, tag in pos_tags if tag.startswith('VB'))
            except Exception as e:
                print(f"Warning: Simplified POS tagging used due to error: {str(e)}")
                features['noun_count'] = 0
                features['verb_count'] = 0
            
            # Pattern features
            features['special_chars'] = len(re.findall(r'[!@#$%^&*(),.?":{}|<>]', text))
            features['numbers'] = len(re.findall(r'\d+', text))
            
        except Exception as e:
            print(f"Warning: Error extracting features: {str(e)}")
            # Provide default values
            features = {
                'length': 0,
                'word_count': 0,
                'avg_word_length': 0,
                'noun_count': 0,
                'verb_count': 0,
                'special_chars': 0,
                'numbers': 0
            }
            
        return features

    def preprocess_text(self, text):
        """Clean and normalize text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove excessive punctuation
        text = re.sub(r'([!?.]){2,}', r'\1', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text

    def check_linguistic_patterns(self, text):
        """Check for suspicious linguistic patterns"""
        red_flags = 0
        
        # Check for repetitive patterns
        words = text.split()
        unique_words = len(set(words))
        if unique_words / len(words) < 0.4:  # High repetition
            red_flags += 1
        
        # Check for excessive punctuation
        if len(re.findall(r'[!?.]', text)) / len(text) > 0.1:
            red_flags += 1
            
        # Check for suspicious word combinations
        suspicious_patterns = [
            r'\b(kindly|please)\s+do\s+the\s+needful\b',
            r'\b(respected|dear)\s+sir/madam\b',
            r'\b(urgent|immediate)\s+action\s+required\b'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, text.lower()):
                red_flags += 1
                
        return red_flags >= 2

    def train_model(self, authentic_path, fake_path):
        """Enhanced training with multiple features"""
        print("\nLoading and processing datasets...")
        
        # Load data
        authentic_df = pd.read_csv(authentic_path)
        fake_df = pd.read_csv(fake_path)
        
        # Combine datasets
        all_texts = authentic_df['complaint'].tolist() + fake_df['complaint'].tolist()
        all_labels = [1] * len(authentic_df) + [0] * len(fake_df)
        
        # Extract features
        feature_list = []
        for text in all_texts:
            features = self.extract_features(text)
            feature_list.append(features)
            
        # Convert to DataFrame with string column names
        feature_df = pd.DataFrame(feature_list)
        feature_df.columns = feature_df.columns.astype(str)  # Convert column names to strings
        
        # Add TF-IDF features
        tfidf_features = self.tfidf.fit_transform([self.preprocess_text(text) for text in all_texts])
        tfidf_df = pd.DataFrame(
            tfidf_features.toarray(),
            columns=[f'tfidf_{i}' for i in range(tfidf_features.shape[1])]
        )
        
        # Combine features
        X = pd.concat([feature_df, tfidf_df], axis=1)
        # Ensure all column names are strings
        X.columns = X.columns.astype(str)
        
        # Train classifier
        self.rf_classifier.fit(X, all_labels)
        
        print(f"\nTraining completed with {len(authentic_df)} authentic and {len(fake_df)} fake samples")
        
        return {
            'authentic_samples': len(authentic_df),
            'fake_samples': len(fake_df)
        }

    def verify_grievance(self, text):
        """Improved verification with multiple checks"""
        # Basic validation
        if not text or len(text.strip()) < 10:
            return {
                'status': 'rejected',
                'reason': 'Grievance text too short or empty',
                'score': 0.0
            }

        # Preprocess text
        clean_text = self.preprocess_text(text)
        
        # Check for toxic content
        toxic_result = self.toxic_detector(clean_text)[0]
        hate_result = self.hate_detector(clean_text)[0]
        
        if toxic_result['label'] == 'LABEL_1' and toxic_result['score'] > 0.8:
            return {
                'status': 'rejected',
                'reason': 'Contains toxic content',
                'score': toxic_result['score']
            }
            
        if hate_result['label'] == 'LABEL_1' and hate_result['score'] > 0.8:
            return {
                'status': 'rejected',
                'reason': 'Contains hate speech',
                'score': hate_result['score']
            }
        
        # Extract features
        features = self.extract_features(clean_text)
        feature_df = pd.DataFrame([features])
        feature_df.columns = feature_df.columns.astype(str)  # Convert column names to strings
        
        # Get TF-IDF features
        tfidf_features = self.tfidf.transform([clean_text])
        tfidf_df = pd.DataFrame(
            tfidf_features.toarray(),
            columns=[f'tfidf_{i}' for i in range(tfidf_features.shape[1])]
        )
        
        # Combine features
        X = pd.concat([
            feature_df,
            tfidf_df
        ], axis=1)
        X.columns = X.columns.astype(str)  # Ensure all column names are strings
        
        # Get prediction from RF classifier
        rf_pred = self.rf_classifier.predict_proba(X)[0]
        
        # Get prediction from fake detector
        fake_result = self.fake_detector(clean_text)[0]
        
        # Check linguistic patterns
        has_suspicious_patterns = self.check_linguistic_patterns(clean_text)
        
        # Combined decision logic
        fake_score = (rf_pred[0] + fake_result['score']) / 2
        
        is_fake = (
            fake_score > 0.7 or
            has_suspicious_patterns or
            (fake_result['label'] == 'FAKE' and fake_result['score'] > 0.8)
        )
        
        return {
            'status': 'rejected' if is_fake else 'accepted',
            'reason': 'Likely AI-generated or suspicious' if is_fake else 'Authentic grievance',
            'score': fake_score,
            'confidence': min(fake_score * 100, 100)
        }

def process_grievance_dataset(file_path, verifier=None):
    """Process a dataset of grievances"""
    if verifier is None:
        verifier = ImprovedGrievanceVerifier()
    
    df = pd.read_csv(file_path)
    results = []
    
    for idx, row in df.iterrows():
        result = verifier.verify_grievance(str(row['complaint']))
        results.append({
            'id': row['id'],
            'status': result['status'],
            'reason': result['reason'],
            'confidence': result['confidence']
        })
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    try:
        print("\nInitializing Grievance Verifier...")
        verifier = ImprovedGrievanceVerifier()
        
        print("\nStarting model training...")
        authentic_path = 'E:\\ML\\Data\\combined_data.csv'
        fake_path = 'E:\\ML\\Data\\fake_grivance.csv'
        
        training_results = verifier.train_model(authentic_path, fake_path)
        print(f"\nTraining completed successfully.")
        print(f"Authentic samples processed: {training_results['authentic_samples']}")
        print(f"Fake samples processed: {training_results['fake_samples']}")
        
        print("\nProcessing test data...")
        test_path = 'E:\\ML\\Data\\fakedata.csv'
        results_df = process_grievance_dataset(test_path, verifier)
        
        output_path = 'E:\\ML\\Data\\test_results.csv'
        results_df.to_csv(output_path, index=False)
        
        print("\nResults Summary:")
        print(f"Total processed: {len(results_df)}")
        print(f"Detected as fake: {len(results_df[results_df['status'] == 'rejected'])}")
        print(f"Detected as authentic: {len(results_df[results_df['status'] == 'accepted'])}")
        print(f"Average confidence: {results_df['confidence'].mean():.2f}%")
        
    except Exception as e:
        print(f"\nError in main execution: {str(e)}")
        print("Please ensure:")
        print("1. All required files exist in E:\\ML\\Data\\")
        print("2. NLTK resources are properly downloaded")
        print("3. You have sufficient permissions to read/write files")