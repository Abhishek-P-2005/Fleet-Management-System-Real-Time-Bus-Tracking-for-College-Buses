import requests
import time
import json
import os
from geopy.distance import geodesic

BUS_ID = "BUS-AD01"
MAX_OCCUPANCY = 40
speed = 30
occupancy = 0
fuel_litres = 30.0
SERVER_URL = "http://127.0.0.1:5000/update-bus"
ROUTE_FOLDER = r"D:\Abhishek Projects\bus-tracker\server\static\routes\adyar_route"
TOTAL_SEGMENTS = 10

segment_stops = [
    "Adyar", "Besant Nagar", "Thiruvanmiyur", "Perungudi", "Thoraipakkam",
    "Sholinganallur", "Navalur", "Kelambakkam", "Pudupakkam",
    "Tagore College", "VIT Chennai"
]

def load_route_points():
    all_points = []
    segment_boundaries = []
    for i in range(1, TOTAL_SEGMENTS + 1):
        seg_file = os.path.join(ROUTE_FOLDER, f"segment{i}.json")
        with open(seg_file, "r") as f:
            seg_data = json.load(f)
            seg_points = seg_data["points"]

            all_points.extend(seg_points)
            segment_boundaries.append(len(all_points) - 1)  # last index of each segment
    return all_points, segment_boundaries

def simulate_bus():
    global occupancy, fuel_litres
    route_points, segment_boundaries = load_route_points()
    num_points = len(route_points)

    completed_stops = 0
    previous_point = None

    for index, point in enumerate(route_points):
        # Fuel consumption per step
        if previous_point:
            step_km = geodesic(
                (previous_point["lat"], previous_point["lng"]),
                (point["lat"], point["lng"])
            ).km
            fuel_litres = max(fuel_litres - step_km * 0.25, 0)

        # Occupancy simulation
        if index % 25 == 0 and occupancy < MAX_OCCUPANCY:
            occupancy += 1

        # Stop completion update
        if index in segment_boundaries and completed_stops < TOTAL_SEGMENTS:
            completed_stops += 1

        stops_completed = f"{completed_stops}/{TOTAL_SEGMENTS}"

        # Current & next stops
        if completed_stops < TOTAL_SEGMENTS:
            current_stop = segment_stops[completed_stops]
            next_stop = segment_stops[completed_stops + 1]
        else:
            current_stop = segment_stops[-1]
            next_stop = "End of Route"

        # Distance to next & final
        if completed_stops < TOTAL_SEGMENTS:
            next_stop_point = route_points[segment_boundaries[completed_stops]]
            distance_to_next_km = geodesic(
                (point["lat"], point["lng"]),
                (next_stop_point["lat"], next_stop_point["lng"])
            ).km
            final_stop_point = route_points[segment_boundaries[-1]]
            distance_to_final_km = geodesic(
                (point["lat"], point["lng"]),
                (final_stop_point["lat"], final_stop_point["lng"])
            ).km
        else:
            distance_to_next_km = 0.0
            distance_to_final_km = 0.0

        # Prepare update payload
        data = {
            "bus_id": BUS_ID,
            "route_name": "Adyar Route",
            "lat": point["lat"],
            "lng": point["lng"],
            "speed_kmph": 0 if completed_stops >= TOTAL_SEGMENTS else speed,
            "occupancy": occupancy,
            "max_capacity": MAX_OCCUPANCY,
            "status": "arrived" if completed_stops >= TOTAL_SEGMENTS else "running",
            "current_stop": current_stop,
            "next_stop": next_stop,
            "stops_completed": stops_completed,
            "distance_to_next_km": round(distance_to_next_km, 2),
            "distance_to_final_km": round(distance_to_final_km, 2),
            "fuel_litres": round(fuel_litres, 2)
        }

        # ✅ One clean debug line
        print(f"SIM UPDATE: Stop {stops_completed} | {current_stop} → {next_stop} | "
              f"Next: {distance_to_next_km:.2f} km | Final: {distance_to_final_km:.2f} km | "
              f"Fuel: {fuel_litres:.2f}L")

        # Send update to server
        requests.post(SERVER_URL, json=data)

        # Break after arrival
        if completed_stops >= TOTAL_SEGMENTS:
            print(f"✅ {BUS_ID} has arrived at {segment_stops[-1]}")
            break

        previous_point = point
        time.sleep(0.5)

if __name__ == "__main__":
    simulate_bus()
