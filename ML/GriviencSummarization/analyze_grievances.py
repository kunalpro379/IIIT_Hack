import pandas as pd
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from multilingual_summarizer import MultilingualGrievanceAnalyzer

def load_and_preprocess_data():
    """Load and preprocess the grievance data"""
    df = pd.read_csv('E:/ML/Data/combined_data.csv')
    return df

def analyze_categories(df):
    """Analyze each grievance category in detail"""
    category_summary = defaultdict(lambda: {
        'count': 0,
        'districts': defaultdict(int),
        'status': defaultdict(int),
        'impact_analysis': {
            'economic': defaultdict(int),
            'social': defaultdict(int),
            'environmental': defaultdict(int)
        },
        'avg_resolution_time': [],
        'urgency_levels': defaultdict(int),
        'emotions': defaultdict(int)
    })

    # Initialize multilingual analyzer
    analyzer = MultilingualGrievanceAnalyzer()
    
    # Group grievances by category
    grouped_grievances = df.groupby('category')
    
    for category, group in grouped_grievances:
        if pd.isna(category):
            continue
            
        # Get category summary
        grievances = group.to_dict('records')
        summary = analyzer.analyze_category(grievances)
        category_summary[category]['summary'] = summary
        
        # Update basic counts
        category_summary[category]['count'] += len(grievances)
        
        for row in grievances:
            # Track district distribution
            district = row['district'] if pd.notna(row['district']) else 'Unknown'
            category_summary[category]['districts'][district] += 1
            
            # Track status
            status = row['status'] if pd.notna(row['status']) else 'Unknown'
            category_summary[category]['status'][status] += 1
            
            # Track impacts
            if pd.notna(row['economicImpact']):
                category_summary[category]['impact_analysis']['economic'][row['economicImpact']] += 1
            if pd.notna(row['socialImpact']):
                category_summary[category]['impact_analysis']['social'][row['socialImpact']] += 1
            if pd.notna(row['environmentalImpact']):
                category_summary[category]['impact_analysis']['environmental'][row['environmentalImpact']] += 1
            
            # Track resolution time
            if pd.notna(row['ResolutionTime']):
                category_summary[category]['avg_resolution_time'].append(row['ResolutionTime'])
                
            # Track urgency levels
            if pd.notna(row['urgencyLevel']):
                category_summary[category]['urgency_levels'][row['urgencyLevel']] += 1
                
            # Track emotions
            if pd.notna(row['emotion']):
                category_summary[category]['emotions'][row['emotion']] += 1

    return category_summary

def generate_detailed_report(category_summary):
    """Generate a detailed report for each category"""
    report = []
    
    for category, data in category_summary.items():
        # Calculate metrics
        total_grievances = data['count']
        avg_resolution = np.mean(data['avg_resolution_time']) if data['avg_resolution_time'] else 0
        most_affected_district = max(data['districts'].items(), key=lambda x: x[1])[0]
        primary_status = max(data['status'].items(), key=lambda x: x[1])[0]
        
        # Format the category report
        category_report = f"""
        Category: {category}
        {'='*50}
        Total Grievances: {total_grievances}
        Average Resolution Time: {avg_resolution:.2f} days
        
        Geographic Distribution:
        - Most Affected District: {most_affected_district}
        - Total Districts Affected: {len(data['districts'])}
        
        Status Breakdown:
        {'-'*20}
        """ + '\n'.join([f"- {status}: {count}" for status, count in data['status'].items()])
        
        # Add impact analysis
        category_report += "\n\nImpact Analysis:"
        for impact_type, impacts in data['impact_analysis'].items():
            if impacts:
                primary_impact = max(impacts.items(), key=lambda x: x[1])[0]
                category_report += f"\n{impact_type.title()}: Primary - {primary_impact}"
        
        # Add urgency and emotion analysis
        if data['urgency_levels']:
            primary_urgency = max(data['urgency_levels'].items(), key=lambda x: x[1])[0]
            category_report += f"\n\nPrimary Urgency Level: {primary_urgency}"
        
        if data['emotions']:
            primary_emotion = max(data['emotions'].items(), key=lambda x: x[1])[0]
            category_report += f"\nPredominant Emotion: {primary_emotion}"
        
        # Add model summaries to report
        if 'summary' in data:
            category_report += f"\n\nMultilingual Summary: {data['summary']}"
        
        report.append(category_report)
    
    return '\n\n'.join(report)

def visualize_category_metrics(category_summary):
    """Create visualizations for category metrics"""
    # Prepare data for plotting
    categories = list(category_summary.keys())
    counts = [data['count'] for data in category_summary.values()]
    
    # Create category distribution plot
    plt.figure(figsize=(15, 8))
    plt.bar(categories, counts)
    plt.xticks(rotation=45, ha='right')
    plt.title('Distribution of Grievance Categories')
    plt.ylabel('Number of Grievances')
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('E:/ML/GriviencSummarization/category_distribution.png')
    plt.close()

def main():
    print("Loading data...")
    df = load_and_preprocess_data()
    
    print("Analyzing categories...")
    category_summary = analyze_categories(df)
    
    print("Generating detailed report...")
    report = generate_detailed_report(category_summary)
    
    # Save the report
    with open('E:/ML/GriviencSummarization/grievance_analysis_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("Generating visualizations...")
    visualize_category_metrics(category_summary)
    
    print("\nAnalysis complete! Check the following files:")
    print("1. grievance_analysis_report.txt - Detailed category analysis")
    print("2. category_distribution.png - Visual distribution of categories")

if __name__ == "__main__":
    main()
