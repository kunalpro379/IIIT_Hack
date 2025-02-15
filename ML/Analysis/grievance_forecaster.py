import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
import json
from prophet import Prophet
import os

class TimeSeriesDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class LSTMForecaster(nn.Module):
    def __init__(self, input_size=1, hidden_size=50, num_layers=2):
        super(LSTMForecaster, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.linear = nn.Linear(hidden_size, 1)
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        predictions = self.linear(lstm_out[:, -1, :])
        return predictions

class GrievanceForecaster:
    def __init__(self, data_path):
        """Initialize with data loading and preprocessing"""
        try:
            self.df = pd.read_csv(data_path)
            self.df['CreatedAt'] = pd.to_datetime(self.df['CreatedAt'])
            # Fill missing categories
            self.df['category'] = self.df['category'].fillna('Uncategorized')
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            print(f"Loaded {len(self.df)} complaints")
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            raise

    def analyze_patterns(self):
        """Analyze seasonal complaint patterns by category with error handling"""
        try:
            # Ensure we have valid categories
            valid_categories = self.df['category'].value_counts()
            valid_categories = valid_categories[valid_categories > 0]
            
            if len(valid_categories) == 0:
                raise ValueError("No valid categories found in the data")
                
            seasonal_data = self.df.groupby([
                self.df['CreatedAt'].dt.month, 
                'category'
            ]).size().unstack(fill_value=0)
            
            # Create heatmap
            fig = px.imshow(seasonal_data,
                          labels=dict(x="Category", y="Month", 
                                    color="Number of Complaints"),
                          title="Seasonal Complaint Patterns")
            
            # Ensure output directory exists
            os.makedirs(r'E:\ML\Analysis\outputs', exist_ok=True)
            fig.write_html(r'E:\ML\Analysis\outputs\seasonal_patterns.html')
            
            return seasonal_data
            
        except Exception as e:
            print(f"Error in pattern analysis: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame on error

    def train_model(self, data, sequence_length=30, epochs=100):
        """Train PyTorch model for forecasting"""
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(data.reshape(-1, 1))
        
        # Prepare sequences
        X, y = [], []
        for i in range(len(scaled_data) - sequence_length):
            X.append(scaled_data[i:i+sequence_length])
            y.append(scaled_data[i+sequence_length])
        
        X = np.array(X)
        y = np.array(y)
        
        # Create dataset and dataloader
        dataset = TimeSeriesDataset(X, y)
        dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
        
        # Initialize model
        model = LSTMForecaster().to(self.device)
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters())
        
        # Training loop
        model.train()
        for epoch in range(epochs):
            for batch_X, batch_y in dataloader:
                batch_X = batch_X.to(self.device)
                batch_y = batch_y.to(self.device)
                
                optimizer.zero_grad()
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
        
        return model, scaler

    def generate_forecast(self, category):
        """Generate forecast for a specific category"""
        cat_data = self.df[self.df['category'] == category]
        daily_counts = cat_data.groupby('CreatedAt').size().values
        
        model, scaler = self.train_model(daily_counts)
        
        # Generate future predictions
        last_sequence = torch.FloatTensor(daily_counts[-30:]).reshape(1, 30, 1).to(self.device)
        
        model.eval()
        with torch.no_grad():
            forecast = model(last_sequence)
            forecast = scaler.inverse_transform(forecast.cpu().numpy())
        
        return forecast[0][0]

    def generate_report(self):
        """Generate comprehensive forecast report with proper encoding"""
        try:
            seasonal_patterns = self.analyze_patterns()
            forecasts = {}
            
            # Get valid categories with sufficient data
            valid_categories = self.df.groupby('category').filter(
                lambda x: len(x) >= 30
            )['category'].unique()
            
            print(f"Generating forecasts for {len(valid_categories)} categories...")
            
            for category in valid_categories:
                try:
                    forecast_value = self.generate_forecast(category)
                    if forecast_value > 0:  # Only include valid forecasts
                        forecasts[category] = forecast_value
                except Exception as e:
                    print(f"Error forecasting {category}: {str(e)}")
                    continue
            
            # Save report with UTF-8 encoding
            report_path = r'E:\ML\Analysis\outputs\forecast_report.md'
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("# Grievance Forecast Report\n\n")
                
                f.write("## Category-wise Forecasts\n")
                for category, forecast in forecasts.items():
                    f.write(f"- {category}: {forecast:.2f} predicted cases\n")
                
                f.write("\n## Seasonal Patterns\n")
                if not seasonal_patterns.empty:
                    f.write(seasonal_patterns.to_markdown())
                else:
                    f.write("No seasonal patterns could be analyzed\n")
            
            return forecasts, seasonal_patterns
            
        except Exception as e:
            print(f"Error generating report: {str(e)}")
            return {}, pd.DataFrame()

if __name__ == "__main__":
    try:
        print("Starting grievance forecasting analysis...")
        
        forecaster = GrievanceForecaster(r'E:\ML\Data\combined_data.csv')
        forecasts, patterns = forecaster.generate_report()
        
        if forecasts:
            print("\nAnalysis completed! Check the outputs folder for detailed reports.")
            
            # Print summary
            print("\nTop 5 Categories by Predicted Volume:")
            top_categories = dict(sorted(forecasts.items(), 
                                      key=lambda x: x[1], 
                                      reverse=True)[:5])
            for category, forecast in top_categories.items():
                print(f"{category}: {forecast:.2f} predicted cases")
        else:
            print("\nNo valid forecasts could be generated.")
            
    except Exception as e:
        print(f"Error in main execution: {str(e)}")
