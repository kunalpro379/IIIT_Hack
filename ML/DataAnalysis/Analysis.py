
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

# Read the CSV file
df = pd.read_csv('../Grivances/gen_datasets/combined_data.csv')

# Basic Data Information
print("\n=== Basic Dataset Information ===")
print(df.info())
print("\n=== Data Sample ===")
print(df.head())

# 1. Complaint Analysis
print("\n=== Complaint Category Analysis ===")
category_counts = df['category'].value_counts()
print("\nTop 10 Complaint Categories:")
print(category_counts.head(10))

# Visualize complaint categories
plt.figure(figsize=(12, 6))
category_counts.head(10).plot(kind='bar')
plt.title('Top 10 Complaint Categories')
plt.xlabel('Category')
plt.ylabel('Number of Complaints')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('complaint_categories.png')

# 2. Status Analysis
print("\n=== Complaint Status Analysis ===")
status_counts = df['status'].value_counts()
print(status_counts)

# Visualize status distribution
plt.figure(figsize=(8, 8))
plt.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%')
plt.title('Complaint Status Distribution')
plt.savefig('status_distribution.png')

# 3. Resolution Time Analysis
print("\n=== Resolution Time Analysis ===")
print("Average Resolution Time:", df['ResolutionTime'].mean())
print("Maximum Resolution Time:", df['ResolutionTime'].max())
print("Minimum Resolution Time:", df['ResolutionTime'].min())

# Visualize resolution time distribution
plt.figure(figsize=(10, 6))
sns.histplot(data=df, x='ResolutionTime', bins=30)
plt.title('Distribution of Resolution Times')
plt.xlabel('Resolution Time (days)')
plt.ylabel('Count')
plt.savefig('resolution_time_distribution.png')

# 4. Geographic Analysis
print("\n=== Geographic Distribution ===")
district_counts = df['district'].value_counts()
print("\nTop 10 Districts with Most Complaints:")
print(district_counts.head(10))

# Visualize geographic distribution
plt.figure(figsize=(12, 6))
district_counts.head(10).plot(kind='bar')
plt.title('Top 10 Districts with Most Complaints')
plt.xlabel('District')
plt.ylabel('Number of Complaints')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('district_distribution.png')

# 5. Impact Analysis
print("\n=== Impact Analysis ===")
urgency_counts = df['urgencyLevel'].value_counts()
print("\nUrgency Level Distribution:")
print(urgency_counts)

# 6. Anonymous Complaints Analysis
print("\n=== Anonymous Complaints Analysis ===")
anonymous_counts = df['isAnonymous'].value_counts()
print("\nAnonymous vs Non-Anonymous Complaints:")
print(anonymous_counts)

# 7. Department Analysis
print("\n=== Department Assignment Analysis ===")
dept_counts = df['departmentAssigned'].value_counts()
print("\nTop 10 Departments with Most Complaints:")
print(dept_counts.head(10))

# 8. Emotion Analysis
print("\n=== Emotion Analysis ===")
emotion_counts = df['emotion'].value_counts()
print("\nDistribution of Emotions:")
print(emotion_counts)

# Visualize emotion distribution
plt.figure(figsize=(12, 6))
emotion_counts.plot(kind='bar')
plt.title('Distribution of Emotions in Complaints')
plt.xlabel('Emotion')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('emotion_distribution.png')

# 9. Time Series Analysis
df['CreatedAt'] = pd.to_datetime(df['CreatedAt'])
complaints_over_time = df.groupby(df['CreatedAt'].dt.date).size()

plt.figure(figsize=(15, 6))
complaints_over_time.plot(kind='line')
plt.title('Number of Complaints Over Time')
plt.xlabel('Date')
plt.ylabel('Number of Complaints')
plt.tight_layout()
plt.savefig('complaints_over_time.png')

# 10. Correlation Analysis
# Select numeric columns for correlation
numeric_columns = df.select_dtypes(include=[np.number]).columns
correlation_matrix = df[numeric_columns].corr()

plt.figure(figsize=(12, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('Correlation Matrix of Numeric Variables')
plt.tight_layout()
plt.savefig('correlation_matrix.png')

# Save summary to a text file
with open('analysis_summary.txt', 'w') as f:
    f.write("=== Grievance Analysis Summary ===\n\n")
    f.write(f"Total number of complaints: {len(df)}\n")
    f.write(f"Date range: {df['CreatedAt'].min()} to {df['CreatedAt'].max()}\n")
    f.write(f"Average resolution time: {df['ResolutionTime'].mean():.2f} days\n")
    f.write(f"Most common category: {category_counts.index[0]}\n")
    f.write(f"Most common department: {dept_counts.index[0]}\n")
    f.write(f"Most common emotion: {emotion_counts.index[0]}\n")
    f.write(f"\nStatus Distribution:\n{status_counts.to_string()}\n")
    f.write(f"\nTop 5 Districts:\n{district_counts.head().to_string()}\n")

print("\nAnalysis complete! Check the generated plots and analysis_summary.txt for detailed results.")
