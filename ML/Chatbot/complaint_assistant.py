import os
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import pandas as pd
from datetime import datetime
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class ComplaintAssistant:
    def __init__(self):
        # Load models and data
        self.model_name = "facebook/opt-350m"
        self.generator = pipeline('text-generation', 
                                model=self.model_name, 
                                device='cuda' if torch.cuda.is_available() else 'cpu')
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load and preprocess historical data
        self.df = pd.read_csv(r'E:\ML\Data\combined_data.csv')
        self.df['complaint_embedding'] = self.df['complaint'].apply(
            lambda x: self.embedder.encode(str(x)) if pd.notnull(x) else None
        )
        
        self.complaint_template = """
        Based on the following complaint and historical data analysis:
        
        Complaint: {complaint}
        
        Similar Past Cases:
        {similar_cases}
        
        Department Performance:
        {dept_stats}
        
        Please provide:
        1. Initial response to the complainant
        2. Most appropriate department assignment based on historical success rate
        3. Estimated resolution time based on similar cases
        4. Recommended action plan with specific steps
        5. Priority level assignment (High/Medium/Low)
        """

    def analyze_department_performance(self, dept):
        """Analyze department performance metrics"""
        dept_data = self.df[self.df['departmentAssigned'] == dept]
        avg_resolution_time = dept_data['ResolutionTime'].mean()
        success_rate = len(dept_data[dept_data['status'] == 'Closed']) / len(dept_data) if len(dept_data) > 0 else 0
        
        return {
            'avg_resolution_time': avg_resolution_time,
            'success_rate': success_rate,
            'total_cases': len(dept_data)
        }

    def find_similar_cases(self, complaint_text, n_cases=3):
        """Find similar historical complaints using embeddings"""
        try:
            query_embedding = self.embedder.encode(complaint_text)
            
            # Calculate similarities
            similarities = self.df['complaint_embedding'].apply(
                lambda x: cosine_similarity([query_embedding], [x])[0][0] if x is not None else 0
            )
            
            # Get top similar cases
            top_indices = similarities.nlargest(n_cases).index
            similar_cases = self.df.iloc[top_indices]
            
            # Format similar cases
            cases_text = ""
            for _, case in similar_cases.iterrows():
                cases_text += f"\nCase ID: {case['id']}\n"
                cases_text += f"Complaint: {case['complaint']}\n"
                cases_text += f"Department: {case['departmentAssigned']}\n"
                cases_text += f"Resolution Time: {case['ResolutionTime']} days\n"
                cases_text += f"Status: {case['status']}\n"
                cases_text += "-" * 50 + "\n"
            
            return cases_text, similar_cases['departmentAssigned'].mode()[0]
        except Exception as e:
            print(f"Error finding similar cases: {str(e)}")
            return "No similar cases found.", None

    def get_department_stats(self, department):
        """Get department performance statistics"""
        stats = self.analyze_department_performance(department)
        return f"""
        Department: {department}
        Average Resolution Time: {stats['avg_resolution_time']:.1f} days
        Success Rate: {stats['success_rate']*100:.1f}%
        Total Cases Handled: {stats['total_cases']}
        """

    def process_complaint(self, complaint_text):
        """Process a new complaint and provide response"""
        similar_cases, suggested_dept = self.find_similar_cases(complaint_text)
        dept_stats = self.get_department_stats(suggested_dept) if suggested_dept else ""
        
        full_prompt = self.complaint_template.format(
            complaint=complaint_text,
            similar_cases=similar_cases,
            dept_stats=dept_stats
        )
        
        response = self._generate_response(full_prompt)
        
        return {
            'response': response,
            'similar_cases': similar_cases,
            'department_stats': dept_stats,
            'suggested_department': suggested_dept
        }

    def _generate_response(self, prompt, max_length=500):
        """Generate response using local model"""
        try:
            response = self.generator(prompt, 
                                    max_length=max_length, 
                                    num_return_sequences=1)
            return response[0]['generated_text']
        except Exception as e:
            print(f"Generation Error: {str(e)}")
            return "Unable to process request. Please try again."

if __name__ == "__main__":
    try:
        print("Note: Using local model and historical data analysis...")
        assistant = ComplaintAssistant()
        
        test_complaint = """
        I received a damaged product in my latest order #12345. 
        The package arrived with visible external damage and the contents were broken.
        I need a replacement or refund as soon as possible.
        """
        
        result = assistant.process_complaint(test_complaint)
        print("\nComplaint Analysis:")
        print("-" * 50)
        print("Response:", result['response'])
        print("\nSimilar Historical Cases:")
        print("-" * 50)
        print(result['similar_cases'])
        print("\nDepartment Statistics:")
        print("-" * 50)
        print(result['department_stats'])
        print("\nSuggested Department:", result['suggested_department'])
        
    except Exception as e:
        print(f"Error: {str(e)}")

