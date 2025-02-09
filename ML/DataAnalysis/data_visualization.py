import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import numpy as np
from datetime import datetime

class GrievanceAnalyzer:
    def __init__(self, data_path):
        self.df = pd.read_csv(data_path)
        self.preprocess_data()
        
    def preprocess_data(self):
        # Convert dates to datetime
        date_columns = ['CreatedAt', 'lastUpdatedDate', 'date', 'submissionDate', 'updatedAt']
        for col in date_columns:
            if (col in self.df.columns):
                self.df[col] = pd.to_datetime(self.df[col])
        
        # Fix fillna operations
        self.df = self.df.copy()  # Create a copy to avoid chained assignment
        self.df['emotion'] = self.df['emotion'].fillna('Not Specified')
        self.df['urgencyLevel'] = self.df['urgencyLevel'].fillna('Medium')
        
    def create_dashboard(self, output_path):
        figs = []
        
        # Replace the map visualization with a simplified district-wise heatmap
        district_stats = self.df.groupby('district').agg({
            'id': 'count',
            'ResolutionTime': 'mean',
            'urgencyLevel': lambda x: (x == 'High').sum(),
            'status': lambda x: (x == 'Open').sum(),
            # Handle empty categories by using a safer aggregation
            'category': lambda x: x.fillna('Not Specified').value_counts().index[0] if len(x) > 0 else 'No Data'
        }).reset_index()
        
        district_stats.columns = ['District', 'Total_Complaints', 'Avg_Resolution_Time', 
                                'High_Priority_Cases', 'Open_Cases', 'Most_Common_Category']

        fig_map = go.Figure()

        # Create a grid layout for districts
        num_rows = 8
        num_cols = 10
        district_positions = {
            # Add your district positions here
            # Example: 'Lucknow': (4, 5),  # row 4, column 5
            'Agra': (5, 2),
            'Aligarh': (4, 2),
            'Prayagraj': (5, 7),
            'Bareilly': (3, 4),
            'Kanpur': (5, 5),
            'Varanasi': (5, 8),
            'Meerut': (2, 3),
            'Lucknow': (4, 5),
            # Add more districts as needed
        }

        # Add rectangles for each district
        for district, pos in district_positions.items():
            if district in district_stats['District'].values:
                stats = district_stats[district_stats['District'] == district].iloc[0]
                
                fig_map.add_trace(go.Scatter(
                    x=[pos[1]],
                    y=[pos[0]],
                    mode='markers+text',
                    marker=dict(
                        size=40,
                        color=stats['Total_Complaints'],
                        colorscale='Viridis',
                        showscale=True,
                        colorbar=dict(title='Total Complaints')
                    ),
                    text=district,
                    textposition='middle center',
                    name=district,
                    hovertemplate=(
                        f"<b>{district}</b><br>" +
                        "Total Complaints: %{marker.color}<br>" +
                        f"Avg Resolution Time: {stats['Avg_Resolution_Time']:.1f} days<br>" +
                        f"High Priority Cases: {stats['High_Priority_Cases']}<br>" +
                        f"Open Cases: {stats['Open_Cases']}<br>" +
                        f"Most Common Category: {stats['Most_Common_Category']}<br>" +
                        "<extra></extra>"
                    )
                ))

        fig_map.update_layout(
            title='UP District-wise Complaint Distribution',
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=600,
            width=800,
            plot_bgcolor='rgba(0,0,0,0)'
        )

        figs.insert(0, fig_map)  # Add map as first visualization
        
        # Add detailed timeline
        timeline_data = self.df.copy()
        timeline_data['Month'] = timeline_data['CreatedAt'].dt.strftime('%Y-%m')
        monthly_stats = timeline_data.groupby('Month').agg({
            'id': 'count',
            'ResolutionTime': 'mean',
            'urgencyLevel': lambda x: (x == 'High').sum()
        }).reset_index()
        monthly_stats.columns = ['Month', 'Total_Complaints', 'Avg_Resolution_Time', 'High_Priority']
        
        fig_timeline = make_subplots(rows=3, cols=1,
                                   subplot_titles=('Total Complaints', 'Average Resolution Time', 'High Priority Cases'))
        
        fig_timeline.add_trace(
            go.Scatter(x=monthly_stats['Month'], y=monthly_stats['Total_Complaints'],
                      mode='lines+markers', name='Total Complaints'),
            row=1, col=1
        )
        
        fig_timeline.add_trace(
            go.Scatter(x=monthly_stats['Month'], y=monthly_stats['Avg_Resolution_Time'],
                      mode='lines+markers', name='Avg Resolution Time'),
            row=2, col=1
        )
        
        fig_timeline.add_trace(
            go.Scatter(x=monthly_stats['Month'], y=monthly_stats['High_Priority'],
                      mode='lines+markers', name='High Priority Cases'),
            row=3, col=1
        )
        
        fig_timeline.update_layout(
            height=800,
            title_text='Monthly Grievance Metrics',
            showlegend=False
        )
        
        figs.append(fig_timeline)
        
        # Update hover templates for existing visualizations
        for fig in figs[1:-1]:  # Skip map and timeline
            if isinstance(fig, go.Figure):
                for trace in fig.data:
                    if hasattr(trace, 'hovertemplate'):
                        trace.hovertemplate = trace.hovertemplate.replace('=', ': ') + '<extra></extra>'
        
        # 1. Emotion Distribution
        fig_emotion = px.pie(self.df, 
                           names='emotion', 
                           title='Distribution of Emotions in Grievances',
                           color_discrete_sequence=px.colors.qualitative.Set3)
        figs.append(fig_emotion)
        
        # 2. Urgency Level Distribution
        fig_urgency = px.pie(self.df, 
                            names='urgencyLevel',
                            title='Distribution of Urgency Levels',
                            color_discrete_sequence=px.colors.qualitative.Set2)
        figs.append(fig_urgency)
        
        # 3. Resolution Time Analysis
        fig_resolution = px.box(self.df, 
                              y='ResolutionTime',
                              title='Resolution Time Distribution (Days)')
        figs.append(fig_resolution)
        
        # 4. Complaints by Category
        category_counts = self.df['category'].value_counts()
        fig_category = px.bar(x=category_counts.index, 
                            y=category_counts.values,
                            title='Complaints by Category',
                            labels={'x': 'Category', 'y': 'Number of Complaints'})
        figs.append(fig_category)
        
        # 5. District-wise Complaints
        district_counts = self.df['district'].value_counts().head(15)
        fig_district = px.bar(x=district_counts.index, 
                            y=district_counts.values,
                            title='Top 15 Districts with Most Complaints',
                            labels={'x': 'District', 'y': 'Number of Complaints'})
        figs.append(fig_district)
        
        # 6. Status Distribution
        fig_status = px.pie(self.df, 
                           names='status',
                           title='Complaint Status Distribution')
        figs.append(fig_status)
        
        # 7. Time Series Analysis
        complaints_over_time = self.df.groupby(self.df['CreatedAt'].dt.date).size().reset_index()
        complaints_over_time.columns = ['Date', 'Count']
        fig_timeline = px.line(complaints_over_time, 
                             x='Date', 
                             y='Count',
                             title='Number of Complaints Over Time')
        figs.append(fig_timeline)
        
        # Update HTML template
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Grievance Analysis Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <h1 style="text-align: center; color: #2c3e50;">Grievance Analysis Dashboard</h1>
    <div style="background-color: #f7f9fc; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
        <h2>Summary Statistics</h2>
        <p>Total Complaints: {total_complaints}</p>
        <p>Average Resolution Time: {avg_resolution:.2f} days</p>
        <p>Most Common Category: {common_category}</p>
        <p>Most Common Status: {common_status}</p>
    </div>
