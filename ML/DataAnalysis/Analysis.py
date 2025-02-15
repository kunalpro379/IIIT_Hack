import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import folium
from textblob import TextBlob
import os
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure paths - Fix to use proper absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'Data')
DATA_FILE = os.path.join(DATA_DIR, 'combined_data.csv')
RESULTS_DIR = os.path.join(BASE_DIR, 'DataAnalysis', 'results')
VISUALIZATIONS_DIR = os.path.join(RESULTS_DIR, 'visualizations')

def setup_directories():
    """Create necessary directories if they don't exist"""
    directories = [DATA_DIR, RESULTS_DIR, VISUALIZATIONS_DIR]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")

def verify_data_file():
    """Verify data file exists and is accessible"""
    if not os.path.exists(DATA_FILE):
        logger.error(f"Data file not found at: {DATA_FILE}")
        logger.info(f"Please ensure combined_data.csv exists in {DATA_DIR}")
        logger.info("Current directory structure should be:")
        logger.info(f"E:\ML\Data\combined_data.csv")
        return False
    return True

class ComplaintAnalysisSystem:
    def __init__(self, df):
        logger.info("Initializing Complaint Analysis System")
        self.df = df.copy()
        self.preprocess_data()
        
    def preprocess_data(self):
        logger.info("Preprocessing data...")
        # Convert date columns to datetime
        date_columns = ['CreatedAt', 'lastUpdatedDate', 'date', 'submissionDate', 'updatedAt']
        for col in date_columns:
            if (col in self.df.columns):
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
        
        # Calculate resolution time in days
        self.df['resolution_days'] = (pd.to_datetime(self.df['lastUpdatedDate']) - 
                                    pd.to_datetime(self.df['CreatedAt'])).dt.days
        
        # Extract month and year for temporal analysis
        self.df['month_year'] = self.df['CreatedAt'].dt.to_period('M')
        
    def analyze_complaint_volumes(self):
        logger.info("Analyzing complaint volumes...")
        # Complaint volume over time
        monthly_complaints = self.df.groupby('month_year').size()
        
        # Category distribution
        category_dist = self.df['category'].value_counts()
        
        # Status distribution
        status_dist = self.df['status'].value_counts()
        
        # Urgency level analysis
        urgency_dist = self.df['urgencyLevel'].value_counts()
        
        return {
            'monthly_complaints': monthly_complaints,
            'category_dist': category_dist,
            'status_dist': status_dist,
            'urgency_dist': urgency_dist
        }
    
    def analyze_impact_metrics(self):
        logger.info("Analyzing impact metrics...")
        # Analysis of different impact types
        impact_analysis = {
            'economic': self.df['economicImpact'].value_counts(),
            'environmental': self.df['environmentalImpact'].value_counts(),
            'social': self.df['socialImpact'].value_counts()
        }
        
        return impact_analysis
    
    def analyze_resolution_time(self):
        logger.info("Analyzing resolution times...")
        # Average resolution time by category
        avg_resolution = self.df.groupby('category')['resolution_days'].mean()
        
        # Resolution time distribution
        resolution_dist = self.df['resolution_days'].describe()
        
        return {
            'avg_resolution_by_category': avg_resolution,
            'resolution_distribution': resolution_dist
        }
    
    def create_geographic_visualization(self):
        logger.info("Creating geographic visualization...")
        # Create a map centered on the mean coordinates
        center_lat = self.df['gpscoordinates_latitude'].mean()
        center_lon = self.df['gpscoordinates_longitude'].mean()
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
        
        # Add markers for each complaint
        for idx, row in self.df.iterrows():
            folium.Marker(
                location=[row['gpscoordinates_latitude'], row['gpscoordinates_longitude']],
                popup=f"Complaint: {row['complaint_type']}<br>Status: {row['status']}"
            ).add_to(m)
            
        return m
    
    def perform_sentiment_analysis(self):
        logger.info("Performing sentiment analysis...")
        # Use TextBlob for sentiment analysis of complaints
        self.df['sentiment'] = self.df['complaint'].apply(
            lambda x: TextBlob(str(x)).sentiment.polarity
        )
        
        sentiment_summary = {
            'average_sentiment': self.df['sentiment'].mean(),
            'sentiment_distribution': self.df['sentiment'].value_counts(bins=5)
        }
        
        return sentiment_summary
    
    def predict_future_volumes(self, months_ahead=3):
        """Predict future complaint volumes with better handling of limited data"""
        logger.info("Predicting future volumes...")
        
        try:
            # Get historical monthly counts
            monthly_counts = self.df.groupby('month_year').size()
            num_months = len(monthly_counts)
            
            logger.info(f"Historical data spans {num_months} months")
            
            if num_months == 0:
                logger.warning("No historical data available")
                return [0] * months_ahead
                
            if num_months == 1:
                logger.warning("Only one month of data available, using as baseline")
                baseline = monthly_counts.iloc[0]
                return [baseline] * months_ahead
            
            # Use available data to calculate trend
            lookback = min(num_months - 1, 12)  # Use up to 12 months of history
            recent_data = monthly_counts.iloc[-lookback:]
            
            # Calculate trend using simple linear regression
            x = np.arange(len(recent_data))
            y = recent_data.values
            z = np.polyfit(x, y, 1)
            slope = z[0]
            
            # Calculate baseline from recent average
            baseline = recent_data.mean()
            
            logger.info(f"Using {lookback} months of historical data")
            logger.info(f"Baseline: {baseline:.2f} complaints/month")
            logger.info(f"Trend: {slope:.2f} complaints/month")
            
            # Generate predictions
            predictions = []
            for i in range(months_ahead):
                predicted = max(0, baseline + (slope * (i + 1)))  # Ensure non-negative
                predictions.append(predicted)
                
            return predictions
            
        except Exception as e:
            logger.error(f"Error in prediction: {str(e)}")
            logger.info("Falling back to simple average prediction")
            # Fallback to simple average if anything goes wrong
            avg_complaints = self.df.groupby('month_year').size().mean()
            return [avg_complaints] * months_ahead
    
    def generate_recommendations(self):
        logger.info("Generating recommendations...")
        # Analyze patterns to generate recommendations
        high_volume_categories = self.df['category'].value_counts().head()
        long_resolution_categories = (
            self.df.groupby('category')['resolution_days']
            .mean()
            .sort_values(ascending=False)
            .head()
        )
        
        recommendations = {
            'process_improvements': [
                f"Focus on {cat} which has high complaint volume" 
                for cat in high_volume_categories.index
            ],
            'resource_allocation': [
                f"Allocate more resources to {cat} to improve resolution time" 
                for cat in long_resolution_categories.index
            ],
            'preventive_measures': []
        }
        
        return recommendations

