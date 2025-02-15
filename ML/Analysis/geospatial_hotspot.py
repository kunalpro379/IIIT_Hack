import pandas as pd
import folium
from folium import plugins
import keplergl
from sklearn.cluster import DBSCAN
import numpy as np
from shapely.geometry import Point
import geopandas as gpd
import json

# Load data
df = pd.read_csv('/e:/ML/DataAnalysis/combined_data.csv')

def create_base_map():
    """Create base map centered on UP"""
    return folium.Map(location=[26.8467, 80.9462], 
                     zoom_start=7,
                     tiles='CartoDB positron')

def identify_hotspots():
    """Identify complaint hotspots using DBSCAN"""
    # Prepare coordinates
    coords = df[['gpscoordinates_latitude', 'gpscoordinates_longitude']].values
    
    # Run DBSCAN
    clustering = DBSCAN(eps=0.1, min_samples=5).fit(coords)
    
    # Add cluster labels to dataframe
    df['cluster'] = clustering.labels_
    
    return df

def create_heatmap():
    """Create heatmap of complaints"""
    base_map = create_base_map()
    
    # Prepare heatmap data
    heat_data = df[['gpscoordinates_latitude', 'gpscoordinates_longitude']].values.tolist()
    
    # Add heatmap layer
    plugins.HeatMap(heat_data).add_to(base_map)
    base_map.save('/e:/ML/Analysis/complaint_heatmap.html')
    
    return base_map

def create_kepler_visualization():
    """Create interactive Kepler.gl visualization"""
    # Convert to GeoDataFrame
    geometry = [Point(xy) for xy in zip(df['gpscoordinates_longitude'], 
                                      df['gpscoordinates_latitude'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry)
    
    # Create Kepler map
    map_1 = keplergl.KeplerGl(height=600)
    map_1.add_data(data=gdf, name='complaints')
    
    # Save map
    map_1.save_to_html(file_name='/e:/ML/Analysis/kepler_map.html')

def analyze_spatial_patterns():
    """Analyze spatial patterns in complaints"""
    # Calculate complaint density by district
    district_density = df.groupby('district').agg({
        'id': 'count',
        'urgencyLevel': lambda x: (x == 'High').mean(),
        'ResolutionTime': 'mean'
    }).reset_index()
    
    # Identify high-risk areas
    high_risk = district_density[
        (district_density['id'] > district_density['id'].mean()) &
        (district_density['urgencyLevel'] > district_density['urgencyLevel'].mean())
    ]
    
    return district_density, high_risk

def generate_resource_recommendations(high_risk_areas):
    """Generate AI-powered resource allocation recommendations"""
    summary = {
        'high_risk_areas': high_risk_areas.to_dict(orient='records'),
        'total_districts': len(df['district'].unique()),
        'complaint_distribution': df['district'].value_counts().to_dict()
    }
    
    prompt = f"""
    Based on this spatial analysis of complaints:
    {json.dumps(summary, indent=2)}
    
    Provide recommendations for:
    1. Resource allocation in high-risk areas
    2. Infrastructure improvements needed
    3. Preventive measures for hotspots
    4. Long-term development strategies
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def create_spatial_report():
    """Generate comprehensive spatial analysis report"""
    # Perform analyses
    df_clustered = identify_hotspots()
    district_density, high_risk = analyze_spatial_patterns()
    
    # Create visualizations
    create_heatmap()
    create_kepler_visualization()
    
    # Generate recommendations
    recommendations = generate_resource_recommendations(high_risk)
    
    # Save report
    with open('/e:/ML/Analysis/spatial_analysis_report.md', 'w') as f:
        f.write("# Geospatial Analysis Report\n\n")
        
        f.write("## High-Risk Areas\n")
        for _, area in high_risk.iterrows():
            f.write(f"- {area['district']}: {area['id']} complaints\n")
        
        f.write("\n## District-wise Analysis\n")
        f.write(str(district_density.describe()) + "\n\n")
        
        f.write("## Recommendations\n")
        f.write(recommendations)

if __name__ == "__main__":
    print("Starting geospatial analysis...")
    create_spatial_report()
    print("Analysis completed! Check the reports and visualizations.")
