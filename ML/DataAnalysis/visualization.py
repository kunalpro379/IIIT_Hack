import pandas as pd
import folium
import json
from collections import defaultdict
import os
from folium import plugins
import branca.colormap as cm

def load_data():
    # Set up correct file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', 'Data')
    csv_path = os.path.join(data_dir, 'combined_data.csv')
    geojson_path = os.path.join(data_dir, 'UttarPradesh.geojson')  # Updated path

    # Read the data
    try:
        df = pd.read_csv(csv_path)
        print(f"Successfully loaded CSV from: {csv_path}")
    except FileNotFoundError:
        print(f"Error: Could not find CSV file at {csv_path}")
        print("Please ensure the data file exists at the correct location")
        exit(1)

    try:
        with open(geojson_path, 'r') as f:
            up_geojson = json.load(f)
        print(f"Successfully loaded GeoJSON from: {geojson_path}")
    except FileNotFoundError:
        print(f"Error: Could not find GeoJSON file at {geojson_path}")
        print("Please ensure the UP boundary file exists at the correct location")
        exit(1)

    return df, up_geojson

def create_filtered_stats(df, analysis_type):
    """Create statistics based on selected analysis type"""
    stats = defaultdict(lambda: {'total': 0, 'details': defaultdict(int)})
    
    for _, row in df.iterrows():
        district = row['location'].split(',')[0].strip()
        stats[district]['total'] += 1
        
        # Map analysis type to corresponding column
        value_map = {
            'Category': row['category'],
            'Status': row['status'],
            'Urgency': row['urgencyLevel'],
            'Department': row['departmentAssigned'],
            'Economic Impact': row['economicImpact'],
            'Social Impact': row['socialImpact'],
            'Environmental Impact': row['environmentalImpact']
        }
        
        stats[district]['details'][value_map[analysis_type]] += 1
    
    return stats

