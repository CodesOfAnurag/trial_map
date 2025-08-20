import folium
from folium.plugins import MarkerCluster
import pandas as pd
from geopy.distance import geodesic
import os
database_url = os.environ.get('DATABASE_URL')

# User location
class InteractivePropertyMap:
    
    def __init__(self, latitude, longitude, radius):
        self.latitude = latitude
        self.longitude = longitude
        self.user_location = (self.latitude, self.longitude)
        self.radius = radius
        # self.data = pd.read_excel('/Users/anurag/Desktop/work/traumbq_data/scraper_gelbeseiten/prototype/scraped_data.xlsx')
        self.data_path = database_url
        self.data = pd.read_csv(self.data_path)
        self.df = pd.DataFrame(self.data).dropna()
    
    def filter_properties(self):
        filtered = []
        
        for _, row in self.df.iterrows():
            prop_loc = (row['latitude'], row['longitude'])
            distance = geodesic(self.user_location, prop_loc).km
            if distance <= self.radius:
                row = row.to_dict()
                row["distance_km"] = round(distance, 2)
                filtered.append(row)
        
        self.filtered_df = pd.DataFrame(filtered)
         
        self.filtered_df['distance'] = self.filtered_df.apply(lambda row : geodesic(self.user_location, (row['latitude'], row['longitude'])).km, axis = 1)
        self.filtered_df = self.filtered_df.sort_values(by = 'distance')
        
        
    def create_map(self):
        m = folium.Map(location=self.user_location, zoom_start=9)
        marker_cluster = MarkerCluster().add_to(m)

        
        folium.Circle(
            location=self.user_location,
            radius=self.radius * 1000,
            color='blue',
            fill=True,
            fill_opacity=0.1,
            popup=f"<div style='width:150px;'><center><b>Search Radius: </b>{self.radius} km</center></div>"
        ).add_to(m)


        markers_js = []
        for i, row in self.filtered_df.iterrows():
            prop_loc = (row['latitude'], row['longitude'])
            distance = geodesic(self.user_location, prop_loc).km
            
            tooltip_text = f"""
            <div style="width:200px;">
                <b>Name:</b> {row['name']}<br>
                <b>Latitude:</b> {row['latitude']}<br>
                <b>Longitude:</b> {row['longitude']}<br>
                <b>Distance:</b> {distance:.2f} km <br>
                <b>Location:</b> <a href = 'https://maps.google.com/?q={row['latitude']},{row['longitude']}' target="_blank">View on Google Maps</a><br>
            </div>
            """

            marker = folium.Marker(
                location=prop_loc,
                popup=tooltip_text,
                tooltip=row['name']
            )
            
            marker.add_to(marker_cluster)

            markers_js.append(f"""
            window.markers["marker_{i}"] = L.marker([{row['latitude']}, {row['longitude']}])
                .bindPopup({repr(tooltip_text)})
                .addTo(window.{m.get_name()});
            """)
            
        all_markers_js = f"""
        <script>
        window.onload = function() {{
            window.markers = window.markers || {{}};
            var mapObj = window.{m.get_name()};
            {''.join(markers_js)}
        }};
        </script>
        """
        
        side_html = """
        <div style="
            position: fixed;
            top: 50px; right: 20px;
            width: 280px; height: 80%;
            overflow-y: scroll;
            background-color: white;
            padding: 10px;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.3);
            z-index:9999;
            font-size:14px;">
        
        """
        # <h4>Properties in radius</h4>
        if not self.filtered_df.empty:
            for i, row in self.filtered_df.iterrows():
                side_html += f"""
                <div 
                    style="
                    margin-bottom:10px; padding:5px; border-bottom:1px solid #ddd; cursor:pointer;"
                    onclick="flyToMarker({row['latitude']}, {row['longitude']}, 'marker_{i}')"
                    onmouseover="this.style.backgroundColor='#f0f8ff'; this.style.boxShadow='0 2px 5px rgba(0,0,0,0.2)';"
                    onmouseout="this.style.backgroundColor=''; this.style.boxShadow='';">
                    <b>{row['name']}</b><br>
                    Latitude: {row['latitude']}<br>
                    Longitude: {row['longitude']}<br>
                    Distance: {row['distance_km']} km
                </div>
                """

        # else:
        #     side_html += "<p>No properties found in this area.</p>"
        side_html += "</div>"

        flyto_js = f"""
        <script>
        function flyToMarker(lat, lon, markerId) {{
            var marker = window.markers[markerId];
            var mapObj = window.{m.get_name()};
            mapObj.setView([lat, lon], 12); 
            console.log(markerId);
            console.log(marker);
            console.log(window.markers);
            marker.fire('click');
        }}
        </script>
        """

        m.get_root().html.add_child(folium.Element(all_markers_js))
        m.get_root().html.add_child(folium.Element(flyto_js))
        m.get_root().html.add_child(folium.Element(side_html))
        
        folium.Marker(
            location=self.user_location,
            icon=folium.Icon(color='red', icon='user'),
            popup=f"""
            <div style="width:120px;">
            <center>
                <b>Marked Location</b>
                <br><b>Latitude:</b> {self.user_location[0]}<br>
                <b>Longitude::</b> {self.user_location[1]}
            </center>
            </div>"""
        ).add_to(m)

        self.map_str = m._repr_html_()


if __name__ == '__main__':
    map = InteractivePropertyMap(51.152634, 11.801068, 150)
    map.filter_properties()
    map.create_map()


    with open('map_final.html', 'w') as file:
        file.write(map.map_str)
    


