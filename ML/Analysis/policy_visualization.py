import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_policy_visualizations(df):
    """Create visualizations for policy analysis"""
    
    # 1. Complaint Volume by District and Category
    fig1 = px.sunburst(df, 
                       path=['district', 'category'],
                       values='ResolutionTime',
                       title='Complaint Distribution Hierarchy')
    fig1.write_html('/e:/ML/Analysis/district_category_distribution.html')
    
    # 2. Department Performance Dashboard
    dept_stats = df.groupby('departmentAssigned').agg({
        'id': 'count',
        'ResolutionTime': 'mean',
        'urgencyLevel': lambda x: (x == 'High').mean() * 100
    }).reset_index()
    
    fig2 = make_subplots(rows=2, cols=2,
                         subplot_titles=('Complaint Volume', 'Resolution Time',
                                       'High Urgency Percentage', 'Performance Matrix'))
    
    fig2.add_trace(go.Bar(x=dept_stats['departmentAssigned'], 
                         y=dept_stats['id'],
                         name='Complaints'),
                   row=1, col=1)
    
    fig2.add_trace(go.Bar(x=dept_stats['departmentAssigned'],
                         y=dept_stats['ResolutionTime'],
                         name='Avg Resolution Time'),
                   row=1, col=2)
    
    fig2.add_trace(go.Bar(x=dept_stats['departmentAssigned'],
                         y=dept_stats['urgencyLevel'],
                         name='High Urgency %'),
                   row=2, col=1)
    
    fig2.update_layout(height=800, title='Department Performance Dashboard')
    fig2.write_html('/e:/ML/Analysis/department_performance.html')
    
    # 3. Impact Analysis
    impact_data = pd.melt(df[['economicImpact', 'environmentalImpact', 'socialImpact']])
    fig3 = px.treemap(impact_data, 
                      path=['variable', 'value'],
                      title='Impact Distribution Analysis')
    fig3.write_html('/e:/ML/Analysis/impact_analysis.html')
    
    # 4. Time Series Analysis
    df['CreatedAt'] = pd.to_datetime(df['CreatedAt'])
    time_series = df.groupby(['CreatedAt', 'category']).size().reset_index(name='count')
    
    fig4 = px.line(time_series, 
                   x='CreatedAt',
                   y='count',
                   color='category',
                   title='Complaint Trends Over Time')
    fig4.write_html('/e:/ML/Analysis/complaint_trends.html')

if __name__ == "__main__":
    df = pd.read_csv('/e:/ML/DataAnalysis/combined_data.csv')
    create_policy_visualizations(df)
    print("Visualizations created successfully!")
