import pandas as pd
import numpy as np
import openai
from datetime import datetime
import json
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('/e:/ML/DataAnalysis/combined_data.csv')

# Configure OpenAI API (replace with your key)
openai.api_key = 'your-api-key-here'

def analyze_impact_category(data, impact_type):
    """Analyze specific impact category using GPT"""
    impact_summary = data[impact_type].value_counts().to_dict()
    prompt = f"""
    Analyze this impact distribution for {impact_type} in government complaints:
    {impact_summary}
    
    Provide:
    1. Key insights
    2. Main challenges
    3. Recommendations for improvement
    4. Action items for concerned departments
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def generate_district_impact_report(data, district):
    """Generate district-specific impact report"""
    district_data = data[data['district'] == district]
    
    summary = {
        'total_complaints': len(district_data),
        'economic_impact': district_data['economicImpact'].value_counts().to_dict(),
        'environmental_impact': district_data['environmentalImpact'].value_counts().to_dict(),
        'social_impact': district_data['socialImpact'].value_counts().to_dict(),
        'top_categories': district_data['category'].value_counts().head(3).to_dict()
    }
    
    prompt = f"""
    Analyze this district's impact summary and provide recommendations:
    {json.dumps(summary, indent=2)}
    
    Provide:
    1. Overall impact assessment
    2. Critical areas needing immediate attention
    3. Specific recommendations for local authorities
    4. Long-term strategic suggestions
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def create_department_action_plan(data, department):
    """Generate department-specific action plan"""
    dept_data = data[data['departmentAssigned'] == department]
    
    summary = {
        'complaint_volume': len(dept_data),
        'avg_resolution_time': dept_data['ResolutionTime'].mean(),
        'urgent_cases': len(dept_data[dept_data['urgencyLevel'] == 'High']),
        'impact_distribution': {
            'economic': dept_data['economicImpact'].value_counts().to_dict(),
            'environmental': dept_data['environmentalImpact'].value_counts().to_dict(),
            'social': dept_data['socialImpact'].value_counts().to_dict()
        }
    }
    
    prompt = f"""
    Based on this department's performance metrics, suggest an action plan:
    {json.dumps(summary, indent=2)}
    
    Provide:
    1. Key performance insights
    2. Priority areas for improvement
    3. Resource allocation suggestions
    4. Timeline-based action items
    5. Monitoring metrics
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def generate_comprehensive_report():
    """Generate comprehensive impact analysis report"""
    
    # Analyze each impact type
    economic_analysis = analyze_impact_category(df, 'economicImpact')
    environmental_analysis = analyze_impact_category(df, 'environmentalImpact')
    social_analysis = analyze_impact_category(df, 'socialImpact')
    
    # Generate district reports for top 5 districts
    top_districts = df['district'].value_counts().head(5).index
    district_reports = {district: generate_district_impact_report(df, district) 
                       for district in top_districts}
    
    # Generate department action plans
    departments = df['departmentAssigned'].unique()
    department_plans = {dept: create_department_action_plan(df, dept) 
                       for dept in departments}
    
    # Save comprehensive report
    report_path = '/e:/ML/Analysis/impact_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Comprehensive Impact Analysis Report\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d')}\n\n")
        
        f.write("## Economic Impact Analysis\n")
        f.write(economic_analysis + "\n\n")
        
        f.write("## Environmental Impact Analysis\n")
        f.write(environmental_analysis + "\n\n")
        
        f.write("## Social Impact Analysis\n")
        f.write(social_analysis + "\n\n")
        
        f.write("## District-wise Analysis\n")
        for district, report in district_reports.items():
            f.write(f"### {district}\n")
            f.write(report + "\n\n")
        
        f.write("## Department Action Plans\n")
        for dept, plan in department_plans.items():
            f.write(f"### {dept}\n")
            f.write(plan + "\n\n")

    print(f"Comprehensive report generated at {report_path}")
    return report_path

if __name__ == "__main__":
    print("Starting Impact Analysis...")
    report_path = generate_comprehensive_report()
    print("Analysis completed!")
