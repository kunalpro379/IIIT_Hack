import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import xgboost as xgb
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

# Deep Learning Framework Selection
DEEP_LEARNING = None

import torch
import torch.nn as nn

class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_size=50, output_size=1):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.linear = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        predictions = self.linear(lstm_out[:, -1, :])
        return predictions

DEEP_LEARNING = 'torch' if torch.cuda.is_available() else None
if DEEP_LEARNING:
    print("Using PyTorch for deep learning")
else:
    print("GPU not available. Will use statistical models only.")

class GrievancePredictor:
    def __init__(self):
        self.models = {}
        self.label_encoders = {}
        self.scaler = StandardScaler()
        
    def prepare_time_series_data(self, df):
        # Aggregate daily complaints
        daily_counts = df.groupby('CreatedAt').size().reset_index()
        daily_counts.columns = ['ds', 'y']
        return daily_counts
    
    def train_prophet_model(self, df):
        """Train Facebook Prophet model for complaint volume prediction"""
        daily_counts = self.prepare_time_series_data(df)
        
        # Initialize and train Prophet model
        prophet_model = Prophet(yearly_seasonality=True, weekly_seasonality=True)
        prophet_model.fit(daily_counts)
        
        # Make future predictions
        future_dates = prophet_model.make_future_dataframe(periods=30)
        forecast = prophet_model.predict(future_dates)
        
        # Create visualization
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_counts['ds'], y=daily_counts['y'],
                                mode='lines', name='Historical'))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'],
                                mode='lines', name='Forecast'))
        fig.update_layout(title='Complaint Volume Forecast (Prophet)',
                         xaxis_title='Date', yaxis_title='Number of Complaints')
        
        self.models['prophet'] = prophet_model
        return fig, forecast
    
    def train_arima_model(self, df):
        """Train ARIMA model for complaint volume prediction"""
        daily_counts = self.prepare_time_series_data(df)
        
        # Fit ARIMA model
        model = ARIMA(daily_counts['y'], order=(1,1,1))
        arima_model = model.fit()
        
        # Make predictions
        forecast = arima_model.forecast(steps=30)
        
        # Create visualization
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_counts['ds'], y=daily_counts['y'],
                                mode='lines', name='Historical'))
        fig.add_trace(go.Scatter(x=pd.date_range(start=daily_counts['ds'].iloc[-1],
                                                periods=31)[1:],
                                y=forecast,
                                mode='lines', name='Forecast'))
        fig.update_layout(title='Complaint Volume Forecast (ARIMA)',
                         xaxis_title='Date', yaxis_title='Number of Complaints')
        
        self.models['arima'] = arima_model
        return fig, forecast
    
    def train_lstm_model(self, df):
        """Train LSTM model for complaint volume prediction"""
        daily_counts = self.prepare_time_series_data(df)
        
        # Prepare sequences
        sequence_length = 7
        X, y = [], []
        values = daily_counts['y'].values
        for i in range(len(values) - sequence_length):
            X.append(values[i:i+sequence_length])
            y.append(values[i+sequence_length])
        
        X = np.array(X)
        y = np.array(y)
        
        if DEEP_LEARNING == 'torch':
            # Use PyTorch implementation
            X = torch.FloatTensor(X.reshape(-1, sequence_length, 1))
            y = torch.FloatTensor(y)
            model = LSTMModel()
            optimizer = torch.optim.Adam(model.parameters())
            criterion = nn.MSELoss()
            
            for epoch in range(50):
                optimizer.zero_grad()
                outputs = model(X)
                loss = criterion(outputs.squeeze(), y)
                loss.backward()
                optimizer.step()
        else:
            # Fallback to simple statistical model
            model = ExponentialSmoothing(daily_counts['y']).fit()
        
        # Make predictions
        last_sequence = values[-sequence_length:]
        forecast = []
        
        if DEEP_LEARNING == 'torch':
            for _ in range(30):
                next_pred = model(torch.FloatTensor(last_sequence.reshape(1, sequence_length, 1)))
                forecast.append(next_pred.item())
                last_sequence = np.append(last_sequence[1:], next_pred.item())
        else:
            forecast = model.forecast(steps=30)
        
        # Create visualization
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_counts['ds'], y=daily_counts['y'],
                                mode='lines', name='Historical'))
        fig.add_trace(go.Scatter(x=pd.date_range(start=daily_counts['ds'].iloc[-1],
                                                periods=31)[1:],
                                y=forecast,
                                mode='lines', name='Forecast'))
        fig.update_layout(title='Complaint Volume Forecast (LSTM)',
                         xaxis_title='Date', yaxis_title='Number of Complaints')
        
        self.models['lstm'] = model
        return fig, forecast
    
    def prepare_ml_features(self, df):
        """Prepare features for ML models"""
        features = []
        
        if 'category' in df.columns:
            self.label_encoders['category'] = LabelEncoder()
            features.append(
                self.label_encoders['category'].fit_transform(df['category']))
            
        if 'district' in df.columns:
            self.label_encoders['district'] = LabelEncoder()
            features.append(
                self.label_encoders['district'].fit_transform(df['district']))
            
        if 'description' in df.columns:
            # Add text length as feature
            features.append(df['description'].str.len())
        
        numerical_features = ['ResolutionTime', 'economicImpact', 
                            'socialImpact', 'environmentalImpact']
        for feat in numerical_features:
            if feat in df.columns:
                features.append(df[feat].fillna(0))
        
        X = np.column_stack(features)
        return self.scaler.fit_transform(X)
    
    def train_urgency_predictor(self, df):
        """Train model to predict complaint urgency"""
        X = self.prepare_ml_features(df)
        y = LabelEncoder().fit_transform(df['urgencyLevel'])
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        # Train Random Forest
        rf_model = RandomForestClassifier(n_estimators=100)
        rf_model.fit(X_train, y_train)
        
        # Train XGBoost
        xgb_model = xgb.XGBClassifier()
        xgb_model.fit(X_train, y_train)
        
        self.models['urgency_rf'] = rf_model
        self.models['urgency_xgb'] = xgb_model
        
        # Create feature importance plot
        importance = pd.DataFrame({
            'feature': range(X.shape[1]),
            'importance': rf_model.feature_importances_
        })
        fig = px.bar(importance.sort_values('importance', ascending=False),
                    x='feature', y='importance',
                    title='Feature Importance for Urgency Prediction')
        
        return fig
    
    def train_resolution_predictor(self, df):
        """Train model to predict resolution time"""
        X = self.prepare_ml_features(df)
        y = df['ResolutionTime'].values
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        # Train Random Forest
        rf_model = RandomForestRegressor(n_estimators=100)
        rf_model.fit(X_train, y_train)
        
        # Train XGBoost
        xgb_model = xgb.XGBRegressor()
        xgb_model.fit(X_train, y_train)
        
        self.models['resolution_rf'] = rf_model
        self.models['resolution_xgb'] = xgb_model
        
        # Create feature importance plot
        importance = pd.DataFrame({
            'feature': range(X.shape[1]),
            'importance': rf_model.feature_importances_
        })
        fig = px.bar(importance.sort_values('importance', ascending=False),
                    x='feature', y='importance',
                    title='Feature Importance for Resolution Time Prediction')
        
        return fig

