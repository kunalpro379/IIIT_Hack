import pandas as pd
import joblib
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics import classification_report, confusion_matrix

test_data = pd.read_csv('test_grivieances.csv')

# test_data = test_data.drop(columns=['keywordsTags_0', 'keywordsTags_1', 'keywordsTags_2', 'keywordsTags_3'])

test_data['text'] = test_data['description'] + ' ' + test_data['sentimentScore'].astype(str)

test_data['priority'] = test_data['urgencyLevel'].apply(lambda x: 1 if x == 'Critical' or x == 'High' else 0)

clf = joblib.load('grievance_classifier.pkl')
tokenizer = joblib.load('bert_tokenizer.pkl')
model = joblib.load('bert_model.pkl')

def get_bert_features(text):
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

X_test = test_data['text']
y_test = test_data['priority']
X_test_bert = [get_bert_features(text) for text in X_test]

y_pred = clf.predict(X_test_bert)

print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))

test_data['predicted_priority'] = y_pred
test_data.to_csv('classified_grievances.csv', index=False)

categories = test_data['category'].unique()
for category in categories:
    category_data = test_data[test_data['category'] == category]
    with open(f'{category}_summary.txt', 'w', encoding='utf-8') as file:
        for index, row in category_data.iterrows():
            file.write(f"ID: {row['id']}\n")
            file.write(f"Title: {row['title']}\n")
            file.write(f"Description: {row['description']}\n")
            file.write(f"Urgency Level: {row['urgencyLevel']}\n")
            file.write(f"Predicted Priority: {'Urgent' if row['predicted_priority'] == 1 else 'Not Urgent'}\n")
            file.write(f"Sentiment Score: {row['sentimentScore']}\n")
            file.write(f"Category: {row['category']}\n")
            file.write(f"Subcategory: {row['subcategory']}\n")
            file.write(f"Submission Date: {row['submissionDate']}\n")
            file.write(f"Last Updated Date: {row['lastUpdatedDate']}\n")
            file.write(f"District: {row['district']}\n")
            file.write(f"Tehsil: {row['tehsil']}\n")
            file.write(f"Ward: {row['ward']}\n")
            file.write(f"Pincode: {row['pincode']}\n")
            file.write(f"GPS Coordinates: ({row['gpsCoordinates_latitude']}, {row['gpsCoordinates_longitude']})\n")
            file.write(f"Department Assigned: {row['departmentAssigned']}\n")
            file.write(f"Status: {row['status']}\n")
            file.write(f"Escalation Level: {row['escalationLevel']}\n")
            file.write(f"Expected Resolution Date: {row['expectedResolutionDate']}\n")
            file.write(f"Attachments: {row['attachments_0_fileUrl']}\n")
            file.write(f"Language Preference: {row['languagePreference']}\n")
            file.write(f"Is Anonymous: {row['isAnonymous']}\n")
            file.write(f"Related Policies: {row['relatedPolicies_0']}, {row['relatedPolicies_1']}\n")
            file.write(f"Impacted Population: {row['impactedPopulation']}\n")
            file.write(f"Recurrence Frequency: {row['recurrenceFrequency']}\n")
            file.write(f"Budget Estimate: {row['budgetEstimate']}\n")
            file.write(f"SDG Goals: {row['sdgGoals_0']}, {row['sdgGoals_1']}\n")
            file.write(f"Media Attention: {row['mediaAttention']}\n")
            file.write(f"Political Sensitivity: {row['politicalSensitivity']}\n")
            file.write(f"Community Support: {row['communitySupport']}\n")
            file.write(f"Historical Data - Previous Occurrences: {row['historicalData_previousOccurrences']}\n")
            file.write(f"Historical Data - Average Resolution Time: {row['historicalData_averageResolutionTime']}\n")
            file.write(f"Historical Data - Success Rate: {row['historicalData_successRate']}\n")
            file.write(f"Accessibility Needs: {row['accessibilityNeeds_0']}\n")
            file.write(f"Preferred Contact Method: {row['preferredContactMethod']}\n")
            file.write(f"Feedback Follow-Up Date: {row['feedbackFollowUpDate']}\n")
            file.write(f"Citizen Satisfaction Index: {row['citizenSatisfactionIndex']}\n")
            file.write(f"Resolution Quality Score: {row['resolutionQualityScore']}\n")
            file.write(f"Environmental Impact: {row['environmentalImpact']}\n")
            file.write(f"Economic Impact: {row['economicImpact']}\n")
            file.write(f"Social Impact: {row['socialImpact']}\n")
            file.write(f"AI Recommendations: {row['aiRecommendations_0']}, {row['aiRecommendations_1']}\n")
            file.write(f"Trend Analysis - Trend: {row['trendAnalysis_trend']}\n")
            file.write(f"Trend Analysis - Confidence Score: {row['trendAnalysis_confidenceScore']}\n")
            file.write(f"Predictive Maintenance - Next Predicted Occurrence: {row['predictiveMaintenance_nextPredictedOccurrence']}\n")
            file.write(f"Predictive Maintenance - Preventive Measures: {row['predictiveMaintenance_preventiveMeasures_0']}, {row['predictiveMaintenance_preventiveMeasures_1']}\n")
            file.write(f"Cross-Department Collaboration: {row['crossDepartmentCollaboration_0']}, {row['crossDepartmentCollaboration_1']}\n")
            file.write(f"Linked Service Requests: {row['linkedServiceRequests_0']}\n")
            file.write(f"Citizen Profile - Government ID: {row['citizenProfile_governmentId']}\n")
            file.write(f"Citizen Profile - Demographic Segment: {row['citizenProfile_demographicSegment']}\n")
            file.write(f"Citizen Profile - Service History: {row['citizenProfile_serviceHistory_0']}, {row['citizenProfile_serviceHistory_1']}\n")
            file.write(f"Attachments: {row['attachments_1_fileUrl']}\n")
            file.write(f"Audit Log: {row['auditLog_0_timestamp']} - {row['auditLog_0_action']} by {row['auditLog_0_performedBy']}\n")
            file.write(f"Accessibility Needs: {row['accessibilityNeeds']}\n")
            file.write(f"Attachments: {row['attachments']}\n")
            file.write(f"Accessibility Needs: {row['accessibilityNeeds_1']}\n")
            file.write("\n\n")
