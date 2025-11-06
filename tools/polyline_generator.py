# polyline_generator.py

import os
import sys
import json
import requests
import time
from urllib.parse import urlencode

# ========== INPUT & VALIDATION ========== #
if len(sys.argv) < 2:
    print("❗ Please provide the input JSON file. Example:")
    print("   python polyline_generator.py input_segments_tnagar.json")
    exit(1)

INPUT_FILE = sys.argv[1]

# Extract route name from input file name (e.g., tnagar, mylapore)
route_name = os.path.splitext(os.path.basename(INPUT_FILE))[0].replace("input_segments_", "")
OUTPUT_BASE = f"routes/{route_name}_route/"
API_URL = "https://maps.googleapis.com/maps/api/directions/json"
API_KEY = "AIzaSyCTZCqSQDe4kTYPPPDTCUmBbTirh61CqoU"  # <-- Your actual key

# ========== DECODE POLYLINE FUNCTION ========== #
def decode_polyline(polyline_str):
    index, lat, lng, coordinates = 0, 0, 0, []
    while index < len(polyline_str):
        result, shift = 0, 0
        while True:
            b = ord(polyline_str[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat

        result, shift = 0, 0
        while True:
            b = ord(polyline_str[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        dlng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += dlng

        coordinates.append({
            "lat": lat / 1e5,
            "lng": lng / 1e5
        })
    return coordinates

# ========== MAIN FUNCTION ========== #
def generate_polylines():
    start_time = time.time()
    print("\n🔁 Generating polylines from:", INPUT_FILE)

    with open(INPUT_FILE, "r") as file:
        segments = json.load(file)

    for idx, segment in enumerate(segments):
        origin = segment["from"]
        destination = segment["to"]
        output_file = os.path.join(OUTPUT_BASE, segment["file"])

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        params = {
            "origin": origin,
            "destination": destination,
            "key": API_KEY
        }

        print(f"\n📍 [{idx + 1}/{len(segments)}] {origin} → {destination}")

        try:
            response = requests.get(f"{API_URL}?{urlencode(params)}")
            result = response.json()

            if result.get("status") != "OK":
                print("❌ Failed to fetch directions:", result.get("status"))
                continue

            route_data = result["routes"][0]
            polyline = route_data["overview_polyline"]["points"]
            decoded = decode_polyline(polyline)

            duration = route_data["legs"][0]["duration"]["value"]  # in seconds

            with open(output_file, "w") as f:
                json.dump({
                    "duration": duration,
                    "points": decoded
                }, f, indent=2)

            print(f"✅ Saved {len(decoded)} points, duration: {duration}s → {output_file}")

        except Exception as e:
            print("⚠️  Error:", e)

        time.sleep(1)

        if (time.time() - start_time) >= 60:
            print("⏳ Progress Update:", idx + 1, "segments processed.")
            start_time = time.time()

if __name__ == "__main__":
    generate_polylines()