def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

def check_non_nan_rows(df):
    non_nan_rows = df.dropna(how='all')
    if len(non_nan_rows) < 2:
        raise ValueError("Dataframe has less than 2 non-NaN rows.")
    return non_nan_rows

def run_predictive_analysis(data_path):
    """Main function to run all predictive analyses"""
    df = load_data(data_path)
    df['CreatedAt'] = pd.to_datetime(df['CreatedAt'])
    
    try:
        df = check_non_nan_rows(df)
        
        predictor = GrievancePredictor()
        figures = []
        
        try:
            # Time series forecasting
            prophet_fig, prophet_forecast = predictor.train_prophet_model(df)
            figures.append(prophet_fig)
            
            arima_fig, arima_forecast = predictor.train_arima_model(df)
            figures.append(arima_fig)
            
            lstm_fig, lstm_forecast = predictor.train_lstm_model(df)
            figures.append(lstm_fig)
            
            # ML-based predictions
            urgency_fig = predictor.train_urgency_predictor(df)
            figures.append(urgency_fig)
            
            resolution_fig = predictor.train_resolution_predictor(df)
            figures.append(resolution_fig)
            
            # Generate summary
            summary = {
                'Forecast (Next 30 Days)': {
                    'Prophet': prophet_forecast['yhat'].tail(30).mean(),
                    'ARIMA': arima_forecast.mean(),
                    'LSTM': np.mean(lstm_forecast)
                },
                'Model Performance': {
                    'Urgency Prediction (RF)': predictor.models['urgency_rf'].score(
                        predictor.scaler.transform(predictor.prepare_ml_features(df)),
                        LabelEncoder().fit_transform(df['urgencyLevel'])
                    ),
                    'Resolution Time Prediction (RF)': predictor.models['resolution_rf'].score(
                        predictor.scaler.transform(predictor.prepare_ml_features(df)),
                        df['ResolutionTime'].values
                    )
                }
            }
            
            return figures, summary
            
        except Exception as e:
            print(f"Error in predictive analysis: {str(e)}")
            return None, None
    except ValueError as e:
        print(f"Error in predictive analysis: {e}")

