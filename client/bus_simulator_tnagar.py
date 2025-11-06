import requests
import time
import os
import json
from geopy.distance import geodesic

# ✅ Config
BUS_ID = "BUS-TN01"
ROUTE_FOLDER = r"D:\Abhishek Projects\bus-tracker\server\static\routes\tnagar_route"
SERVER_URL = "http://127.0.0.1:5000/update-bus"
MAX_OCCUPANCY = 40
FUEL_START = 30.0

# ✅ Route details
TOTAL_SEGMENTS = 9
segment_stops = [
    "T Nagar",
    "Saidapet",
    "Guindy",
    "Velachery",
    "Balaji Dental College",
    "Medavakkam Junction",
    "Sholinganallur",
    "Navalur",
    "Kelambakkam",
    "VIT Chennai"
]

def load_route_points():
    route_points = []
    segment_boundaries = [0]
    for i in range(1, TOTAL_SEGMENTS + 1):
        seg_file = os.path.join(ROUTE_FOLDER, f"segment{i}.json")
        with open(seg_file, "r") as f:
            segment = json.load(f)
            route_points.extend(segment["points"])
            segment_boundaries.append(len(route_points))
    return route_points, segment_boundaries

def simulate_bus():
    occupancy = 0
    fuel_litres = FUEL_START
    speed = 30
    completed_stops = 0

    route_points, segment_boundaries = load_route_points()
    TOTAL_POINTS = len(route_points)
    previous_point = None

    for idx, point in enumerate(route_points):
        # Fuel consumption
        if previous_point:
            distance_km = geodesic(
                (previous_point["lat"], previous_point["lng"]),
                (point["lat"], point["lng"])
            ).km
            fuel_litres -= distance_km * 0.25
            fuel_litres = max(fuel_litres, 0)

        # Occupancy growth
        if idx % 25 == 0 and occupancy < MAX_OCCUPANCY:
            occupancy += 1

        # Find current segment
        segment_index = next((i for i, b in enumerate(segment_boundaries) if idx < b), TOTAL_SEGMENTS) - 1

        # Stops completed
        if idx == segment_boundaries[completed_stops + 1] - 1 and completed_stops < TOTAL_SEGMENTS:
            completed_stops += 1

        current_stop = segment_stops[segment_index]
        next_stop = segment_stops[min(segment_index + 1, len(segment_stops) - 1)]

        # Distance to next stop
        next_stop_idx = min(segment_boundaries[segment_index + 1] - 1, TOTAL_POINTS - 1)
        next_stop_point = route_points[next_stop_idx]
        distance_to_next_km = geodesic(
            (point["lat"], point["lng"]),
            (next_stop_point["lat"], next_stop_point["lng"])
        ).km

        # Distance to final stop
        distance_to_final_km = distance_to_next_km
        for seg_idx in range(segment_index + 1, TOTAL_SEGMENTS):
            seg_start = route_points[segment_boundaries[seg_idx] - 1]
            seg_end = route_points[segment_boundaries[seg_idx + 1] - 1]
            distance_to_final_km += geodesic(
                (seg_start["lat"], seg_start["lng"]),
                (seg_end["lat"], seg_end["lng"])
            ).km

        # Data payload
        data = {
            "bus_id": BUS_ID,
            "route_name": "T Nagar Route",
            "lat": point["lat"],
            "lng": point["lng"],
            "speed_kmph": speed,
            "occupancy": occupancy,
            "max_capacity": MAX_OCCUPANCY,
            "status": "running" if completed_stops < TOTAL_SEGMENTS else "arrived",
            "current_stop": current_stop,
            "next_stop": next_stop,
            "stops_completed": f"{completed_stops}/{TOTAL_SEGMENTS}",
            "distance_to_next_km": round(distance_to_next_km, 2),
            "distance_to_final_km": round(distance_to_final_km, 2),
            "fuel_litres": round(fuel_litres, 2)
        }

        try:
            requests.post(SERVER_URL, json=data)
            print(f"[{idx+1}/{TOTAL_POINTS}] {current_stop} → {next_stop} | Stops: {completed_stops}/{TOTAL_SEGMENTS} | Dist→Next: {distance_to_next_km:.2f} km | Fuel: {fuel_litres:.2f}L")
        except Exception as e:
            print("❌ Failed to send update:", e)

        previous_point = point
        time.sleep(0.5)

if __name__ == "__main__":
    simulate_bus()
