import pandas as pd
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import openai
from collections import defaultdict
import json
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN

# Load data
df = pd.read_csv('/e:/ML/DataAnalysis/combined_data.csv')

# Configure OpenAI API
openai.api_key = 'your-api-key-here'

# Load NLP models
nlp = spacy.load('en_core_web_sm')
sentiment_analyzer = pipeline('sentiment-analysis')

def extract_key_issues(complaints):
    """Extract key issues using spaCy NER"""
    key_issues = defaultdict(int)
    
    for complaint in complaints:
        doc = nlp(complaint)
        # Extract locations, problems, and entities
        for ent in doc.ents:
            if ent.label_ in ['GPE', 'LOC', 'PROBLEM']:
                key_issues[ent.text] += 1
    
    return dict(key_issues)

def analyze_complaint_cluster(complaints):
    """Analyze a cluster of similar complaints using GPT-4"""
    summary = {
        'complaint_count': len(complaints),
        'key_issues': extract_key_issues(complaints),
        'sample_complaints': complaints[:3]  # Send few examples
    }
    
    prompt = f"""
    Analyze these related complaints and identify the root cause:
    {json.dumps(summary, indent=2)}
    
    Provide:
    1. Likely root cause
    2. Contributing factors
    3. Systemic issues
    4. Recommended solutions
    5. Prevention strategies
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def cluster_similar_complaints():
    """Cluster similar complaints using TF-IDF and DBSCAN"""
    vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(df['complaint'])
    
    # Cluster complaints
    clustering = DBSCAN(eps=0.3, min_samples=3)
    clusters = clustering.fit_predict(tfidf_matrix)
    
    return clusters, vectorizer

def identify_temporal_patterns(category):
    """Identify temporal patterns in complaints"""
    cat_data = df[df['category'] == category].copy()
    cat_data['CreatedAt'] = pd.to_datetime(cat_data['CreatedAt'])
    
    # Analyze daily and weekly patterns
    temporal_patterns = {
        'daily_pattern': cat_data.groupby(cat_data['CreatedAt'].dt.hour).size().to_dict(),
        'weekly_pattern': cat_data.groupby(cat_data['CreatedAt'].dt.dayofweek).size().to_dict(),
        'volume_trend': len(cat_data)
    }
    
    return temporal_patterns

def analyze_category_root_cause(category):
    """Analyze root causes for a specific category"""
    category_data = df[df['category'] == category]
    
    summary = {
        'total_complaints': len(category_data),
        'temporal_patterns': identify_temporal_patterns(category),
        'impact_distribution': {
            'economic': category_data['economicImpact'].value_counts().to_dict(),
            'environmental': category_data['environmentalImpact'].value_counts().to_dict(),
            'social': category_data['socialImpact'].value_counts().to_dict()
        },
        'sample_complaints': category_data['complaint'].sample(5).tolist()
    }
    
    prompt = f"""
    Analyze this category of complaints and identify systemic issues:
    {json.dumps(summary, indent=2)}
    
    Provide:
    1. Primary root causes
    2. Systemic issues identified
    3. Infrastructure gaps
    4. Policy recommendations
    5. Preventive measures
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def generate_root_cause_report():
    """Generate comprehensive root cause analysis report"""
    # Cluster similar complaints
    clusters, vectorizer = cluster_similar_complaints()
    
    # Analyze each category
    category_analyses = {}
    for category in df['category'].unique():
        category_analyses[category] = analyze_category_root_cause(category)
    
    # Analyze clusters
    cluster_analyses = {}
    for cluster_id in set(clusters):
        if cluster_id != -1:  # Skip noise points
            cluster_complaints = df['complaint'][clusters == cluster_id].tolist()
            cluster_analyses[f"Cluster_{cluster_id}"] = analyze_complaint_cluster(cluster_complaints)
    
    # Save comprehensive report
    report_path = '/e:/ML/Analysis/root_cause_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Root Cause Analysis Report\n\n")
        
        f.write("## Category-wise Root Causes\n\n")
        for category, analysis in category_analyses.items():
            f.write(f"### {category}\n")
            f.write(analysis + "\n\n")
        
        f.write("## Complaint Cluster Analysis\n\n")
        for cluster_name, analysis in cluster_analyses.items():
            f.write(f"### {cluster_name}\n")
            f.write(analysis + "\n\n")
        
        # Generate summary recommendations
        summary_prompt = f"""
        Based on the analysis of {len(df)} complaints across {len(category_analyses)} categories,
        provide high-level recommendations for systemic improvements.
        Focus on infrastructure, policy, and governance aspects.
        """
        
        summary_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": summary_prompt}]
        )
        
        f.write("## Executive Summary and Recommendations\n")
        f.write(summary_response.choices[0].message.content)

    return report_path

def predict_future_issues():
    """Predict potential future issues based on current patterns"""
    # Analyze complaint growth rates
    complaint_trends = df.groupby(['category', pd.to_datetime(df['CreatedAt']).dt.month])\
                        .size().unstack(fill_value=0)
    growth_rates = complaint_trends.pct_change(axis=1).mean(axis=1)
    
    # Identify rapidly growing categories
    high_growth_categories = growth_rates[growth_rates > growth_rates.mean()].index.tolist()
    
    # Predict potential issues
    prediction_prompt = f"""
    Based on these rapidly growing complaint categories:
    {high_growth_categories}
    
    Predict:
    1. Potential future issues
    2. Areas requiring preventive action
    3. Long-term infrastructure needs
    4. Policy interventions needed
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prediction_prompt}]
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    print("Starting Root Cause Analysis...")
    report_path = generate_root_cause_report()
    
    # Generate future predictions
    future_predictions = predict_future_issues()
    with open('/e:/ML/Analysis/future_predictions.md', 'w') as f:
        f.write("# Predicted Future Issues\n\n")
        f.write(future_predictions)
    
    print("Analysis completed! Check the reports for detailed findings.")