def main():
    data_path = 'E:\\ML\\Data\\combined_data.csv'
    figures, summary = run_predictive_analysis(data_path)
    
    if figures and summary:
        print("\nPredictive Analysis Summary:")
        for key, value in summary.items():
            print(f"\n{key}:")
            for subkey, subvalue in value.items():
                print(f"  {subkey}: {subvalue:.2f}")

    # Historical data analysis
    df = pd.read_csv(data_path)

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
    plt.savefig('E:\\ML\\DataAnalysis\\status_distribution.png')

    # Analyze urgency levels
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='urgencyLevel')
    plt.title('Distribution of Urgency Levels')
    plt.tight_layout()
    plt.savefig('E:\\ML\\DataAnalysis\\urgency_levels.png')

    # Time-based analysis
    df['month'] = df['CreatedAt'].dt.month
    monthly_complaints = df.groupby('month').size()

    plt.figure(figsize=(12, 6))
    monthly_complaints.plot(kind='bar')
    plt.title('Monthly Distribution of Complaints')
    plt.xlabel('Month')
    plt.ylabel('Number of Complaints')
    plt.tight_layout()
    plt.savefig('E:\\ML\\DataAnalysis\\monthly_distribution.png')

    # Analysis of resolution time
    df['ResolutionTime'] = pd.to_numeric(df['ResolutionTime'], errors='coerce')
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='status', y='ResolutionTime', data=df)
    plt.title('Resolution Time by Status')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('E:\\ML\\DataAnalysis\\resolution_time.png')

    # Department-wise analysis
    dept_complaints = df['departmentAssigned'].value_counts()
    plt.figure(figsize=(15, 6))
    dept_complaints.plot(kind='bar')
    plt.title('Complaints by Department')
    plt.xlabel('Department')
    plt.ylabel('Number of Complaints')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('E:\\ML\\DataAnalysis\\department_complaints.png')

    # Correlation analysis for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    correlation = df[numeric_cols].corr()
    plt.figure(figsize=(12, 8))
    sns.heatmap(correlation, annot=True, cmap='coolwarm')
    plt.title('Correlation Matrix')
    plt.tight_layout()
    plt.savefig('E:\\ML\\DataAnalysis\\correlation_matrix.png')

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
    with open('E:\\ML\\DataAnalysis\\analysis_results.txt', 'w') as f:
        f.write("Data Analysis Results\n")
        f.write("===================\n\n")
        f.write(f"Total number of complaints: {len(df)}\n")
        f.write(f"Date range: {df['CreatedAt'].min()} to {df['CreatedAt'].max()}\n")
        f.write(f"Average resolution time: {df['ResolutionTime'].mean():.2f} days\n")
        f.write(f"Percentage of resolved cases: {(df['status'] == 'Closed').mean()*100:.2f}%\n")

