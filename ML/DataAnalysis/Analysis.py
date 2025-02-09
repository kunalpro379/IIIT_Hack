def check_dependencies():
    required_packages = ['plotly', 'pandas', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
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
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError:
    print("Error: plotly package not found. Installing...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])
    import plotly.express as px
    import plotly as go
    from plotly.subplots import make_subplots

from datetime import datetime

def analyze_grievance_data(data_path):
    # Load and preprocess data
    df = pd.read_csv(data_path)
    
    # Convert date columns to datetime
    date_cols = ['CreatedAt', 'lastUpdatedDate', 'date', 'submissionDate', 'updatedAt']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    
    # Create figures for analysis
    figures = []
    
    try:
        # 1. District-wise Analysis
        district_counts = df['district'].value_counts().head(10)
        fig1 = px.bar(x=district_counts.index, y=district_counts.values,
                     title='Top 10 Districts by Number of Complaints',
                     labels={'x': 'District', 'y': 'Number of Complaints'})
        figures.append(fig1)
        
        # 2. Category Analysis
        category_counts = df['category'].value_counts()
        fig2 = px.pie(values=category_counts.values, names=category_counts.index,
                      title='Distribution of Complaints by Category')
        figures.append(fig2)
        
        # 3. Status Analysis
        status_counts = df['status'].value_counts()
        fig3 = px.pie(values=status_counts.values, names=status_counts.index,
                      title='Distribution of Complaint Status')
        figures.append(fig3)
        
        # 4. Resolution Time Analysis
        fig4 = px.box(df, y='ResolutionTime',
                      title='Resolution Time Distribution')
        figures.append(fig4)
        
        # 5. Urgency Level Analysis
        urgency_counts = df['urgencyLevel'].value_counts()
        fig5 = px.pie(values=urgency_counts.values, names=urgency_counts.index,
                      title='Distribution of Urgency Levels')
        figures.append(fig5)
        
        # 6. Time Series Analysis
        daily_counts = df.groupby(df['CreatedAt'].dt.date).size().reset_index()
        daily_counts.columns = ['Date', 'Count']
        fig6 = px.line(daily_counts, x='Date', y='Count',
                       title='Daily Complaint Trends')
        figures.append(fig6)
        
    except Exception as e:
        print(f"Error creating plots: {str(e)}")
        return None

    # Create HTML report
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Grievance Analysis Report</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <h1 style="text-align: center;">Grievance Analysis Report</h1>
    <div style="padding: 20px; background-color: #f5f5f5; margin: 20px;">
        <h2>Summary Statistics</h2>
        <p>Total Complaints: {total}</p>
        <p>Average Resolution Time: {avg_time:.2f} days</p>
        <p>Most Common Category: {top_category}</p>
        <p>Most Affected District: {top_district}</p>
        <p>Open Cases: {open_cases}</p>
        <p>High Priority Cases: {high_priority}</p>
    </div>""".format(
        total=len(df),
        avg_time=df['ResolutionTime'].mean(),
        top_category=category_counts.index[0],
        top_district=district_counts.index[0],
        open_cases=len(df[df['status'] == 'Open']),
        high_priority=len(df[df['urgencyLevel'] == 'High'])
    )
    
    # Add plots to HTML
    for fig in figures:
        html_content += f'<div style="margin: 20px 0;">{fig.to_html(full_html=False, include_plotlyjs=False)}</div>'
    
    html_content += "</body></html>"
    
    # Save report with proper error handling
    output_path = 'E:\\ML\\Data\\analysis_report.html'
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    except IOError as e:
        print(f"Error saving report: {str(e)}")
        print(f"Please ensure you have write permissions to {output_path}")
        return None

    print(f"Analysis report has been saved to {output_path}")
    
    # Generate summary statistics
    summary_stats = {
        'Total Complaints': len(df),
        'Average Resolution Time': f"{df['ResolutionTime'].mean():.2f} days",
        'Open Cases': len(df[df['status'] == 'Open']),
        'Closed Cases': len(df[df['status'] == 'Closed']),
        'High Priority Cases': len(df[df['urgencyLevel'] == 'High']),
        'Most Common Category': category_counts.index[0],
        'Most Affected District': district_counts.index[0]
    }
    
    return summary_stats

if __name__ == "__main__":
    try:
        # Path to your data file
        data_path = 'E:\\ML\\Data\\combined_data.csv'
        
        # Run analysis
        print("\nAnalyzing grievance data...")
        stats = analyze_grievance_data(data_path)
        
        # Print summary
        print("\nAnalysis Summary:")
        for key, value in stats.items():
            print(f"{key}: {value}")
            
        print("\nDetailed report has been generated. Please check the output HTML file.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Please ensure:")
        print("1. The data file exists at the specified path")
        print("2. You have necessary permissions to read/write files")
        print("3. Required Python packages are installed (pandas, plotly)")
