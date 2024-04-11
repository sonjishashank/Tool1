from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import pandas as pd
import plotly.graph_objects as go

app = Flask(__name__)
CORS(app)

# Connect to your PostgreSQL database
def connect_to_postgresql():
    connection = psycopg2.connect(
        host="aws-0-ap-southeast-1.pooler.supabase.com",
        database="postgres",
        user="postgres.faatiflkdkozhenblufj",
        password="##Sonji@2534##"
    )
    return connection

# Function to fetch data from PostgreSQL
def fetch_data_from_postgresql(district_name):
    connection = connect_to_postgresql()
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM tool1 WHERE District_Name = '{district_name}';")
    data = cursor.fetchall()
    print(data)  # Print fetched data for debugging
    cursor.close()
    connection.close()
    return data



@app.route('/crime_visualizations/<district>', methods=['GET'])
def generate_crime_visualizations(district):
    data = fetch_data_from_postgresql(district)
    if not data:
        return jsonify({'message': f"No data available for district: {district}"}), 404

    df = pd.DataFrame(data, columns=['district_name', 'latitude', 'longitude', 'crimetype', 'fir_type'])

    center = {
        'lat': df['latitude'].mean(),
        'lon': df['longitude'].mean()
    }

    # Plot Crime Map
    fig_map = go.Figure(go.Scattermapbox(
        lat=df['latitude'],
        lon=df['longitude'],
        mode='markers',
        marker=go.scattermapbox.Marker(size=9),
        text=df['fir_type']
    ))

    fig_map.update_layout(
        mapbox_style='open-street-map',
        mapbox_center=center,
        mapbox_zoom=10,
        height=800,
        width=1000,
        title=f"Crime Map for {district}"
    )

    # Plot Heatmap
    fig_heatmap = go.Figure(go.Densitymapbox(
        lat=df['latitude'],
        lon=df['longitude'],
        radius=10,
        opacity=0.8,
        colorscale='Viridis',
        zmin=0,
        text=df['fir_type']
    ))

    fig_heatmap.update_layout(
        mapbox_style='open-street-map',
        mapbox_center=center,
        mapbox_zoom=10,
        height=800,
        width=1000,
        title=f"Crime Heatmap for {district}"
    )

    return jsonify({'crime_map': fig_map.to_json(), 'crime_heatmap': fig_heatmap.to_json()})
