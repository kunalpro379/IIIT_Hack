import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from transformers import BertTokenizer, BertModel
import torch

data = pd.read_csv('grievances.csv')

data = data.drop(columns=['keywordsTags_0', 'keywordsTags_1', 'keywordsTags_2', 'keywordsTags_3'])

data['text'] = data['description'] + ' ' + data['sentimentScore'].astype(str)

data['priority'] = data['urgencyLevel'].apply(lambda x: 1 if x == 'Critical' or x == 'High' else 0)

X = data['text']
y = data['priority']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def get_bert_features(text):
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

X_train_bert = [get_bert_features(text) for text in X_train]
X_test_bert = [get_bert_features(text) for text in X_test]

clf = LogisticRegression(max_iter=1000)
clf.fit(X_train_bert, y_train)

y_pred = clf.predict(X_test_bert)
print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))

joblib.dump(clf, 'grievance_classifier.pkl')
joblib.dump(tokenizer, 'bert_tokenizer.pkl')
joblib.dump(model, 'bert_model.pkl')