def create_visualizations(volume_analysis):
    logger.info("Creating visualizations...")
    # Monthly trend
    fig_monthly = px.line(
        x=volume_analysis['monthly_complaints'].index.astype(str),
        y=volume_analysis['monthly_complaints'].values,
        title='Monthly Complaint Volumes'
    )
    
    # Category distribution
    fig_categories = px.bar(
        x=volume_analysis['category_dist'].index,
        y=volume_analysis['category_dist'].values,
        title='Complaints by Category'
    )
    
    return fig_monthly, fig_categories

def save_results(results_dict, df_length):
    logger.info("Saving analysis results...")
    results_file = os.path.join(RESULTS_DIR, 'analysis_results.txt')
    
    with open(results_file, 'w', encoding='utf-8') as f:
        f.write("Complaint Analysis Results\n")
        f.write("========================\n\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Complaints Analyzed: {df_length}\n\n")
        
        for key, value in results_dict.items():
            f.write(f"\n{key.replace('_', ' ').title()}\n")
            f.write("-" * len(key) + "\n")
            f.write(str(value))
            f.write("\n")

def main():
    try:
        logger.info("Starting Complaint Analysis System")
        
        # Setup directories
        setup_directories()
        
        # Verify data file exists
        if not verify_data_file():
            return
            
        # Read data
        logger.info(f"Loading data from {DATA_FILE}")
        df = pd.read_csv(DATA_FILE)
        
        if len(df) == 0:
            logger.error("Data file is empty")
            return
            
        logger.info(f"Successfully loaded {len(df)} records")
        
        # Initialize analysis system and perform analyses
        analysis_system = ComplaintAnalysisSystem(df)
        
        # Collect all analysis results
        results = {
            'volume_analysis': analysis_system.analyze_complaint_volumes(),
            'impact_analysis': analysis_system.analyze_impact_metrics(),
            'resolution_analysis': analysis_system.analyze_resolution_time(),
            'sentiment_analysis': analysis_system.perform_sentiment_analysis(),
            'future_predictions': analysis_system.predict_future_volumes(),
            'recommendations': analysis_system.generate_recommendations()
        }
        
        # Create visualizations
        fig_monthly, fig_categories = create_visualizations(results['volume_analysis'])
        map_viz = analysis_system.create_geographic_visualization()
        
        # Save results
        save_results(results, len(df))
        
        # Save visualizations
        logger.info("Saving visualizations...")
        fig_monthly.write_html(os.path.join(VISUALIZATIONS_DIR, 'monthly_trend.html'))
        fig_categories.write_html(os.path.join(VISUALIZATIONS_DIR, 'category_distribution.html'))
        map_viz.save(os.path.join(VISUALIZATIONS_DIR, 'geographic_distribution.html'))
        
        logger.info("Analysis completed successfully")
        logger.info(f"Results directory: {RESULTS_DIR}")
        logger.info(f"Visualizations directory: {VISUALIZATIONS_DIR}")
        
        return results
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        logger.error(traceback.format_exc())
        return None

if __name__ == "__main__":
    main()