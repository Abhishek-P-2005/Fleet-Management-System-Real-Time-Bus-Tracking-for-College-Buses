from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import time

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

# Store bus data
buses = {}

# -------- APIs --------

@app.route("/update-bus", methods=["POST"])
def update_bus():
    data = request.get_json()
    bus_id = data.get("bus_id")
    if not bus_id:
       return jsonify({"error": "bus_id missing"}), 400

    data["last_updated"] = time.time()
    buses[bus_id] = data

    # ✅ Compact debug log
    print(f"SERVER RECEIVED: {bus_id} | Stops: {data.get('stops_completed')}")

    return jsonify({"status": "success"}), 200

@app.route("/buses", methods=["GET"])
def get_all_buses():
    enriched = []
    for bus in buses.values():
        bus_copy = dict(bus)
        speed = bus_copy.get("speed_kmph", 0)
        dist_next = bus_copy.get("distance_to_next_km", 0)

        # ETA (next stop)
        if speed > 0:
            eta_min = (dist_next / speed) * 60
            bus_copy["eta_min"] = round(eta_min, 1)
        else:
            bus_copy["eta_min"] = None

        # ✅ Preserve stops_completed from simulator
        if "stops_completed" not in bus_copy:
            route_name = bus_copy.get("route_name", "")
            total_segments = 0
            if "Adyar" in route_name:
                total_segments = 10
            elif "Chengalpattu" in route_name:
                total_segments = 7
            elif "Mylapore" in route_name:
                total_segments = 7
            elif "T Nagar" in route_name:
                total_segments = 9
            bus_copy["stops_completed"] = f"0/{total_segments}"

        # Ensure distance_to_final_km exists
        if bus_copy.get("distance_to_final_km") is None and dist_next:
            bus_copy["distance_to_final_km"] = round(dist_next, 2)

        enriched.append(bus_copy)

    # ✅ Compact debug log
    print("SERVER SENDING:", [(b["bus_id"], b["stops_completed"]) for b in enriched])

    return jsonify(enriched), 200

# -------- Frontend Routes --------

@app.route("/")
def serve_index():
    return send_from_directory("../frontend", "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("../frontend", path)

if __name__ == "__main__":
    app.run(debug=True)
