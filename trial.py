
from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

LOCATION_FILE = "user_location.json"


def save_location(lat, lon):
    """Save location to local JSON file"""
    data = {"latitude": lat, "longitude": lon}
    with open(LOCATION_FILE, "w") as f:
        json.dump(data, f)
    return data


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        lat = request.form.get("latitude")
        lon = request.form.get("longitude")
        if lat and lon:
            save_location(float(lat), float(lon))
            return render_template("index.html", message="Location saved successfully!")
    return render_template("index.html", message=None)


@app.route("/save_location", methods=["POST"])
def save_location_api():
    """AJAX endpoint to save location via JS (geolocation)"""
    data = request.json
    lat = data.get("latitude")
    lon = data.get("longitude")
    if lat and lon:
        saved = save_location(float(lat), float(lon))
        return jsonify({"status": "success", "saved": saved})
    return jsonify({"status": "error", "message": "Invalid data"}), 400


@app.route("/get_location")
def get_location():
    """Return last saved location"""
    if os.path.exists(LOCATION_FILE):
        with open(LOCATION_FILE, "r") as f:
            data = json.load(f)
        return jsonify(data)
    return jsonify({"message": "No location saved"}), 404


if __name__ == "__main__":
    
    app.run(debug=True)