if __name__ == "__main__":
    main()

# Read the data
print("Loading data...")
df = pd.read_csv('/e:/ML/Data/combined_data.csv')

# Basic data preprocessing
print("\nPreprocessing data...")

# Handle missing values
df = df.fillna({
    'complaintType': 'Unknown',
    'status': 'Pending',
    'urgencyLevel': 'Medium',
    'ResolutionTime': df['ResolutionTime'].median(),
    'departmentAssigned': 'Unassigned'
})

# Convert dates to datetime
date_columns = ['CreatedAt', 'lastUpdatedDate', 'updatedAt']
for col in date_columns:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col])

# Create temporal features
df['month'] = df['CreatedAt'].dt.month
df['day'] = df['CreatedAt'].dt.day
df['hour'] = df['CreatedAt'].dt.hour

# Encode categorical variables
le = LabelEncoder()
categorical_columns = ['complaintType', 'status', 'urgencyLevel', 'departmentAssigned']
encoded_features = {}

for col in categorical_columns:
    if col in df.columns:
        df[f'{col}_encoded'] = le.fit_transform(df[col])
        encoded_features[col] = df[f'{col}_encoded']

# Prepare features for prediction
print("\nPreparing features for prediction...")
features = ['month', 'day', 'hour']
features.extend([f'{col}_encoded' for col in categorical_columns if col in df.columns])

# Ensure ResolutionTime is numeric
df['ResolutionTime'] = pd.to_numeric(df['ResolutionTime'], errors='coerce')
if 'ResolutionTime' in df.columns:
    features.append('ResolutionTime')

X = df[features].fillna(0)
y = df['status_encoded'] if 'status_encoded' in df.columns else le.fit_transform(df['status'])

# Split the data
print("\nSplitting data into train and test sets...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train the model
print("\nTraining Random Forest model...")
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train_scaled, y_train)

# Make predictions
print("\nMaking predictions...")
y_pred = rf_model.predict(X_test_scaled)

# Print model performance
print("\nModel Performance:")
print(classification_report(y_test, y_pred))

# Feature importance analysis
print("\nFeature Importance Analysis:")
feature_importance = pd.DataFrame({
    'feature': features,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)
print(feature_importance)

# Visualizations
print("\nGenerating visualizations...")

# 1. Complaint Distribution
plt.figure(figsize=(12, 6))
df['complaintType'].value_counts().head(10).plot(kind='bar')
plt.title('Top 10 Types of Complaints')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('/e:/ML/DataAnalysis/complaint_distribution.png')

# 2. Status Distribution
plt.figure(figsize=(10, 6))
df['status'].value_counts().plot(kind='pie', autopct='%1.1f%%')
plt.title('Complaint Status Distribution')
plt.savefig('/e:/ML/DataAnalysis/status_distribution.png')

# 3. Monthly Trend
plt.figure(figsize=(12, 6))
df.groupby('month').size().plot(kind='line', marker='o')
plt.title('Monthly Complaint Trend')
plt.xlabel('Month')
plt.ylabel('Number of Complaints')
plt.tight_layout()
plt.savefig('/e:/ML/DataAnalysis/monthly_trend.png')

# Save predictions and insights
print("\nSaving analysis results...")
with open('/e:/ML/DataAnalysis/analysis_results.txt', 'w') as f:
    f.write("Predictive Analysis Results\n")
    f.write("==========================\n\n")
    f.write(f"Total number of complaints analyzed: {len(df)}\n")
    f.write(f"Model accuracy score: {accuracy_score(y_test, y_pred):.2f}\n\n")
    f.write("Top predictive features:\n")
    for idx, row in feature_importance.head().iterrows():
        f.write(f"- {row['feature']}: {row['importance']:.3f}\n")
    f.write("\nCommon complaint types:\n")
    for complaint, count in df['complaintType'].value_counts().head().items():
        f.write(f"- {complaint}: {count}\n")

print("\nAnalysis completed! Results saved in /e:/ML/DataAnalysis/")
