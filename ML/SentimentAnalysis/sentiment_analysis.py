# Check required packages
def check_dependencies():
    required_packages = ['textblob', 'sklearn', 'pandas', 'numpy', 'joblib']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if (missing_packages):
        print("Missing required packages. Please install:")
        for package in missing_packages:
            print(f"pip install {package}")
        return False
    return True

if not check_dependencies():
    exit(1)

# Import required packages
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, mean_squared_error
import joblib

class GrievancePredictor:
    def __init__(self):
        self.tfidf = TfidfVectorizer(max_features=1500)
        self.emotion_classifier = RandomForestClassifier(n_estimators=200)
        self.resolution_regressor = RandomForestRegressor(n_estimators=200)
        self.urgency_classifier = RandomForestClassifier(n_estimators=200)
        self.emotion_encoder = LabelEncoder()
        self.urgency_encoder = LabelEncoder()
        
    def preprocess_data(self, df):
        # Clean text data
        df['complaint'] = df['complaint'].fillna('')
        df['complaint'] = df['complaint'].astype(str)
        
        # Handle missing values and standardize labels
        df['emotion'] = df['emotion'].fillna('Neutral')
        df['ResolutionTime'] = df['ResolutionTime'].fillna(df['ResolutionTime'].mean())
        df['urgencyLevel'] = df['urgencyLevel'].fillna('Medium')
        
        # Standardize Hindi/English labels
        emotion_mapping = {
            'नाराज': 'Angry',
            'गुस्सा': 'Angry',
            'निराश': 'Disappointed',
            'चिंतित': 'Concerned',
            'असंतुष्ट': 'Disappointed'
        }
        urgency_mapping = {
            'उच्च': 'High',
            'मध्यम': 'Medium',
            'कम': 'Low'
        }
        
        df['emotion'] = df['emotion'].replace(emotion_mapping)
        df['urgencyLevel'] = df['urgencyLevel'].replace(urgency_mapping)
        
        return df
    
    def train(self, data_path):
        print("Loading and preprocessing data...")
        df = pd.read_csv(data_path)
        df = self.preprocess_data(df)
        
        # Create features
        print("Creating features...")
        X = self.tfidf.fit_transform(df['complaint'])
        
        # Prepare targets
        y_emotion = self.emotion_encoder.fit_transform(df['emotion'])
        y_resolution = df['ResolutionTime'].values
        y_urgency = self.urgency_encoder.fit_transform(df['urgencyLevel'])
        
        # Split data
        X_train, X_test, y_emotion_train, y_emotion_test = train_test_split(X, y_emotion, test_size=0.2)
        _, _, y_resolution_train, y_resolution_test = train_test_split(X, y_resolution, test_size=0.2)
        _, _, y_urgency_train, y_urgency_test = train_test_split(X, y_urgency, test_size=0.2)
        
        # Train models
        print("\nTraining models...")
        
        print("Training emotion classifier...")
        self.emotion_classifier.fit(X_train, y_emotion_train)
        emotion_pred = self.emotion_classifier.predict(X_test)
        print("\nEmotion Classification Report:")
        print(classification_report(y_emotion_test, emotion_pred))
        
        print("\nTraining resolution time predictor...")
        self.resolution_regressor.fit(X_train, y_resolution_train)
        resolution_pred = self.resolution_regressor.predict(X_test)
        mse = mean_squared_error(y_resolution_test, resolution_pred)
        print(f"Resolution Time MSE: {mse:.2f}")
        
        print("\nTraining urgency classifier...")
        self.urgency_classifier.fit(X_train, y_urgency_train)
        urgency_pred = self.urgency_classifier.predict(X_test)
        print("\nUrgency Classification Report:")
        print(classification_report(y_urgency_test, urgency_pred))
        
        # Save models
        print("\nSaving models...")
        joblib.dump(self.emotion_classifier, 'emotion_model.pkl')
        joblib.dump(self.resolution_regressor, 'resolution_model.pkl')
        joblib.dump(self.urgency_classifier, 'urgency_model.pkl')
        joblib.dump(self.tfidf, 'tfidf.pkl')
        joblib.dump(self.emotion_encoder, 'emotion_encoder.pkl')
        joblib.dump(self.urgency_encoder, 'urgency_encoder.pkl')
        
        return {
            'emotion_classes': self.emotion_encoder.classes_.tolist(),
            'urgency_levels': self.urgency_encoder.classes_.tolist()
        }
    
    def predict(self, text):
        try:
            # Transform text
            X = self.tfidf.transform([text])
            
            # Make predictions
            emotion = self.emotion_encoder.inverse_transform([self.emotion_classifier.predict(X)[0]])[0]
            resolution_time = int(self.resolution_regressor.predict(X)[0])
            urgency = self.urgency_encoder.inverse_transform([self.urgency_classifier.predict(X)[0]])[0]
            
            return {
                'emotion': emotion,
                'resolution_time_days': resolution_time,
                'urgency_level': urgency
            }
        except Exception as e:
            print(f"Error in prediction: {str(e)}")
            return {
                'emotion': 'Unknown',
                'resolution_time_days': 0,
                'urgency_level': 'Unknown'
            }

def predict_grievances(data_path, output_path=None):
    predictor = GrievancePredictor()
    
    # Train models
    print("Training models...")
    predictor.train(data_path)
    
    # Make predictions on the dataset
    df = pd.read_csv(data_path)
    results = []
    
    print("\nMaking predictions...")
    for text in df['complaint']:
        result = predictor.predict(text)
        results.append(result)
    
    # Create results DataFrame
    results_df = pd.DataFrame(results)
    
    if output_path:
        results_df.to_csv(output_path, index=False)
        print(f"\nResults saved to {output_path}")
    
    # Print summary statistics
    print("\nPrediction Summary:")
    print("\nEmotion Distribution:")
    print(results_df['emotion'].value_counts())
    print("\nUrgency Level Distribution:")
    print(results_df['urgency_level'].value_counts())
    print(f"\nAverage Resolution Time: {results_df['resolution_time_days'].mean():.1f} days")
    
    return results_df

if __name__ == "__main__":
    data_path = 'E:\\ML\\Data\\combined_data.csv'
    output_path = 'E:\\ML\\Data\\predictions.csv'
    
    try:
        results_df = predict_grievances(data_path, output_path)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Please ensure:")
        print("1. The dataset file exists at the specified path")
        print("2. The dataset contains 'complaint', 'emotion', 'ResolutionTime', and 'urgencyLevel' columns")
        print("3. You have sufficient permissions to read/write files")
