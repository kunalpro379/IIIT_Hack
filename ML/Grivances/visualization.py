import pandas as pd
import folium
import json
from folium import plugins

# Read the data
df = pd.read_csv('final_dataset/combined_data.csv')
with open('final_dataset/UttarPradesh.geojson', 'r') as f:
    up_geojson = json.load(f)

# Create a base map centered on UP
m = folium.Map(location=[26.8467, 80.9462], zoom_start=7)

# Add the UP boundary
folium.GeoJson(
    up_geojson,
    name='UP Boundary',
    style_function=lambda x: {
        'fillColor': '#ffff00',
        'color': 'black',
        'weight': 2,
        'fillOpacity': 0.1
    }
).add_to(m)

# Create a marker cluster
marker_cluster = plugins.MarkerCluster().add_to(m)

# Add markers for each grievance
for idx, row in df.iterrows():
    # Check if coordinates are available
    if pd.notna(row['gpscoordinates_latitude']) and pd.notna(row['gpscoordinates_longitude']):
        # Create popup content
        popup_content = f"""
        <b>Location:</b> {row['location']}<br>
        <b>Category:</b> {row['category']}<br>
        <b>Complaint Type:</b> {row['complaintType']}<br>
        <b>Status:</b> {row['status']}<br>
        <b>Urgency Level:</b> {row['urgencyLevel']}<br>
        <b>Economic Impact:</b> {row['economicImpact']}<br>
        <b>Social Impact:</b> {row['socialImpact']}<br>
        <b>Environmental Impact:</b> {row['environmentalImpact']}<br>
        <b>Department:</b> {row['departmentAssigned']}<br>
        <b>Complaint:</b> {row['complaint'][:100]}...<br>
        """

        # Create marker
        folium.Marker(
            location=[row['gpscoordinates_latitude'], row['gpscoordinates_longitude']],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"{row['category']} - {row['status']}",
            icon=folium.Icon(
                color='red' if row['status'] == 'Open' else 'green' if row['status'] == 'Closed' else 'orange',
                icon='info-sign'
            )
        ).add_to(marker_cluster)

# Add a layer control
folium.LayerControl().add_to(m)

# Save the map
m.save('grievances_map.html')

print("Map has been generated as 'grievances_map.html'")