""".format(
            total_complaints=len(self.df),
            avg_resolution=self.df['ResolutionTime'].mean(),
            common_category=self.df['category'].mode()[0],
            common_status=self.df['status'].mode()[0]
        )
        
        # Add each figure to the HTML
        for i, fig in enumerate(figs):
            html_content += f'<div style="margin-bottom: 30px;">{fig.to_html(full_html=False, include_plotlyjs=False)}</div>'
        
        html_content += """
</body>
</html>
"""
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Dashboard has been saved to {output_path}")
        
    def generate_detailed_report(self, output_path):
        """Generate a detailed statistical report"""
        stats = {
            'Total Complaints': len(self.df),
            'Average Resolution Time': f"{self.df['ResolutionTime'].mean():.2f} days",
            'Median Resolution Time': f"{self.df['ResolutionTime'].median():.2f} days",
            'Most Common Category': self.df['category'].mode()[0],
            'Most Common Status': self.df['status'].mode()[0],
            'Total Districts': len(self.df['district'].unique()),
            'High Urgency Cases': len(self.df[self.df['urgencyLevel'] == 'High']),
            'Open Cases': len(self.df[self.df['status'] == 'Open']),
            'Closed Cases': len(self.df[self.df['status'] == 'Closed'])
        }
        
        # Create HTML report
        report_html = """
        <html>
        <head>
            <title>Detailed Grievance Analysis Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .stat-card { 
                    background-color: #f8f9fa;
                    padding: 15px;
                    margin: 10px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .stat-value { 
                    font-size: 24px;
                    color: #2c3e50;
                    font-weight: bold;
                }
                .stat-label {
                    color: #7f8c8d;
                    font-size: 14px;
                }
            </style>
        </head>
        <body>
            <h1>Detailed Grievance Analysis Report</h1>
        """
        
        # Add statistics
        for label, value in stats.items():
            report_html += f"""
            <div class="stat-card">
                <div class="stat-value">{value}</div>
                <div class="stat-label">{label}</div>
            </div>
            """
        
        report_html += "</body></html>"
        
        # Save detailed report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_html)
        
        print(f"Detailed report has been saved to {output_path}")

if __name__ == "__main__":
    # Initialize analyzer
    analyzer = GrievanceAnalyzer('E:\\ML\\Data\\combined_data.csv')
    
    # Generate visualizations
    analyzer.create_dashboard('E:\\ML\\Data\\grievance_dashboard.html')
    
    # Generate detailed report
    analyzer.generate_detailed_report('E:\\ML\\Data\\detailed_report.html')
