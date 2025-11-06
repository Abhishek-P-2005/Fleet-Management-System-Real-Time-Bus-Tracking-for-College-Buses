## 🚌 Fleet Management System – Real-Time Bus Tracking for College Buses

### 📖 Overview

The **Fleet Management System (Bus Tracker)** is a real-time bus monitoring web application designed to track multiple college buses simultaneously.
It provides live updates of each bus — including **current stop, next stop, distance to next/final destination, fuel level, ETA, and total stops completed** — all displayed on an interactive map dashboard.

This system helps college transport departments monitor operations effectively and ensures timely arrival and safety of students.

---

### ⚙️ Features

✅ Real-time bus tracking across multiple routes (Adyar, Chengalpattu, Mylapore, T-Nagar)
✅ Dashboard showing live data: stops completed, distance, ETA, fuel level, and occupants
✅ Dynamic alerts for **low fuel levels (≤12 L)** appearing at the screen corner
✅ Separate simulators for each route with realistic distance and fuel consumption logic
✅ Interactive frontend map (Google Maps / Leaflet.js style)
✅ Modular backend (Flask server) for live data handling and dashboard updates
✅ Clean code structure following **SOLID principles**

---

### 🧩 System Architecture

```
bus-tracker/
│
├── client/
│   ├── bus_simulator_adyar.py
│   ├── bus_simulator_chengalpattu.py
│   ├── bus_simulator_mylapore.py
│   └── bus_simulator_tnagar.py
│
├── frontend/
│   ├── index.html          # Dashboard UI
│   └── script.js           # Handles data fetch + low fuel alerts
│
├── server/
│   ├── server.py           # Flask backend
│   └── static/routes/      # JSON route data (segments)
│
├── tools/
│   ├── input_segments_*.json
│   └── polyline_generator.py
│
└── README.md
```

---

### 💻 Tech Stack

| Layer                | Technology                                  |
| -------------------- | ------------------------------------------- |
| **Frontend**         | HTML5, CSS3, JavaScript                     |
| **Backend**          | Python Flask                                |
| **Simulation**       | Python (Real-time route + fuel computation) |
| **Data Format**      | JSON                                        |
| **Version Control**  | Git, GitHub                                 |
| **IDE**              | Visual Studio Code                          |
| **Operating System** | Windows 10/11                               |

---

### 🚀 How It Works

1. **Run the Flask Server**

   ```bash
   cd server
   python server.py
   ```

   ➜ Starts backend on `http://localhost:5000`

2. **Launch the Frontend**
   Open `frontend/index.html` in your browser to view the live dashboard.

3. **Start Simulators**
   In separate terminals:

   ```bash
   cd client
   python bus_simulator_adyar.py
   python bus_simulator_chengalpattu.py
   python bus_simulator_mylapore.py
   python bus_simulator_tnagar.py
   ```

   ➜ Each simulator sends live updates to the dashboard.

4. **Observe in Dashboard**

   * Buses move along their predefined routes.
   * Fuel depletes with distance.
   * Low fuel alerts pop up dynamically.
   * All data refreshes in real time.

---

### 🧠 SOLID Principles Applied

* **S – Single Responsibility:**
  Each simulator file handles one route. Server only manages updates.
* **O – Open/Closed Principle:**
  New routes or buses can be added without changing core logic.
* **L – Liskov Substitution:**
  Each simulator can be substituted without breaking system flow.
* **I – Interface Segregation:**
  Frontend and backend communicate via minimal, well-defined JSON API.
* **D – Dependency Inversion:**
  Frontend depends on API abstractions, not internal simulator details.

---

### ⚠️ Low Fuel Alert System

When any bus’s fuel level ≤ 25 L:

* A **toast-style alert** appears on the **bottom-right** of the screen.
* Alerts remain active until fuel is refilled.
* Each alert shows the bus ID, stop name, and current fuel level.

---

### 👨‍💻 Author

**Abhishek Prabakar**
📧 [abhishek.prabakar@gmail.com](mailto:abhishek.prabakar@gmail.com)
🌐 [GitHub Profile](https://github.com/Abhishek-P-2005)



