import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from transformers import pipeline
import torch

print("Loading model...")
# Initialize model with better parameters for creative generation
model = pipeline('text-generation', 
                model='gpt2',
                device=-1,
                max_length=150,
                temperature=0.9,
                top_p=0.9,
                no_repeat_ngram_size=2)

# Define templates for Hindi-English mixed content
TEMPLATES = {
    'complaints': [
        "सड़क में बहुत गड्ढे हैं need urgent repair",
        "Road condition is very bad गाड़ी चलाना मुश्किल है",
        "{category} की हालत खराब है immediate action needed",
        "Serious problem with {category} in {location} area",
        "बहुत गंभीर समस्या है {category} की urgent attention required",
    ],
    'impacts': [
        "causing accidents daily",
        "बहुत परेशानी हो रही है",
        "affecting elderly and children", 
        "business losses हो रहे हैं",
        "emergency situation है"
    ]
}

# Add Hindi names data
HINDI_NAMES = [
    'सुधा वर्मा', 'राजेश यादव', 'अमित कुमार', 'प्रिया सिंह', 'संजय वर्मा',
    'नेहा गुप्ता', 'विकास त्रिपाठी', 'कविता सिंह', 'राहुल शर्मा', 'मीना सिंह',
    'अभिषेक तिवारी', 'पूजा गुप्ता', 'दीपक चौहान', 'स्वाति अग्रवाल', 'मनोज पांडेय'
]

def generate_natural_complaint(category, location):
    """Generate natural sounding complaints mixing Hindi and English"""
    prompts = [
        f"Write a complaint in Hindi and English about {category} problems in {location}:",
        f"Describe issues with {category} services in {location} using Hindi and English:",
        f"Express concerns about {category} situation in {location} mixing Hindi and English:",
    ]
    
    # Generate base complaint
    complaint = model(random.choice(prompts))[0]['generated_text']
    
    # Add emotional/urgency elements randomly
    emotions = [
        "बहुत परेशानी हो रही है",
        "urgent action needed",
        "situation is very critical",
        "लोग त्रस्त हैं",
        "immediate intervention required"
    ]
    
    # Add impact statements
    impacts = [
        "affecting daily life",
        "causing economic losses", 
        "public safety at risk",
        "बच्चों की पढ़ाई प्रभावित",
        "व्यापार पर असर"
    ]
    
    complaint = f"{complaint} {random.choice(emotions)}. {random.choice(impacts)}"
    return complaint

# Define constant values matching the training data format
CATEGORIES = {
    'Fire Safety': ['Fire Hazard', 'Fire Prevention'],
    'Education': ['School Infrastructure', 'Quality Education'],
    'Street Lighting': ['Broken Lights', 'New Installation'],
    'Water Supply': ['Low Pressure', 'Water Quality'],
    'Road Infrastructure': ['Pothole Repair', 'Road Widening'],
    'Healthcare': ['Medicine Availability', 'Hospital Services'],
    # Add more categories and subcategories from training data
}

DISTRICTS = ['सहारनपुर', 'लखनऊ', 'कानपुर', 'वाराणसी', 'आगरा', 'प्रयागराज', 'गोरखपुर', 'मेरठ', 'झाँसी', 'बरेली']
TEHSILS = ['बक्शी का तालाब', 'सरोजिनी नगर', 'माल', 'हजरतगंज']
WARDS = ['Hazratganj', 'Civil Lines', 'Gomti Nagar', 'रापती नगर', 'शास्त्री नगर', 'सिविल लाइन्स', 'भेलूपुर']
PINCODES = ['221001', '226001', '208001', '273001', '250001']

