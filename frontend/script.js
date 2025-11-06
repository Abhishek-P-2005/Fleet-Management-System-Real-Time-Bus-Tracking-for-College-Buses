let map;
let busMarkers = {};
let alertBox;

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 12,
    center: { lat: 13.0358, lng: 80.2442 },
  });

  alertBox = document.getElementById("alerts");
  fetchBusPositions();
  setInterval(fetchBusPositions, 3000);

  document.getElementById("dashboardBtn").addEventListener("click", toggleDashboard);
}

function fetchBusPositions() {
  fetch("http://127.0.0.1:5000/buses")
    .then(res => res.json())
    .then(data => {
      updateMap(data);
      updateDashboard(data);
      checkLowFuelAlerts(data);
    })
    .catch(err => console.error("❌ Failed to fetch buses:", err));
}

function updateMap(data) {
  data.forEach(bus => {
    const { bus_id, lat, lng, occupancy, max_capacity, speed_kmph, current_stop, next_stop, distance_to_next_km, fuel_litres, eta_min } = bus;
    const newPos = { lat, lng };

    const shortLabel = `🚌 ${bus_id}`;
    const fullLabel = `
      <b>${bus_id}</b><br>
      📍 ${current_stop} → ${next_stop}<br>
      📏 ${distance_to_next_km?.toFixed(2)} km<br>
      ⏱ ETA: ${eta_min ? eta_min + " min" : "N/A"}<br>
      👥 ${occupancy}<br>
      ⛽ ${fuel_litres?.toFixed(2)} L
    `;

    let iconUrl = "https://maps.google.com/mapfiles/ms/icons/green-dot.png";
    if (fuel_litres < 7) {
      iconUrl = "https://maps.google.com/mapfiles/ms/icons/red-dot.png";
    } else if ((occupancy / max_capacity) * 100 > 80) {
      iconUrl = "https://maps.google.com/mapfiles/ms/icons/yellow-dot.png";
    }

    if (busMarkers[bus_id]) {
      busMarkers[bus_id].setPosition(newPos);
      busMarkers[bus_id].info.setContent(fullLabel);
      busMarkers[bus_id].setLabel(shortLabel);
      busMarkers[bus_id].setIcon({ url: iconUrl, scaledSize: new google.maps.Size(40, 40) });
    } else {
      const marker = new google.maps.Marker({
        position: newPos,
        map,
        label: shortLabel,
        icon: { url: iconUrl, scaledSize: new google.maps.Size(40, 40) },
      });
      const infoWindow = new google.maps.InfoWindow({ content: fullLabel });
      marker.addListener("click", () => infoWindow.open(map, marker));
      marker.info = infoWindow;
      busMarkers[bus_id] = marker;
    }
  });
}

function checkLowFuelAlerts(data) {
  alertBox.innerHTML = "";
  data.forEach(bus => {
    if (bus.fuel_litres < 7) {
      const div = document.createElement("div");
      div.className = "alert";
      div.innerHTML = `🚨 Low Fuel Alert: ${bus.bus_id}<br>Fuel: ${bus.fuel_litres} L<br>Stop: ${bus.current_stop}`;
      alertBox.appendChild(div);
    }
  });
}

function toggleDashboard() {
  const dashboard = document.getElementById("dashboard");
  dashboard.style.display = dashboard.style.display === "block" ? "none" : "block";
}

function updateDashboard(data) {
  const dashboard = document.getElementById("dashboard");
  if (dashboard.style.display !== "block") return;

  let html = "<table><tr><th>Bus</th><th>Current</th><th>Next</th><th>Stops Completed</th><th>Dist→Next</th><th>Dist→Final</th><th>Occupants</th><th>Fuel</th><th>ETA</th></tr>";
  data.forEach(bus => {
    html += `<tr>
      <td>${bus.bus_id}</td>
      <td>${bus.current_stop}</td>
      <td>${bus.next_stop}</td>
      <td>${bus.stops_completed !== undefined ? bus.stops_completed : "-"}</td>
      <td>${bus.distance_to_next_km?.toFixed(2)} km</td>
      <td>${bus.distance_to_final_km || "-"} km</td>
      <td>${bus.occupancy}</td>
      <td>${bus.fuel_litres} L</td>
      <td>${bus.eta_min ? bus.eta_min + " min" : "N/A"}</td>
    </tr>`;
  });
  html += "</table>";
  dashboard.innerHTML = html;
}

function checkLowFuelAlerts(data) {
  const alertBox = document.getElementById("alerts");
  alertBox.innerHTML = ""; // clear old alerts each cycle

  data.forEach(bus => {
    if (bus.fuel_litres <= 25) {
      const div = document.createElement("div");
      div.className = "alert";
      div.innerHTML = `
        🚨 <b>Low Fuel Alert</b><br>
        Bus: ${bus.bus_id}<br>
        Fuel: ${bus.fuel_litres} L<br>
        Stop: ${bus.current_stop}
      `;
      alertBox.appendChild(div);
    }
  });
}

