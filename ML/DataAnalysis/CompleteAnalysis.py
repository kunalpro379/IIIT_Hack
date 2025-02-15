import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats

# Read the data
df = pd.read_csv('E:/ML/Data/combined_data.csv')

# Basic Dataset Statistics
print("\n1. BASIC DATASET INFORMATION")
print("-" * 50)
print(f"Total number of complaints: {len(df)}")
print(f"Number of features: {df.shape[1]}")
print("\nMissing Values Analysis:")
print(df.isnull().sum())

# Complaint Type Analysis
print("\n2. COMPLAINT TYPE ANALYSIS")
print("-" * 50)
complaint_stats = df['complaintType'].value_counts()
print("\nTop 10 Most Common Complaints:")
print(complaint_stats.head(10))
print(f"\nTotal unique complaint types: {df['complaintType'].nunique()}")

# Status Analysis
print("\n3. STATUS ANALYSIS")
print("-" * 50)
status_stats = df['status'].value_counts()
print("\nComplaints by Status:")
print(status_stats)
print(f"\nResolution Rate: {(df['status'] == 'Closed').mean()*100:.2f}%")

# Resolution Time Analysis
print("\n4. RESOLUTION TIME ANALYSIS")
print("-" * 50)
df['ResolutionTime'] = pd.to_numeric(df['ResolutionTime'], errors='coerce')
print("\nResolution Time Statistics (in days):")
print(df['ResolutionTime'].describe())
print(f"\nMedian Resolution Time: {df['ResolutionTime'].median()} days")
print(f"Mode Resolution Time: {df['ResolutionTime'].mode()[0]} days")

# Department Analysis
print("\n5. DEPARTMENT ANALYSIS")
print("-" * 50)
dept_stats = df['departmentAssigned'].value_counts()
print("\nComplaints by Department:")
print(dept_stats)
print(f"\nTotal Departments Involved: {df['departmentAssigned'].nunique()}")

# Urgency Level Analysis
print("\n6. URGENCY LEVEL ANALYSIS")
print("-" * 50)
urgency_stats = df['urgencyLevel'].value_counts()
print("\nComplaints by Urgency Level:")
print(urgency_stats)
print(f"\nPercentage of High Urgency Cases: {(df['urgencyLevel'] == 'High').mean()*100:.2f}%")

# Location Analysis
print("\n7. LOCATION ANALYSIS")
print("-" * 50)
location_stats = df['district'].value_counts()
print("\nTop 10 Districts with Most Complaints:")
print(location_stats.head(10))

# Impact Analysis
print("\n8. IMPACT ANALYSIS")
print("-" * 50)
print("\nEconomic Impact Distribution:")
print(df['economicImpact'].value_counts())
print("\nSocial Impact Distribution:")
print(df['socialImpact'].value_counts())
print("\nEnvironmental Impact Distribution:")
print(df['environmentalImpact'].value_counts())

# Temporal Analysis
print("\n9. TEMPORAL ANALYSIS")
print("-" * 50)
df['CreatedAt'] = pd.to_datetime(df['CreatedAt'])
df['Month'] = df['CreatedAt'].dt.month
df['DayOfWeek'] = df['CreatedAt'].dt.dayofweek

monthly_stats = df['Month'].value_counts().sort_index()
print("\nComplaints by Month:")
print(monthly_stats)

daily_stats = df['DayOfWeek'].value_counts().sort_index()
print("\nComplaints by Day of Week (0=Monday, 6=Sunday):")
print(daily_stats)

# Cross Analysis
print("\n10. CROSS ANALYSIS")
print("-" * 50)
print("\nAverage Resolution Time by Urgency Level:")
print(df.groupby('urgencyLevel')['ResolutionTime'].mean())

print("\nStatus Distribution by Department (Top 5 Departments):")
top_depts = dept_stats.head().index
for dept in top_depts:
    dept_df = df[df['departmentAssigned'] == dept]
    print(f"\n{dept}:")
    print(dept_df['status'].value_counts(normalize=True).multiply(100).round(2))

# Statistical Tests
print("\n11. STATISTICAL ANALYSIS")
print("-" * 50)

# Chi-square test for independence between urgency level and status
contingency = pd.crosstab(df['urgencyLevel'], df['status'])
chi2, p_value = stats.chi2_contingency(contingency)[:2]
print(f"\nChi-square test (Urgency Level vs Status):")
print(f"Chi2 value: {chi2:.2f}")
print(f"p-value: {p_value:.4f}")

# ANOVA test for resolution time differences across departments
departments = df['departmentAssigned'].unique()
resolution_by_dept = [group['ResolutionTime'].dropna() for name, group in df.groupby('departmentAssigned')]
f_stat, anova_p = stats.f_oneway(*resolution_by_dept)
print(f"\nANOVA test (Resolution Time across Departments):")
print(f"F-statistic: {f_stat:.2f}")
print(f"p-value: {anova_p:.4f}")

# Key Findings Summary
print("\n12. KEY FINDINGS SUMMARY")
print("-" * 50)
print("\nTop Issues:")
print(f"1. Most common complaint type: {complaint_stats.index[0]}")
print(f"2. Department with highest workload: {dept_stats.index[0]}")
print(f"3. Average resolution time: {df['ResolutionTime'].mean():.2f} days")
print(f"4. Percentage of high urgency cases: {(df['urgencyLevel'] == 'High').mean()*100:.2f}%")
print(f"5. Most affected district: {location_stats.index[0]}")

# Save analysis results to file
with open('/e:/ML/DataAnalysis/detailed_analysis_results.txt', 'w') as f:
    f.write("Detailed Analysis Results\n")
    f.write("=======================\n\n")
    f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Total Complaints Analyzed: {len(df)}\n")
    f.write(f"Date Range: {df['CreatedAt'].min()} to {df['CreatedAt'].max()}\n")
    f.write(f"Resolution Rate: {(df['status'] == 'Closed').mean()*100:.2f}%\n")
    f.write(f"Average Resolution Time: {df['ResolutionTime'].mean():.2f} days\n")
    f.write(f"High Urgency Cases: {(df['urgencyLevel'] == 'High').sum()}\n")
    f.write(f"Most Common Complaint: {complaint_stats.index[0]}\n")
    f.write(f"Most Active Department: {dept_stats.index[0]}\n")
