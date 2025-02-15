from transformers import pipeline
import pandas as pd
from tqdm import tqdm

class CategorySummarizer:
    def __init__(self):
        try:
            # Initialize BART summarizer
            print("Loading summarization model...")
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                max_length=150,
                min_length=50
            )
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error initializing model: {e}")
            raise

    def summarize_category(self, grievances):
        """Summarize grievances for a category"""
        try:
            # Filter out empty complaints
            valid_grievances = [g for g in grievances if pd.notna(g.get('complaint', ''))]
            
            if not valid_grievances:
                return "No valid complaints found for summarization"
            
            # Combine all complaints in the category
            combined_text = "\n\n".join([
                f"Complaint: {g['complaint']}\n"
                f"District: {g.get('district', 'Unknown')}\n"
                f"Status: {g.get('status', 'Unknown')}\n"
                f"Emotion: {g.get('emotion', 'Unknown')}"
                for g in valid_grievances
            ])
            
            # Generate summary
            if len(combined_text) > 0:
                summary = self.summarizer(combined_text, truncation=True)[0]['summary_text']
                return summary
            return "No text available for summarization"
            
        except Exception as e:
            print(f"Error summarizing: {e}")
            return "Error generating summary"

def analyze_categories(df, max_samples=20):
    """Analyze complaints by category"""
    print("Initializing summarizer...")
    summarizer = CategorySummarizer()
    
    # Take first N samples
    print(f"Taking first {max_samples} samples...")
    df_sample = df.head(max_samples)
    
    categories = {}
    print("Analyzing categories...")
    
    # Group by category
    for category in df_sample['category'].unique():
        if pd.isna(category):
            continue
            
        print(f"\nProcessing category: {category}")
        # Get grievances for this category
        category_df = df_sample[df_sample['category'] == category]
        grievances = category_df.to_dict('records')
        
        # Get category summary
        print(f"Generating summary for {len(grievances)} grievances...")
        summary = summarizer.summarize_category(grievances)
        
        # Calculate metrics
        categories[category] = {
            'total_grievances': len(grievances),
            'summary': summary,
            'metrics': {
                'avg_resolution_time': category_df['ResolutionTime'].mean(),
                'districts': category_df['district'].unique().tolist(),
                'common_emotions': category_df['emotion'].value_counts().to_dict(),
                'statuses': category_df['status'].value_counts().to_dict()
            }
        }
    
    return categories

def generate_report(categories):
    """Generate summary report"""
    report = ["CATEGORY ANALYSIS REPORT (First 20 Grievances)\n" + "="*50 + "\n"]
    
    for category, data in categories.items():
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
        
        report.append(section)
    
    return "\n\n".join(report)

def main():
    try:
        # Load data
        print("Loading grievance data...")
        df = pd.read_csv('E:/ML/Data/combined_data.csv')
        print(f"Loaded {len(df)} records")
        
        # Analyze categories
        print("\nAnalyzing categories...")
        categories = analyze_categories(df, max_samples=20)
        
        # Generate report
        print("\nGenerating report...")
        report = generate_report(categories)
        
        # Save report
        output_path = 'E:/ML/GriviencSummarization/category_summaries.txt'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\nAnalysis complete! Check {output_path} for category summaries")
        
    except Exception as e:
        print(f"Error in main execution: {e}")

if __name__ == "__main__":
    main()
