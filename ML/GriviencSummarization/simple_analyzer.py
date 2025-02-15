from transformers import pipeline
import pandas as pd
import numpy as np
from collections import defaultdict

class SimpleGrievanceAnalyzer:
    def __init__(self):
        # Using simpler BART model that doesn't require sentencepiece
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def summarize_text(self, text):
        """Generate summary for given text"""
        try:
            summary = self.summarizer(text, max_length=130, min_length=30)[0]['summary_text']
            return summary
        except Exception as e:
            print(f"Error in summarization: {e}")
            return text[:100] + "..."

    def analyze_sample(self, df, sample_size=20):
        """Analyze first N grievances by category"""
        # Take first N rows
        sample_df = df.head(sample_size)
        
        # Group by category
        grouped = sample_df.groupby('category')
        
        analyses = {}
        
        for category, group in grouped:
            if pd.isna(category):
                continue
                
            grievances = group.to_dict('records')
            
            # Combine complaints for this category
            complaints_text = "\n".join([
                f"Complaint: {g['complaint']}\n"
                f"Location: {g['location']}\n"
                f"Impact: {g['economicImpact']}, {g['socialImpact']}, {g['environmentalImpact']}\n"
                for g in grievances
            ])
            
            # Generate category summary
            summary = self.summarize_text(complaints_text)
            
            # Calculate metrics
            analyses[category] = {
                'total_grievances': len(grievances),
                'summary': summary,
                'grievances': grievances,
                'metrics': {
                    'avg_resolution_time': group['ResolutionTime'].mean(),
                    'common_emotions': group['emotion'].value_counts().to_dict(),
                    'districts': group['district'].unique().tolist(),
                    'statuses': group['status'].value_counts().to_dict()
                }
            }
        
        return analyses

def generate_sample_report(analyses):
    """Generate detailed report for sample analysis"""
    report = ["SAMPLE ANALYSIS REPORT (First 20 Grievances)\n" + "="*50 + "\n"]
    
    for category, data in analyses.items():
        section = f"""
Category: {category}
{'-'*40}
Total Grievances: {data['total_grievances']}
Average Resolution Time: {data['metrics']['avg_resolution_time']:.2f} days

Districts Affected: {', '.join(data['metrics']['districts'])}

Status Distribution:
{'-'*20}
""" + "\n".join([f"- {status}: {count}" 
                 for status, count in data['metrics']['statuses'].items()])
        
        section += f"\n\nCommon Emotions:\n{'-'*20}\n"
        section += "\n".join([f"- {emotion}: {count}" 
                           for emotion, count in data['metrics']['common_emotions'].items()])
        
        section += f"\n\nCategory Summary:\n{'-'*20}\n{data['summary']}\n"
        
        # Add individual grievances
        section += "\nIndividual Complaints:\n" + "-"*20
        for i, g in enumerate(data['grievances'], 1):
            section += f"""
Grievance {i}:
Location: {g['location']}
Complaint: {g['complaint']}
Status: {g['status']}
"""
        
        report.append(section)
    
    return "\n\n".join(report)

def main():
    # Load data
    print("Loading grievance data...")
    df = pd.read_csv('E:/ML/Data/combined_data.csv')
    
    # Initialize analyzer
    print("Initializing analyzer...")
    analyzer = SimpleGrievanceAnalyzer()
    
    # Analyze sample
    print("Analyzing first 20 grievances...")
    analyses = analyzer.analyze_sample(df, sample_size=20)
    
    # Generate report
    print("Generating sample analysis report...")
    report = generate_sample_report(analyses)
    
    # Save report
    output_path = 'E:/ML/GriviencSummarization/sample_analysis_report.txt'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nAnalysis complete! Check {output_path} for detailed analysis")

if __name__ == "__main__":
    main()
