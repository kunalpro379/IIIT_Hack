from transformers import AutoTokenizer, AutoModelForSeq2SeqGeneration
import torch
import pandas as pd
from tqdm import tqdm

class MultilingualGrievanceAnalyzer:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Use mBART which doesn't require sentencepiece
        self.model_name = "facebook/mbart-large-50-many-to-many-mmt"
        self._initialize_model()

    def _initialize_model(self):
        """Initialize multilingual BART model"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqGeneration.from_pretrained(self.model_name).to(self.device)
            print("Model initialized successfully!")
        except Exception as e:
            print(f"Error initializing model: {e}")
            raise

    def summarize_text(self, text, max_length=150, min_length=50):
        """Generate summary for given text"""
        try:
            # Handle mixed language input (Hindi/English)
            inputs = self.tokenizer(text, return_tensors="pt", max_length=1024, 
                                  truncation=True, padding='max_length').to(self.device)
            
            summary_ids = self.model.generate(
                inputs["input_ids"],
                max_length=max_length,
                min_length=min_length,
                num_beams=4,
                length_penalty=2.0,
                early_stopping=True,
                no_repeat_ngram_size=2
            )
            
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            return summary
        except Exception as e:
            print(f"Error in summarization: {e}")
            return text[:max_length] + "..."

    def analyze_category(self, grievances):
        """Analyze all grievances in a category and generate comprehensive summary"""
        try:
            # Combine all grievances with better structure
            combined_text = "\n".join([
                f"Grievance Details:\n"
                f"Complaint: {g.get('complaint', 'N/A')}\n"
                f"Location: {g.get('location', 'N/A')}\n"
                f"Impact: Economic - {g.get('economicImpact', 'N/A')}, "
                f"Social - {g.get('socialImpact', 'N/A')}, "
                f"Environmental - {g.get('environmentalImpact', 'N/A')}\n"
                f"Status: {g.get('status', 'N/A')}\n"
                f"Emotion: {g.get('emotion', 'N/A')}\n"
                f"Resolution Time: {g.get('ResolutionTime', 'N/A')} days\n"
                for g in grievances
            ])
            
            # Generate category summary
            summary = self.summarize_text(combined_text)
            return summary
        except Exception as e:
            print(f"Error in category analysis: {e}")
            return "Error generating summary"

def process_grievances(df):
    """Process and analyze grievances by category"""
    analyzer = MultilingualGrievanceAnalyzer()
    categories = df['category'].unique()
    
    category_analyses = {}
    
    for category in tqdm(categories, desc="Analyzing categories"):
        if pd.isna(category):
            continue
            
        # Get all grievances for this category
        category_df = df[df['category'] == category]
        grievances = category_df.to_dict('records')
        
        # Generate category summary
        summary = analyzer.analyze_category(grievances)
        
        # Store analysis
        category_analyses[category] = {
            'total_grievances': len(grievances),
            'summary': summary,
            'common_emotions': category_df['emotion'].value_counts().to_dict(),
            'districts_affected': category_df['district'].nunique(),
            'avg_resolution_time': category_df['ResolutionTime'].mean()
        }
    
    return category_analyses

def generate_report(analyses):
    """Generate detailed report for all categories"""
    report = []
    
    for category, analysis in analyses.items():
        report.append(f"""
Category: {category}
{'='*50}
Total Grievances: {analysis['total_grievances']}
Districts Affected: {analysis['districts_affected']}
Average Resolution Time: {analysis['avg_resolution_time']:.2f} days

Common Emotions:
{'-'*20}
""" + "\n".join([f"- {emotion}: {count}" 
                 for emotion, count in analysis['common_emotions'].items()]))
        
        report.append(f"""
Summary Analysis:
{'-'*20}
{analysis['summary']}

""")
    
    return "\n".join(report)

def main():
    # Load data
    print("Loading grievance data...")
    df = pd.read_csv('E:/ML/Data/combined_data.csv')
    
    # Process grievances
    print("Analyzing grievances by category...")
    analyses = process_grievances(df)
    
    # Generate and save report
    print("Generating comprehensive report...")
    report = generate_report(analyses)
    
    with open('E:/ML/GriviencSummarization/category_analysis_report.txt', 'w', 
              encoding='utf-8') as f:
        f.write(report)
    
    print("Analysis complete! Check category_analysis_report.txt for detailed analysis")

if __name__ == "__main__":
    main()
