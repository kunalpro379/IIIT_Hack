import pandas as pd
import numpy as np
from prophet import Prophet
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
import json

# Load data
df = pd.read_csv('/e:/ML/DataAnalysis/combined_data.csv')
df['CreatedAt'] = pd.to_datetime(df['CreatedAt'])

def analyze_seasonal_patterns():
    """Analyze seasonal complaint patterns by category"""
    seasonal_data = df.groupby([df['CreatedAt'].dt.month, 'category']).size().unstack()
    
    # Create heatmap
    fig = px.imshow(seasonal_data,
                    labels=dict(x="Category", y="Month", color="Number of Complaints"),
                    title="Seasonal Complaint Patterns")
    fig.write_html('/e:/ML/Analysis/seasonal_patterns.html')
    
    return seasonal_data

def forecast_category_trends():
    """Forecast trends for each complaint category"""
    forecasts = {}
    
    for category in df['category'].unique():
        cat_data = df[df['category'] == category]
        daily_counts = cat_data.groupby('CreatedAt').size().reset_index()
        daily_counts.columns = ['ds', 'y']
        
        # Train Prophet model
        model = Prophet(yearly_seasonality=True, weekly_seasonality=True)
        model.fit(daily_counts)
        
        # Make future predictions
        future = model.make_future_dataframe(periods=180)  # 6 months
        forecast = model.predict(future)
        
        forecasts[category] = forecast
        
        # Create category-specific plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_counts['ds'], y=daily_counts['y'],
                                mode='lines', name='Historical'))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'],
                                mode='lines', name='Forecast'))
        fig.update_layout(title=f'Forecast for {category} Complaints')
        fig.write_html(f'/e:/ML/Analysis/forecasts/{category}_forecast.html')
    
    return forecasts

def train_lstm_model(data):
    """Train LSTM model for detailed forecasting"""
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data.reshape(-1, 1))
    
    # Prepare sequences
    sequence_length = 30
    X, y = [], []
    for i in range(len(scaled_data) - sequence_length):
        X.append(scaled_data[i:i+sequence_length])
        y.append(scaled_data[i+sequence_length])
    
    X = np.array(X)
    y = np.array(y)
    
    # Build model
    model = Sequential([
        LSTM(50, activation='relu', input_shape=(sequence_length, 1), return_sequences=True),
        Dropout(0.2),
        LSTM(50, activation='relu'),
        Dense(1)
    ])
    
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=100, batch_size=32, verbose=0)
    
    return model, scaler

def generate_trend_report():
    """Generate comprehensive trend analysis report"""
    # Get forecasts
    seasonal_patterns = analyze_seasonal_patterns()
    category_forecasts = forecast_category_trends()
    
    # Identify rising trends
    rising_categories = []
    for category, forecast in category_forecasts.items():
        current_avg = forecast['yhat'][-180:].mean()
        past_avg = forecast['yhat'][:-180].mean()
        if current_avg > past_avg:
            rising_categories.append({
                'category': category,
                'growth_rate': (current_avg - past_avg) / past_avg * 100
            })
    
    # Sort by growth rate
    rising_categories.sort(key=lambda x: x['growth_rate'], reverse=True)
    
    # Save report
    with open('/e:/ML/Analysis/trend_forecast_report.md', 'w') as f:
        f.write("# Future Grievance Trends Forecast Report\n\n")
        
        f.write("## Rising Complaint Categories\n")
        for cat in rising_categories:
            f.write(f"- {cat['category']}: {cat['growth_rate']:.2f}% projected increase\n")
        
        f.write("\n## Seasonal Patterns\n")
        f.write(str(seasonal_patterns.describe()) + "\n\n")
        
        f.write("## Recommendations\n")
        # Generate recommendations using the trends
        recommendations = generate_recommendations(rising_categories, seasonal_patterns)
        f.write(recommendations)

def generate_recommendations(rising_categories, seasonal_patterns):
    """Generate AI-powered recommendations based on trends"""
    trend_summary = {
        'rising_categories': rising_categories,
        'seasonal_patterns': seasonal_patterns.to_dict()
    }
    
    prompt = f"""
    Based on these complaint trends:
    {json.dumps(trend_summary, indent=2)}
    
    Provide:
    1. Resource allocation recommendations
    2. Preventive measures for rising complaints
    3. Seasonal preparation strategies
    4. Long-term improvement suggestions
    """
    
    # Use GPT-4 for generating insights
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    print("Starting trend forecasting analysis...")
    generate_trend_report()
    print("Analysis completed! Check the reports folder for detailed forecasts.")
