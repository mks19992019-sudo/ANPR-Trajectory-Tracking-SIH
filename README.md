# City-Wide ANPR Vehicle Tracking, Traffic Analytics & Intelligence Platform

A centralized, real-time traffic intelligence and vehicle tracking platform engineered for smart city command centers. The system ingests structured ANPR (Automatic Number Plate Recognition) events from municipal camera networks, performs real-time validation and deduplication, reconstructs multi-hop vehicle trajectories, detects anomalies (e.g. cloned plates / physically impossible movement), calculates corridor congestion and speed compliance, and exposes live REST and WebSocket streams for interactive GIS dashboards.

---

## 🏛️ System Boundary & Core Ingestion Pipeline

> **Clear System Boundary**: This platform starts **AFTER** the police ANPR/OCR cameras. It does not perform camera-level computer vision. It consumes pre-extracted ANPR event payloads:

```json
{
  "event_id": "EVT102938",
  "camera_id": "CAM_023",
  "plate_number": "RJ14AB1234",
  "timestamp": "2026-09-05T09:12:15Z",
  "speed_kmph": 47.5,
  "direction": "NORTH",
  "vehicle_type": "car",
  "violation": null,
  "ocr_confidence": 0.98
}
```

```
┌─────────────────────────────────┐
│ Police ANPR / Checkpoint Cameras│
└───────────────┬─────────────────┘
                │ (Structured Events)
                ▼
┌─────────────────────────────────┐
│     FastAPI Ingestion Engine    │ ───► [Deduplication & Validation (5s Window)]
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│      Alert & Anomaly Engine     │ ───► [Blacklist / Overspeed / Clone Detection]
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│       Trajectory Engine         │ ───► [Haversine / Delta Time / Implied Speed]
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│   Congestion & OD Matrix Engine │ ───► [Score: (Vol/Cap)*(1 - v/v_limit)]
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ REST APIs + Live WebSocket Bus  │ ───► React GIS Command Center Dashboard
└─────────────────────────────────┘
```

---

## ⚡ Key Intelligence Features

1. **Vehicle Trajectory Reconstruction**:
   - Reconstructs chronological waypoints across 25+ city checkpoints.
   - Calculates geodesic distance ($\Delta d$) via Haversine formula and time elapsed ($\Delta t$).
   - Calculates implied velocity: $v_{implied} = \frac{\Delta d}{\Delta t}$.
   - Automatically flags **PHYSICALLY_IMPOSSIBLE** anomalies (e.g., cloned license plates transiting 14.8 km in 90 seconds $\approx 592\text{ km/h}$).

2. **Corridor Congestion & Speed Analytics**:
   - Dynamic congestion scoring:
     $$\text{Congestion Score} = \left(\frac{\text{Volume}}{\text{Capacity}}\right) \times \left(1 - \frac{v_{\text{avg}}}{v_{\text{limit}}}\right)$$
   - Classifies road conditions into `LOW`, `MODERATE`, `HIGH`, and `SEVERE`.
   - Computes 85th percentile speeds ($P_{85}$), median speeds, and speed compliance rates.

3. **Origin-Destination (OD) Matrix & Flow Heatmaps**:
   - Reconstructs inter-zone commuter trips between city corridors.
   - Generates GeoJSON heatmap layer of camera detection frequencies.

4. **Multi-Tier Alert System**:
   - `CRITICAL`: Stolen / Wanted / Suspicious Blacklist matches.
   - `HIGH`: Physically impossible movement / Teleportation anomalies (cloned plates).
   - `WARNING`: Active speed limit violations.

5. **Future-Proof ML Placeholder**:
   - Dedicated `/api/ml/prediction` interface prepared for your custom XGBoost traffic forecasting model.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, Pydantic v2, Uvicorn, WebSockets.
- **Database**: PostgreSQL with PostGIS only.
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Leaflet GIS Maps, Recharts.
- **Data Generator**: High-throughput multi-route vehicle simulator with anomaly and duplicate injection.
- **DevOps**: Docker, Docker Compose, Nginx.

---

## 🚀 Quickstart Guide

### 1. Backend Setup & Local Run

```bash
# Navigate to project root
cd "/Users/All file hear/my all projects /SIH smart city"

# Create and activate virtual environment
python3 -m venv backend/venv
source backend/venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start the FastAPI backend server (auto-seeds checkpoints, roads & demo data)
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup & Local Run

```bash
cd frontend
npm install
npm run dev
# Dashboard opens on http://localhost:5173/
```

### 3. Docker Compose (Full Stack)

```bash
docker-compose up --build
```
- Frontend UI: `http://localhost:5173`
- Backend Swagger Docs: `http://localhost:8000/docs`
- PostGIS Database: `localhost:5432`

---

## 📊 Synthetic Data Generator & Live Streaming

### Batch Data Generation
Generate realistic historical records with configurable vehicle counts, anomalies, and duplicates:
```bash
python generator/generate_data.py --events 1000 --vehicles 250 --anomaly-pct 3.0 --duplicate-pct 2.0
```

### Real-Time Live Streaming Simulation
Stream live ANPR observations to the ingestion endpoint (`POST /api/events`) to watch live WebSocket updates on the dashboard:
```bash
python generator/stream_events.py --interval 0.5 --vehicles 50
```

---

## 🧪 Running Automated Tests

Run the test suite covering ingestion validation, deduplication, trajectory anomaly detection, and alert generation:

```bash
pytest tests/ -v
```

---

## 📖 API Endpoints Reference

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/health` | `GET` | System health and database status |
| `/api/events` | `POST` | Ingest single ANPR observation from police cameras |
| `/api/cameras` | `GET` | List all 25 camera checkpoints with coordinates & limits |
| `/api/vehicles/{plate}/trajectory` | `GET` | Vehicle trajectory, waypoints, and plausibility status |
| `/api/traffic/summary` | `GET` | City-wide vehicle volume, active cameras, avg speed |
| `/api/traffic/congestion` | `GET` | Corridor-level congestion scores and levels |
| `/api/traffic/speed-analytics` | `GET` | P85, median speeds, and speed compliance rates |
| `/api/traffic/flow` | `GET` | Camera-to-camera directional flow volumes |
| `/api/traffic/od-matrix` | `GET` | Inter-zone origin-destination matrix |
| `/api/traffic/heatmap` | `GET` | GeoJSON camera detection intensity dataset |
| `/api/alerts` | `GET` | Active security and traffic violation alerts |
| `/api/alerts/{id}/status` | `PATCH` | Update alert status (`INVESTIGATING`, `RESOLVED`) |
| `/api/blacklist` | `GET / POST` | Query or register flagged license plates |
| `/api/ml/prediction` | `GET` | Placeholder endpoint for custom XGBoost model |
| `/ws/traffic` | `WS` | Real-time WebSocket event feed |
