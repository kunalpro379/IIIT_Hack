import pandas as pd
from multilingual_summarizer import MultilingualGrievanceAnalyzer
from analyze_grievances import visualize_category_metrics
from collections import defaultdict

def analyze_sample_grievances(df, sample_size=20):
    """Analyze first N grievances"""
    # Take first N rows
    sample_df = df.head(sample_size)
    
    # Initialize analyzer
    analyzer = MultilingualGrievanceAnalyzer()
    
    # Group by category
    grouped = sample_df.groupby('category')
    
    category_analyses = {}
    
    for category, group in grouped:
        if pd.isna(category):
            continue
            
        grievances = group.to_dict('records')
        
        # Generate summary for this category
        summary = analyzer.analyze_category(grievances)
        
        # Store metrics
        category_analyses[category] = {
            'total_grievances': len(grievances),
            'summary': summary,
            'grievances': grievances,
            'emotions': group['emotion'].value_counts().to_dict(),
            'districts': group['district'].nunique(),
            'avg_resolution_time': group['ResolutionTime'].mean(),
            'impacts': {
                'economic': group['economicImpact'].value_counts().to_dict(),
                'social': group['socialImpact'].value_counts().to_dict(),
                'environmental': group['environmentalImpact'].value_counts().to_dict()
            }
        }
    
    return category_analyses

def generate_sample_report(analyses):
    """Generate detailed report for sample analysis"""
    report = ["SAMPLE ANALYSIS REPORT (First 20 Grievances)\n" + "="*50 + "\n"]
    
    for category, data in analyses.items():
        section = f"""
Category: {category}
{'-'*40}
Total Grievances: {data['total_grievances']}
Districts Affected: {data['districts']}
Average Resolution Time: {data['avg_resolution_time']:.2f} days

Emotional Analysis:
{'-'*20}
""" + "\n".join([f"- {emotion}: {count}" for emotion, count in data['emotions'].items()])

        section += "\n\nImpact Analysis:"
        for impact_type, impacts in data['impacts'].items():
            if impacts:
                section += f"\n{impact_type.title()}:"
                for impact, count in impacts.items():
                    section += f"\n- {impact}: {count}"

        section += f"\n\nCategory Summary:\n{'-'*20}\n{data['summary']}\n"
        
        # Add individual grievances
        section += "\nIndividual Grievances:\n" + "-"*20
        for i, grievance in enumerate(data['grievances'], 1):
            section += f"""
Grievance {i}:
Location: {grievance['location']}
Complaint: {grievance['complaint']}
Status: {grievance['status']}
"""
        
        report.append(section)
    
    return "\n\n".join(report)

def main():
    # Load data
    print("Loading grievance data...")
    df = pd.read_csv('E:/ML/Data/combined_data.csv')
    
    # Analyze sample
    print("Analyzing first 20 grievances...")
    analyses = analyze_sample_grievances(df, sample_size=20)
    
    # Generate report
    print("Generating sample analysis report...")
    report = generate_sample_report(analyses)
    
    # Save report
    output_path = 'E:/ML/GriviencSummarization/sample_analysis_report.txt'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nSample analysis complete! Check {output_path} for detailed analysis")

if __name__ == "__main__":
    main()
