import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Read the data
df = pd.read_csv('/e:/ML/Data/combined_data.csv')

# Basic data exploration
print("\nBasic Data Information:")
print(df.info())
print("\nMissing Values:")
print(df.isnull().sum())

# Convert dates to datetime
df['CreatedAt'] = pd.to_datetime(df['CreatedAt'])
df['lastUpdatedDate'] = pd.to_datetime(df['lastUpdatedDate'])
df['updatedAt'] = pd.to_datetime(df['updatedAt'])

# Analysis of complaint types
print("\nComplaint Type Distribution:")
complaint_dist = df['complaintType'].value_counts()
print(complaint_dist)

# Analysis of status distribution
print("\nStatus Distribution:")
status_dist = df['status'].value_counts()
print(status_dist)

# Create visualizations
plt.figure(figsize=(12, 6))
sns.countplot(data=df, x='status')
plt.title('Distribution of Complaint Status')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('/e:/ML/DataAnalysis/status_distribution.png')

# Analyze urgency levels
plt.figure(figsize=(10, 6))
sns.countplot(data=df, x='urgencyLevel')
plt.title('Distribution of Urgency Levels')
plt.tight_layout()
plt.savefig('/e:/ML/DataAnalysis/urgency_levels.png')

# Time-based analysis
df['month'] = df['CreatedAt'].dt.month
monthly_complaints = df.groupby('month').size()

plt.figure(figsize=(12, 6))
monthly_complaints.plot(kind='bar')
plt.title('Monthly Distribution of Complaints')
plt.xlabel('Month')
plt.ylabel('Number of Complaints')
plt.tight_layout()
plt.savefig('/e:/ML/DataAnalysis/monthly_distribution.png')

# Analysis of resolution time
df['ResolutionTime'] = pd.to_numeric(df['ResolutionTime'], errors='coerce')
plt.figure(figsize=(10, 6))
sns.boxplot(x='status', y='ResolutionTime', data=df)
plt.title('Resolution Time by Status')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('/e:/ML/DataAnalysis/resolution_time.png')

# Department-wise analysis
dept_complaints = df['departmentAssigned'].value_counts()
plt.figure(figsize=(15, 6))
dept_complaints.plot(kind='bar')
plt.title('Complaints by Department')
plt.xlabel('Department')
plt.ylabel('Number of Complaints')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('/e:/ML/DataAnalysis/department_complaints.png')

# Correlation analysis for numeric columns
numeric_cols = df.select_dtypes(include=[np.number]).columns
correlation = df[numeric_cols].corr()
plt.figure(figsize=(12, 8))
sns.heatmap(correlation, annot=True, cmap='coolwarm')
plt.title('Correlation Matrix')
plt.tight_layout()
plt.savefig('/e:/ML/DataAnalysis/correlation_matrix.png')

# Predict future problems
# Prepare data for prediction
le = LabelEncoder()
df['status_encoded'] = le.fit_transform(df['status'])
df['complaintType_encoded'] = le.fit_transform(df['complaintType'])
df['urgencyLevel_encoded'] = le.fit_transform(df['urgencyLevel'])

# Features for prediction
features = ['complaintType_encoded', 'urgencyLevel_encoded', 'ResolutionTime', 'month']
X = df[features].fillna(0)
y = df['status_encoded']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Make predictions
y_pred = rf_model.predict(X_test)

# Print model performance
print("\nModel Performance:")
print(classification_report(y_test, y_pred))

# Feature importance
feature_importance = pd.DataFrame({
    'feature': features,
    'importance': rf_model.feature_importances_
})
feature_importance = feature_importance.sort_values('importance', ascending=False)
print("\nFeature Importance:")
print(feature_importance)

# Generate insights and recommendations
print("\nKey Insights and Recommendations:")
print("1. Most Common Complaints:", complaint_dist.head().index.tolist())
print("2. Average Resolution Time:", df['ResolutionTime'].mean())
print("3. Departments with Highest Workload:", dept_complaints.head().index.tolist())
print("4. Most Urgent Issues:", df[df['urgencyLevel'] == 'High']['complaintType'].value_counts().head().index.tolist())

# Save analysis results to a file
with open('/e:/ML/DataAnalysis/analysis_results.txt', 'w') as f:
    f.write("Data Analysis Results\n")
    f.write("===================\n\n")
    f.write(f"Total number of complaints: {len(df)}\n")
    f.write(f"Date range: {df['CreatedAt'].min()} to {df['CreatedAt'].max()}\n")
    f.write(f"Average resolution time: {df['ResolutionTime'].mean():.2f} days\n")
    f.write(f"Percentage of resolved cases: {(df['status'] == 'Closed').mean()*100:.2f}%\n")
