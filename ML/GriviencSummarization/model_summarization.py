import torch
from transformers import (
    BartForConditionalGeneration, 
    BartTokenizer,
    pipeline
)
import pandas as pd
from tqdm import tqdm

class GrievanceSummarizer:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_name = "facebook/bart-large-cnn"
        self._initialize_model()

    def _initialize_model(self):
        self.tokenizer = BartTokenizer.from_pretrained(self.model_name)
        self.model = BartForConditionalGeneration.from_pretrained(self.model_name).to(self.device)
        # Create summarization pipeline
        self.summarizer = pipeline(
            "summarization", 
            model=self.model_name, 
            tokenizer=self.tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )

    def summarize_text(self, text, max_length=150, min_length=30):
        try:
            summary = self.summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )[0]['summary_text']
            return summary
        except Exception as e:
            print(f"Error summarizing text: {e}")
            return text[:max_length] + "..."

class GrievanceAnalyzer:
    def __init__(self):
        self.summarizer = GrievanceSummarizer()

    def prepare_text_for_summarization(self, row):
        """Prepare a structured text from row data"""
        text = f"""
        Category: {row['category']}
        Location: {row['location']}
        Complaint: {row['complaint']}
        Impact: Economic - {row['economicImpact']}, Social - {row['socialImpact']}, Environmental - {row['environmentalImpact']}
        Status: {row['status']}
        Urgency: {row['urgencyLevel']}
        Emotion: {row['emotion']}
        """
        return text.strip()

    def analyze_grievance(self, text):
        """Generate summary using BART model"""
        return {'BART': self.summarizer.summarize_text(text)}

    def analyze_category_data(self, df, category):
        """Analyze all grievances in a specific category"""
        category_data = df[df['category'] == category]
        summaries = []
        
        for _, row in tqdm(category_data.iterrows(), desc=f"Analyzing {category}"):
            text = self.prepare_text_for_summarization(row)
            summary = self.analyze_grievance(text)
            summaries.append(summary)
            
        return summaries

def main():
    # Load data
    df = pd.read_csv('E:/ML/Data/combined_data.csv')
    
    # Initialize analyzer
    analyzer = GrievanceAnalyzer()
    
    # Analyze each category
    categories = df['category'].unique()
    all_summaries = {}
    
    for category in categories:
        if pd.notna(category):
            print(f"\nAnalyzing category: {category}")
            summaries = analyzer.analyze_category_data(df, category)
            all_summaries[category] = summaries
            
            # Save category summaries
            with open(f'E:/ML/GriviencSummarization/summaries_{category.lower()}.txt', 'w', encoding='utf-8') as f:
                f.write(f"Category: {category}\n")
                f.write("="*50 + "\n\n")
                
                for i, summary in enumerate(summaries, 1):
                    f.write(f"Grievance {i}:\n")
                    f.write("-"*30 + "\n")
                    f.write(f"BART Summary: {summary['BART']}\n\n")

if __name__ == "__main__":
    main()
