import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import torch
from sklearn.metrics import classification_report
import joblib
import warnings
warnings.filterwarnings('ignore')

# Read data
print("Loading and preparing data...")
df = pd.read_csv('E:/ML/Data/combined_data.csv')
df['CreatedAt'] = pd.to_datetime(df['CreatedAt'])

# 1. Time Series Analysis for Complaint Patterns
print("\n1. ANALYZING TEMPORAL PATTERNS")
print("-" * 50)
df['month'] = df['CreatedAt'].dt.month
df['day_of_week'] = df['CreatedAt'].dt.dayofweek
df['hour'] = df['CreatedAt'].dt.hour

monthly_patterns = df.groupby('month').size()
daily_patterns = df.groupby('day_of_week').size()

print("\nComplaint Distribution by Month:")
print(monthly_patterns)
print("\nComplaint Distribution by Day:")
print(daily_patterns)

# 2. Prepare Features for Traditional ML Model
print("\n2. PREPARING PREDICTION MODELS")
print("-" * 50)

# Feature Engineering
features_df = pd.DataFrame({
    'month': df['month'],
    'day_of_week': df['day_of_week'],
    'hour': df['hour'],
    'ResolutionTime': df['ResolutionTime'],
})

# Add encoded categorical features
le = LabelEncoder()
features_df['complaintType'] = le.fit_transform(df['complaintType'].fillna('Unknown'))
features_df['status'] = le.fit_transform(df['status'])
features_df['district'] = le.fit_transform(df['district'])
features_df['urgencyLevel'] = le.fit_transform(df['urgencyLevel'].fillna('Medium'))

# 3. Train Traditional ML Model
X = features_df.drop('urgencyLevel', axis=1)
y = features_df['urgencyLevel']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Save the model
joblib.dump(rf_model, 'E:/ML/Models/grievance_predictor.joblib')

# 4. Load Hugging Face Model for Text Classification
print("\n3. PREPARING TRANSFORMER MODEL")
print("-" * 50)

# Initialize zero-shot classification pipeline
classifier = pipeline("zero-shot-classification")

# Define possible categories based on your data
categories = [
    "Infrastructure",
    "Public Services",
    "Safety",
    "Environment",
    "Health",
    "Utilities",
    "Transportation",
    "Education"
]

# 5. Make Predictions
print("\n4. MAKING PREDICTIONS")
print("-" * 50)

# Function to predict future grievances
def predict_future_grievances(days_ahead=30):
    last_date = df['CreatedAt'].max()
    future_dates = pd.date_range(start=last_date, periods=days_ahead, freq='D')
    
    predictions = []
    for date in future_dates:
        # Prepare features for traditional model
        features = {
            'month': date.month,
            'day_of_week': date.dayofweek,
            'hour': 12,  # Default to noon
            'ResolutionTime': df['ResolutionTime'].mean(),
            'complaintType': 0,  # Default value
            'status': 0,  # Default value
            'district': 0  # Default value
        }
        
        # Make prediction
        urgency_pred = rf_model.predict([list(features.values())])[0]
        
        predictions.append({
            'date': date,
            'predicted_urgency': le.inverse_transform([urgency_pred])[0],
            'confidence': rf_model.predict_proba([list(features.values())])[0].max()
        })
    
    return pd.DataFrame(predictions)

# Make predictions for next 30 days
future_predictions = predict_future_grievances(30)

# 6. Analyze Common Complaint Patterns
print("\n5. ANALYZING COMPLAINT PATTERNS")
print("-" * 50)

# Sample some complaints for text analysis
sample_complaints = df['complaint'].sample(n=min(100, len(df))).tolist()

# Analyze complaint types using transformer
complaint_categories = []
for text in sample_complaints[:5]:  # Limited sample for demonstration
    result = classifier(text, categories)
    complaint_categories.append({
        'text': text[:100] + '...',
        'predicted_category': result['labels'][0],
        'confidence': result['scores'][0]
    })

# Save predictions and analysis
print("\n6. SAVING RESULTS")
print("-" * 50)

# Save future predictions
future_predictions.to_csv('E:/ML/DataAnalysis/future_grievance_predictions.csv', index=False)

# Save complaint pattern analysis
pd.DataFrame(complaint_categories).to_csv('E:/ML/DataAnalysis/complaint_pattern_analysis.csv', index=False)

# Generate summary report
with open('E:/ML/DataAnalysis/grievance_prediction_report.txt', 'w') as f:
    f.write("Future Grievance Prediction Report\n")
    f.write("================================\n\n")
    f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    f.write("1. Model Performance\n")
    f.write(f"Traditional Model Accuracy: {rf_model.score(X_test, y_test):.2f}\n\n")
    
    f.write("2. Expected Grievance Patterns\n")
    f.write("Monthly Distribution:\n")
    f.write(str(monthly_patterns) + "\n\n")
    
    f.write("3. Most Likely Complaint Categories:\n")
    for cat in complaint_categories:
        f.write(f"- {cat['predicted_category']} (Confidence: {cat['confidence']:.2f})\n")
    
    f.write("\n4. Recommendations:\n")
    f.write("- Focus resources on high-frequency complaint days\n")
    f.write("- Prepare for predicted urgent cases\n")
    f.write("- Monitor identified problem areas\n")

print("\n7. KEY INSIGHTS")
print("-" * 50)
print(f"1. Model Accuracy: {rf_model.score(X_test, y_test):.2f}")
print(f"2. Most Common Complaint Type: {df['complaintType'].mode()[0]}")
print(f"3. Peak Complaint Month: {monthly_patterns.idxmax()}")
print(f"4. Expected Urgent Cases Next Month: {len(future_predictions[future_predictions['predicted_urgency'] == 'High'])}")
print("\nDetailed results saved in 'grievance_prediction_report.txt'")