def generate_grievance():
    category = random.choice(list(CATEGORIES.keys()))
    district = random.choice(DISTRICTS)
    base_date = datetime.now() - timedelta(days=random.randint(1, 365))

    # Generate natural title and description
    title = generate_natural_complaint(category, district).split('.')[0]  # First sentence
    description = generate_natural_complaint(category, district)
    
    record = {
        'id': f"GR{base_date.strftime('%Y%m')}{random.randint(1000, 9999)}",
        'title': title,
        'description': description,
        'citizenName': random.choice(HINDI_NAMES),  # Use predefined Hindi names
        'contactNumber': f"{random.randint(7000000000, 8999999999)}",
        'email': f"citizen{random.randint(100,999)}@example.com",
        'category': category,
        'subcategory': random.choice(CATEGORIES[category]),
        'urgencyLevel': random.choice(['Low', 'Medium', 'High', 'Critical']),
        'submissionDate': base_date.isoformat() + 'Z',
        'lastUpdatedDate': (base_date + timedelta(days=random.randint(1, 14))).isoformat() + 'Z',
        'district': random.choice(DISTRICTS),
        'tehsil': random.choice(TEHSILS),
        'ward': random.choice(WARDS),
        'pincode': random.choice(PINCODES),
        'gpsCoordinates_latitude': random.uniform(25.0, 28.9),
        'gpsCoordinates_longitude': random.uniform(77.0, 84.5),
        'departmentAssigned': f"{category} Department",
        'status': random.choice(['New', 'InProgress', 'Resolved', 'Escalated']),
        'escalationLevel': random.randint(0, 3),
        'expectedResolutionDate': (base_date + timedelta(days=random.randint(3, 30))).isoformat() + 'Z',
        'attachments': '[]',
        'sentimentScore': round(random.uniform(-1.0, -0.3), 2),
        'priorityScore': random.randint(50, 100)
    }
    
    # Add standard keywords based on category
    keywords = ['road', 'pothole', 'accident', 'repair', 'सड़क', 'गड्ढा', 'मरम्मत', 'safety']
    for i, keyword in enumerate(keywords):
        record[f'keywordsTags_{i}'] = keyword
    
    # Add remaining fields matching training data format
    record.update({
        'categoryPrediction': category,
        'estimatedResolutionTime': random.randint(1, 30),
        'createdAt': record['submissionDate'],
        'updatedAt': record['lastUpdatedDate'],
        'auditLog_0_timestamp': record['submissionDate'],
        'auditLog_0_action': 'Grievance Submitted',
        'auditLog_0_performedBy': 'Citizen',
        'auditLog_0_details': 'Grievance submitted through mobile app',
        'languagePreference': random.choice(['Hindi', 'English', 'Hinglish']),
        'isAnonymous': random.choice([True, False]),
        'relatedPolicies_0': 'Road Safety Policy',
        'relatedPolicies_1': 'Infrastructure Maintenance Guidelines',
        'impactedPopulation': random.choice([100, 250, 500, 1000, 2000, 5000]),
        'recurrenceFrequency': 'First occurrence',
        'budgetEstimate': random.randint(5000, 50000),
        'sdgGoals_0': 'SDG 9: Infrastructure',
        'sdgGoals_1': 'SDG 11: Sustainable Cities',
        'historicalData_previousOccurrences': 0,
        'environmentalImpact': random.choice(['Minimal', 'Air pollution', 'Water wastage']),
        'economicImpact': random.choice(['Local business impact', 'Infrastructure damage', 'Crop yield reduction']),
        'socialImpact': random.choice(['Social disruption', 'Public safety risk', 'Community health concern']),
        'citizenProfile_governmentId': f"AADHAAR-XXXX-XXXX-{random.randint(1000,9999)}",
        'citizenProfile_demographicSegment': random.choice(['Student', 'Rural farmer', 'Urban professional']),
        'citizenProfile_serviceHistory_0': random.choice(['Agricultural Subsidies', 'Health Services', 'Water Supply Services']),
        'citizenProfile_serviceHistory_1': random.choice(['Health Services', 'Water Supply Services', 'Agricultural Subsidies']),
        'mediaAttention': random.choice([True, False]),
        'politicalSensitivity': random.randint(1, 5),
        'communitySupport': random.randint(50, 100),
        'accessibilityNeeds_0': random.choice(['', 'Audio assistance', 'Sign language interpreters', 'Wheelchair access']),
        'accessibilityNeeds_1': random.choice(['', 'Wheelchair access', 'Audio assistance', 'Sign language interpreters']),
        'preferredContactMethod': random.choice(['SMS', 'Email', 'Phone']),
        'feedbackFollowUpDate': (base_date + timedelta(days=random.randint(5, 35))).isoformat() + 'Z'
    })
    
    return record

if __name__ == "__main__":
    print("Generating grievances...")
    grievances = [generate_grievance() for _ in range(200)]
    df = pd.DataFrame(grievances)
    df.to_csv('generated_grievances.csv', index=False)
    print("Generated 200 grievances successfully!")