def create_map(df, up_geojson):
    # Initialize base map centered on UP with tighter bounds
    m = folium.Map(
        location=[26.8467, 80.9462],
        zoom_start=7,
        tiles='CartoDB positron',
        control_scale=True,
        prefer_canvas=True,
        max_bounds=True,  # Restrict panning
        min_zoom=6,      # Restrict zoom out
        max_zoom=10      # Restrict zoom in
    )

    # Add district statistics collection
    district_stats = defaultdict(lambda: {
        'total': 0,
        'details': defaultdict(int)
    })
    
    for _, row in df.iterrows():
        district = row['location'].split(',')[0].strip()
        district_stats[district]['total'] += 1
        district_stats[district]['details'][row['category']] += 1

    # Create choropleth with enhanced smooth boundaries
    choropleth = folium.Choropleth(
        geo_data=up_geojson,
        name='Uttar Pradesh',
        data={k: v['total'] for k, v in district_stats.items()},
        key_on='feature.properties.Name',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.4,
        highlight=True,
        smooth_factor=2.5,  # Increased smoothing
        legend_name='Number of Grievances'
    ).add_to(m)

    # Add district boundaries with improved styling
    for feature in up_geojson['features']:
        district_name = feature['properties']['Name']
        if district_name in district_stats:
            stats = district_stats[district_name]
            
            # Enhanced popup styling
            popup_html = f"""
            <div class="district-popup" data-district="{district_name}" style="font-family: Arial; min-width: 250px;">
                <h3 style="color: #2c3e50; margin-bottom: 10px; border-bottom: 2px solid #3498db; padding-bottom: 5px;">
                    {district_name}
                </h3>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <p style="font-size: 16px; color: #2c3e50;"><b>Total Grievances:</b> {stats['total']}</p>
                    <hr style="margin: 10px 0; border: none; border-top: 1px solid #e0e0e0;">
                    <h4 style="color: #34495e; margin: 10px 0;">Category Breakdown:</h4>
                    {''.join(
                        f'<div style="margin: 8px 0; display: flex; justify-content: space-between;">'
                        f'<span style="color: #2c3e50;"><b>{cat}:</b></span>'
                        f'<span>{count} ({count/stats["total"]*100:.1f}%)</span>'
                        f'</div>'
                        for cat, count in sorted(stats['details'].items(), key=lambda x: x[1], reverse=True)
                    )}
                </div>
            </div>
            """

            # Add district boundaries with enhanced smooth edges
            folium.GeoJson(
                feature,
                style_function=lambda x: {
                    'fillColor': 'none',
                    'color': '#34495e',
                    'weight': 1.2,
                    'opacity': 0.7,
                    'smoothFactor': 2.5  # Increased smoothing
                },
                highlight_function=lambda x: {
                    'color': '#3498db',
                    'weight': 2,
                    'opacity': 1,
                    'fillOpacity': 0.2,
                    'smoothFactor': 2.5
                },
                popup=folium.Popup(popup_html, max_width=350)
            ).add_to(m)

    # Set map bounds to UP boundaries
    bounds = folium.GeoJson(up_geojson).get_bounds()
    m.fit_bounds(bounds)

    # Add selection control HTML
    selection_html = """
    <div id="selection-control" style="position: fixed; top: 10px; right: 10px; background: white; padding: 10px; z-index: 1000; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.2);">
        <h4 style="margin-bottom: 10px;">Analysis Type</h4>
        <select id="analysis-select" onchange="updateMap(this.value)" style="width: 200px; padding: 5px;">
            <option value="Category">Category</option>
            <option value="Status">Status</option>
            <option value="Urgency">Urgency Level</option>
            <option value="Department">Department</option>
            <option value="Economic">Economic Impact</option>
            <option value="Social">Social Impact</option>
            <option value="Environmental">Environmental Impact</option>
        </select>
        <div id="stats" style="margin-top: 10px;"></div>
    </div>
    
    <script>
    function updateMap(analysisType) {
        // Store all district data
        const districtData = {
    """
    
    # Generate JavaScript data object
    js_data = {}
    analysis_types = {
        'Category': 'category',
        'Status': 'status',
        'Urgency': 'urgencyLevel',
        'Department': 'departmentAssigned',
        'Economic': 'economicImpact',
        'Social': 'socialImpact',
        'Environmental': 'environmentalImpact'
    }
    
    for district in df['location'].str.split(',').str[0].unique():
        js_data[district] = {}
        district_df = df[df['location'].str.startswith(district)]
        
        for analysis_type, column in analysis_types.items():
            counts = district_df[column].value_counts().to_dict()
            js_data[district][analysis_type] = {
                'total': len(district_df),
                'details': counts
            }
    
    selection_html += f"districtData: {json.dumps(js_data)},\n"
    
    selection_html += """
        };
        
        // Update popups and colors based on selection
        document.querySelectorAll('.district-popup').forEach(popup => {
            const district = popup.getAttribute('data-district');
            const data = districtData[district][analysisType];
            
            // Update popup content
            let content = `<h4>${district}</h4>`;
            content += `<p>Total: ${data.total}</p>`;
            for (let [key, value] of Object.entries(data.details)) {
                content += `<p>${key}: ${value} (${((value/data.total)*100).toFixed(1)}%)</p>`;
            }
            popup.innerHTML = content;
        });
        
        // Update stats panel
        let totalGrievances = 0;
        let categoryTotals = {};
        Object.values(districtData).forEach(district => {
            const data = district[analysisType];
            totalGrievances += data.total;
            Object.entries(data.details).forEach(([key, value]) => {
                categoryTotals[key] = (categoryTotals[key] || 0) + value;
            });
        });
        
        let statsHtml = `<h4>Overall Statistics</h4>`;
        statsHtml += `<p>Total Grievances: ${totalGrievances}</p>`;
        Object.entries(categoryTotals)
            .sort((a, b) => b[1] - a[1])
            .forEach(([key, value]) => {
                statsHtml += `<p>${key}: ${value} (${((value/totalGrievances)*100).toFixed(1)}%)</p>`;
            });
        
        document.getElementById('stats').innerHTML = statsHtml;
    }
    
    // Initialize with Category analysis
    updateMap('Category');
    </script>
    """
    
    m.get_root().html.add_child(folium.Element(selection_html))

    # Add interactive features
    plugins.Fullscreen().add_to(m)
    folium.LayerControl().add_to(m)
    
    return m

def main():
    df, up_geojson = load_data()
    m = create_map(df, up_geojson)
    m.save('up_grievances_dashboard.html')
    print("Generated interactive dashboard as 'up_grievances_dashboard.html'")

if __name__ == "__main__":
    main()
