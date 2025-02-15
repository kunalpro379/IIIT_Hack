import pandas as pd
import numpy as np
from transformers import pipeline
import openai
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Load the data
df = pd.read_csv('/e:/ML/DataAnalysis/combined_data.csv')
df['CreatedAt'] = pd.to_datetime(df['CreatedAt'])

# Initialize sentiment analyzer
sentiment_analyzer = pipeline('sentiment-analysis')

def analyze_complaint_patterns():
    """Analyze patterns in complaints to identify systemic issues"""
    pattern_analysis = {
        'district_stats': df.groupby('district').agg({
            'id': 'count',
            'ResolutionTime': 'mean',
            'urgencyLevel': lambda x: (x == 'High').mean()
        }).to_dict(),
        'category_growth': df.groupby(['category', df['CreatedAt'].dt.month]).size().unstack().pct_change(axis=1).mean().to_dict(),
        'impact_distribution': {
            'economic': df['economicImpact'].value_counts().to_dict(),
            'environmental': df['environmentalImpact'].value_counts().to_dict(),
            'social': df['socialImpact'].value_counts().to_dict()
        }
    }
    return pattern_analysis

def analyze_department_performance():
    """Analyze department performance metrics"""
    dept_analysis = df.groupby('departmentAssigned').agg({
        'id': 'count',
        'ResolutionTime': ['mean', 'std'],
        'status': lambda x: (x == 'Closed').mean()
    }).round(2).to_dict()
    return dept_analysis

def generate_policy_recommendations():
    """Generate policy recommendations using GPT-4"""
    # Get analyses
    patterns = analyze_complaint_patterns()
    dept_performance = analyze_department_performance()
    
    prompt = f"""
    As a policy advisor, analyze this government complaint data and recommend policy changes:

    Complaint Patterns:
    {json.dumps(patterns, indent=2)}

    Department Performance:
    {json.dumps(dept_performance, indent=2)}

    Provide detailed recommendations for:
    1. Immediate policy changes needed
    2. Long-term strategic policies
    3. Department-specific improvements
    4. Resource allocation suggestions
    5. Preventive measures
    6. Monitoring mechanisms
    7. Implementation timeline
    8. Expected outcomes
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def analyze_policy_impact(policy_area):
    """Analyze potential impact of policy changes"""
    area_data = df[df['category'] == policy_area]
    
    impact_summary = {
        'complaint_volume': len(area_data),
        'avg_resolution_time': area_data['ResolutionTime'].mean(),
        'high_urgency_percentage': (area_data['urgencyLevel'] == 'High').mean() * 100,
        'economic_impact': area_data['economicImpact'].value_counts().to_dict(),
        'social_impact': area_data['socialImpact'].value_counts().to_dict()
    }
    
    prompt = f"""
    Analyze the potential impact of policy changes in {policy_area}:
    {json.dumps(impact_summary, indent=2)}
    
    Provide:
    1. Expected benefits
    2. Potential challenges
    3. Implementation costs
    4. Timeline for results
    5. Success metrics
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def generate_district_recommendations():
    """Generate district-specific policy recommendations"""
    district_recommendations = {}
    
    for district in df['district'].unique():
        district_data = df[df['district'] == district]
        
        summary = {
            'total_complaints': len(district_data),
            'major_categories': district_data['category'].value_counts().head(3).to_dict(),
            'avg_resolution_time': district_data['ResolutionTime'].mean(),
            'high_urgency_percent': (district_data['urgencyLevel'] == 'High').mean() * 100
        }
        
        prompt = f"""
        Recommend specific policies for {district} district based on this data:
        {json.dumps(summary, indent=2)}
        
        Focus on:
        1. District-specific issues
        2. Local resource allocation
        3. Implementation strategies
        4. Success metrics
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        district_recommendations[district] = response.choices[0].message.content
    
    return district_recommendations

def create_policy_report():
    """Create comprehensive policy recommendation report"""
    # Generate all recommendations
    general_recommendations = generate_policy_recommendations()
    district_recommendations = generate_district_recommendations()
    
    # Generate visualization of complaint patterns
    fig = px.treemap(df, 
                     path=['district', 'category'],
                     values='ResolutionTime',
                     title='Complaint Distribution and Resolution Time by District and Category')
    fig.write_html('/e:/ML/Analysis/complaint_distribution.html')
    
    # Save comprehensive report
    report_path = '/e:/ML/Analysis/policy_recommendations.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Government Policy Recommendations Report\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d')}\n\n")
        
        f.write("## Executive Summary\n")
        f.write(general_recommendations + "\n\n")
        
        f.write("## District-Specific Recommendations\n")
        for district, recommendations in district_recommendations.items():
            f.write(f"### {district}\n")
            f.write(recommendations + "\n\n")
        
        # Generate implementation roadmap
        roadmap_prompt = """
        Create a detailed implementation roadmap for the recommended policies, including:
        1. Priority order
        2. Timeline
        3. Resource requirements
        4. Success metrics
        5. Monitoring mechanisms
        """
        
        roadmap_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": roadmap_prompt}]
        )
        
        f.write("## Implementation Roadmap\n")
        f.write(roadmap_response.choices[0].message.content)
    
    return report_path

if __name__ == "__main__":
    print("Starting policy analysis...")
    report_path = create_policy_report()
    print(f"Analysis completed! Check {report_path} for detailed recommendations.")
