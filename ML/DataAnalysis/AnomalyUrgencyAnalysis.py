import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns

# Set display options for better output
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)

# Read the data
df = pd.read_csv('E:/ML/Data/combined_data.csv')

print("1. ANOMALY DETECTION IN RESOLUTION TIMES")
print("-" * 50)

# Prepare data for anomaly detection
resolution_times = df['ResolutionTime'].values.reshape(-1, 1)

# Initialize and fit Isolation Forest
iso_forest = IsolationForest(contamination=0.1, random_state=42)
anomalies = iso_forest.fit_predict(resolution_times)

# Analyze anomalies
normal_cases = resolution_times[anomalies == 1]
anomaly_cases = resolution_times[anomalies == -1]

print(f"\nTotal cases analyzed: {len(resolution_times)}")
print(f"Normal cases detected: {len(normal_cases)}")
print(f"Anomalies detected: {len(anomaly_cases)}")

# Visualize anomalies
plt.figure(figsize=(10, 6))
plt.hist(normal_cases, bins=30, alpha=0.5, label='Normal')
plt.hist(anomaly_cases, bins=30, alpha=0.5, label='Anomaly')
plt.title('Distribution of Resolution Times - Normal vs Anomaly')
plt.xlabel('Resolution Time (days)')
plt.ylabel('Frequency')
plt.legend()
plt.savefig('E:/ML/DataAnalysis/resolution_time_anomalies.png')
plt.close()

print("\n2. URGENCY PREDICTION")
print("-" * 50)

# Prepare features for urgency prediction
features = ['ResolutionTime', 'status', 'complaintType']

# Handle missing values
df['ResolutionTime'] = df['ResolutionTime'].fillna(df['ResolutionTime'].mean())
df['status'] = df['status'].fillna('Unknown')
df['complaintType'] = df['complaintType'].fillna('Other')

# Normalize urgency levels - combine Hindi and English values
df['urgencyLevel'] = df['urgencyLevel'].map({
    'High': 'High',
    'Medium': 'Medium',
    'उच्च': 'High',  # Map Hindi "High" to English
    'मध्यम': 'Medium',  # Map Hindi "Medium" to English
    'nan': 'Medium'  # Default value for NaN
}).fillna('Medium')

# Encode categorical variables
le_status = LabelEncoder()
le_complaint = LabelEncoder()
le_urgency = LabelEncoder()

# Transform features
X = pd.DataFrame({
    'ResolutionTime': df['ResolutionTime'],
    'status': le_status.fit_transform(df['status']),
    'complaintType': le_complaint.fit_transform(df['complaintType'])
})
y = le_urgency.fit_transform(df['urgencyLevel'])

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest model with class weights
rf_model = RandomForestClassifier(
    n_estimators=100,
    class_weight='balanced',
    random_state=42
)
rf_model.fit(X_train, y_train)

# Make predictions
y_pred = rf_model.predict(X_test)

# Evaluate model
print("\nModel Performance:")
print(classification_report(y_test, y_pred, target_names=le_urgency.classes_))

# Create a mapping of predictions to readable labels
urgency_mapping = dict(zip(range(len(le_urgency.classes_)), le_urgency.classes_))
print("\nUrgency Level Mapping:")
for key, value in urgency_mapping.items():
    print(f"Class {key}: {value}")

# Feature importance
feature_importance = pd.DataFrame({
    'feature': features,
    'importance': rf_model.feature_importances_
})
feature_importance = feature_importance.sort_values('importance', ascending=False)

print("\nFeature Importance:")
print(feature_importance)

# Visualize feature importance
plt.figure(figsize=(10, 6))
sns.barplot(x='importance', y='feature', data=feature_importance)
plt.title('Feature Importance for Urgency Prediction')
plt.savefig('E:/ML/DataAnalysis/feature_importance.png')
plt.close()

# Save results with proper label mapping
results = pd.DataFrame({
    'ComplaintID': df.index[X_test.index],
    'ActualUrgency': le_urgency.inverse_transform(y_test),
    'PredictedUrgency': le_urgency.inverse_transform(y_pred),
    'IsAnomaly': anomalies[X_test.index]
})

# Add confidence scores
predictions_proba = rf_model.predict_proba(X_test)
results['Confidence'] = [max(proba) for proba in predictions_proba]

# Save results to CSV with UTF-8 encoding
results.to_csv('E:/ML/DataAnalysis/anomaly_urgency_predictions.csv', 
               index=False, 
               encoding='utf-8')

print("\n3. KEY INSIGHTS")
print("-" * 50)
print(f"1. Anomaly Detection Rate: {(len(anomaly_cases)/len(resolution_times))*100:.2f}%")
print(f"2. Model Accuracy: {accuracy_score(y_test, y_pred)*100:.2f}%")
print(f"3. Most Important Feature: {feature_importance.iloc[0]['feature']}")
print(f"4. Average Resolution Time: {df['ResolutionTime'].mean():.2f} days")
print(f"5. Most Common Urgency Level: {df['urgencyLevel'].mode()[0]}")

# Additional insights about predictions
print("\n4. PREDICTION DISTRIBUTION")
print("-" * 50)
pred_dist = pd.Series(le_urgency.inverse_transform(y_pred)).value_counts()
print("\nPredicted Urgency Levels Distribution:")
print(pred_dist)

print("\nConfidence Score Statistics:")
print(f"Average Confidence: {results['Confidence'].mean():.2f}")
print(f"Min Confidence: {results['Confidence'].min():.2f}")
print(f"Max Confidence: {results['Confidence'].max():.2f}")

# Save detailed analysis with UTF-8 encoding
with open('E:/ML/DataAnalysis/anomaly_urgency_analysis.txt', 'w', encoding='utf-8') as f:
    f.write("Anomaly and Urgency Analysis Results\n")
    f.write("===================================\n\n")
    f.write(f"Total Cases Analyzed: {len(resolution_times)}\n")
    f.write(f"Anomalies Detected: {len(anomaly_cases)}\n")
    f.write(f"Anomaly Detection Rate: {(len(anomaly_cases)/len(resolution_times))*100:.2f}%\n")
    f.write(f"Model Accuracy: {accuracy_score(y_test, y_pred)*100:.2f}%\n\n")
    
    f.write("Urgency Level Distribution:\n")
    f.write(str(pred_dist) + "\n\n")
    
    f.write("Feature Importance:\n")
    f.write(str(feature_importance) + "\n\n")
    
    f.write("Confidence Score Statistics:\n")
    f.write(f"Average: {results['Confidence'].mean():.2f}\n")
    f.write(f"Min: {results['Confidence'].min():.2f}\n")
    f.write(f"Max: {results['Confidence'].max():.2f}\n")
