import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Load and prepare data
df = pd.read_csv('/e:/ML/DataAnalysis/combined_data.csv')
df['CreatedAt'] = pd.to_datetime(df['CreatedAt'])

def analyze_seasonal_patterns():
    """Analyze seasonal patterns in complaints"""
    df['month'] = df['CreatedAt'].dt.month
    df['day_of_week'] = df['CreatedAt'].dt.dayofweek
    df['hour'] = df['CreatedAt'].dt.hour

    # Monthly patterns
    monthly_counts = df.groupby(['month', 'category']).size().unstack(fill_value=0)
    
    # Create heatmap
    fig = px.imshow(monthly_counts,
                    labels=dict(x="Category", y="Month", color="Number of Complaints"),
                    title="Monthly Complaint Patterns by Category")
    fig.write_html('/e:/ML/Analysis/monthly_patterns.html')
    
    return monthly_counts

def predict_emerging_categories():
    """Predict emerging complaint categories"""
    # Calculate growth rate for each category
    category_trends = df.groupby(['CreatedAt', 'category']).size().unstack(fill_value=0)
    
    # Calculate month-over-month growth
    growth_rates = category_trends.pct_change().mean().sort_values(ascending=False)
    
    # Identify emerging categories (top 5 fastest growing)
    emerging_categories = growth_rates.head()
    
    return emerging_categories

def forecast_complaint_volumes():
    """Forecast future complaint volumes using Prophet"""
    # Prepare data for Prophet
    daily_complaints = df.groupby('CreatedAt').size().reset_index()
    daily_complaints.columns = ['ds', 'y']
    
    # Train Prophet model
    model = Prophet(yearly_seasonality=True,
                   weekly_seasonality=True,
                   daily_seasonality=False)
    model.fit(daily_complaints)
    
    # Make future predictions
    future_dates = model.make_future_dataframe(periods=90)  # 3 months forecast
    forecast = model.predict(future_dates)
    
    # Create forecast plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily_complaints['ds'], y=daily_complaints['y'],
                            mode='lines', name='Historical'))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'],
                            mode='lines', name='Forecast',
                            line=dict(dash='dash')))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'],
                            fill=None, mode='lines', line=dict(width=0),
                            showlegend=False))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'],
                            fill='tonexty', mode='lines', line=dict(width=0),
                            name='Confidence Interval'))
    
    fig.update_layout(title='Complaint Volume Forecast',
                      xaxis_title='Date',
                      yaxis_title='Number of Complaints')
    fig.write_html('/e:/ML/Analysis/forecast_plot.html')
    
    return forecast

def identify_anomalies():
    """Identify unusual spikes in complaints"""
    daily_counts = df.groupby('CreatedAt').size()
    
    # Calculate rolling statistics
    rolling_mean = daily_counts.rolling(window=7).mean()
    rolling_std = daily_counts.rolling(window=7).std()
    
    # Identify anomalies (days with complaints > 2 std from mean)
    anomalies = daily_counts[abs(daily_counts - rolling_mean) > 2 * rolling_std]
    
    return anomalies

def generate_trends_report():
    """Generate comprehensive trends report"""
    # Get all analyses
    seasonal_patterns = analyze_seasonal_patterns()
    emerging_cats = predict_emerging_categories()
    forecast = forecast_complaint_volumes()
    anomalies = identify_anomalies()
    
    # Save report
    with open('/e:/ML/Analysis/trends_report.md', 'w') as f:
        f.write("# Complaint Trends Analysis Report\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d')}\n\n")
        
        f.write("## Emerging Categories\n")
        f.write("Top 5 fastest growing complaint categories:\n")
        for cat, growth in emerging_cats.items():
            f.write(f"- {cat}: {growth:.2%} average monthly growth\n")
        
        f.write("\n## Seasonal Patterns\n")
        f.write("Monthly variation in complaint volumes:\n")
        f.write(str(seasonal_patterns.mean()) + "\n\n")
        
        f.write("## Forecast Summary\n")
        f.write("Predicted complaint volumes for next 90 days:\n")
        f.write(f"- Average: {forecast['yhat'].mean():.0f} complaints/day\n")
        f.write(f"- Maximum: {forecast['yhat_upper'].max():.0f} complaints/day\n")
        f.write(f"- Minimum: {forecast['yhat_lower'].min():.0f} complaints/day\n\n")
        
        f.write("## Anomalous Days\n")
        f.write("Days with unusually high complaint volumes:\n")
        for date, count in anomalies.items():
            f.write(f"- {date.strftime('%Y-%m-%d')}: {count} complaints\n")

if __name__ == "__main__":
    print("Starting trends analysis...")
    generate_trends_report()
    print("Analysis completed! Check the trends_report.md file for results.")
