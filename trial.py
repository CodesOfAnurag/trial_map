#############################################################
# Show Map Code
#############################################################

from flask import Flask, render_template
import folium
import pandas as pd
import os

app = Flask(__name__)

# Example dataframe (replace with your data)
data = pd.DataFrame({
    "name": ["Property A", "Property B", "Property C"],
    "lat": [12.9716, 12.9352, 12.9985],
    "lon": [77.5946, 77.6245, 77.5671],
    "price": [100000, 150000, 200000]
})


@app.route("/")
def index():
    # Center map around Bangalore
    start_coords = (12.9716, 77.5946)
    m = folium.Map(location=start_coords, zoom_start=12)

    # Add markers from dataframe
    for _, row in data.iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            tooltip=f"{row['name']} - ${row['price']}"
        ).add_to(m)

    # Save map as HTML string
    map_html = m._repr_html_()

    # Pass dataframe records for side pane
    properties = data.to_dict(orient="records")

    return render_template("index.html", map_html=map_html, properties=properties)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


#############################################################
# Get Location Code
#############################################################

# from flask import Flask, render_template, request, jsonify
# import json
# import os

# app = Flask(__name__)

# LOCATION_FILE = "user_location.json"


# def save_location(lat, lon):
#     """Save location to local JSON file"""
#     data = {"latitude": lat, "longitude": lon}
#     print(f'{lat} {lon}', flush=True)
#     with open(LOCATION_FILE, "w") as f:
#         json.dump(data, f)
#     return data


# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         lat = request.form.get("latitude")
#         lon = request.form.get("longitude")
#         if lat and lon:
#             save_location(float(lat), float(lon))
#             return render_template("index.html", message="Location saved successfully!")
#     return render_template("index.html", message=None)


# @app.route("/save_location", methods=["POST"])
# def save_location_api():
#     """AJAX endpoint to save location via JS (geolocation)"""
#     data = request.json
#     lat = data.get("latitude")
#     lon = data.get("longitude")
#     if lat and lon:
#         saved = save_location(float(lat), float(lon))
#         return jsonify({"status": "success", "saved": saved})
#     return jsonify({"status": "error", "message": "Invalid data"}), 400


# @app.route("/get_location")
# def get_location():
#     """Return last saved location"""
#     if os.path.exists(LOCATION_FILE):
#         with open(LOCATION_FILE, "r") as f:
#             data = json.load(f)
#         return jsonify(data)
#     return jsonify({"message": "No location saved"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)


