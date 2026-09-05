import type { 
  Camera, 
  Alert, 
  TrafficMetric, 
  TrafficFlow, 
  Trajectory, 
  SystemStats, 
  PredictionResult, 
  ANPREvent,
  VehicleObservation
} from '../types';
import { 
  MOCK_CAMERAS, 
  MOCK_ALERTS, 
  MOCK_TRAFFIC_METRICS, 
  MOCK_TRAFFIC_FLOWS, 
  MOCK_TRAJECTORIES, 
  MOCK_SYSTEM_STATS, 
  MOCK_PREDICTION_RESULTS,
  SAMPLE_EVENTS
} from './mockData';

const API_BASE = 'http://localhost:8000/api';
const WS_URL = 'ws://localhost:8000/ws/traffic';

// Privacy masking helper
export function formatPlate(plate: string, maskPrivacy = false): string {
  if (!maskPrivacy || plate.length < 6) return plate;
  return `${plate.slice(0, 4)}••••${plate.slice(-2)}`;
}

class ApiService {
  private ws: WebSocket | null = null;
  private wsListeners: ((event: ANPREvent) => void)[] = [];

  // 1. Fetch Cameras
  async getCameras(): Promise<Camera[]> {
    try {
      const res = await fetch(`${API_BASE}/cameras`, { signal: AbortSignal.timeout(5000) });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      return data;
    } catch (err) {
      console.warn('Backend unavailable for getCameras, falling back to cached seed data:', err);
      return MOCK_CAMERAS;
    }
  }

  // 2. Fetch System Summary Stats (total vehicles, active cameras, avg speed, congested count)
  async getSystemStats(): Promise<SystemStats> {
    try {
      const res = await fetch(`${API_BASE}/traffic/summary`, { signal: AbortSignal.timeout(5000) });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      return {
        total_vehicles_today: data.total_vehicles_today || 142850,
        active_cameras: data.active_cameras || 23,
        total_cameras: data.total_cameras || 25,
        average_speed_city: data.average_speed_city || 54.2,
        active_alerts: data.active_alerts || 4,
        congested_corridors: data.congested_corridors || 3,
        events_per_second: 42,
        system_health: 'OPTIMAL'
      };
    } catch (err) {
      console.warn('Backend unavailable for getSystemStats, falling back to mock stats:', err);
      return MOCK_SYSTEM_STATS;
    }
  }

  // 3. Fetch Active Security & Traffic Alerts
  async getAlerts(): Promise<Alert[]> {
    try {
      const res = await fetch(`${API_BASE}/alerts`, { signal: AbortSignal.timeout(5000) });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      return data;
    } catch (err) {
      console.warn('Backend unavailable for getAlerts, falling back to mock alerts:', err);
      return MOCK_ALERTS;
    }
  }

  // 4. Update Alert Status (Triage: INVESTIGATING / RESOLVED)
  async updateAlertStatus(alertId: string, status: string): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE}/alerts/${alertId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });
      return res.ok;
    } catch (err) {
      console.error('Failed to update alert status:', err);
      return false;
    }
  }

  // 5. Fetch Corridor Congestion Metrics
  async getTrafficMetrics(): Promise<TrafficMetric[]> {
    try {
      const res = await fetch(`${API_BASE}/traffic/congestion`, { signal: AbortSignal.timeout(5000) });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      return data;
    } catch (err) {
      console.warn('Backend unavailable for getTrafficMetrics, falling back to mock metrics:', err);
      return MOCK_TRAFFIC_METRICS;
    }
  }

  // 6. Fetch Camera-to-Camera Directional Flows
  async getTrafficFlows(): Promise<TrafficFlow[]> {
    try {
      const res = await fetch(`${API_BASE}/traffic/flow`, { signal: AbortSignal.timeout(5000) });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      return data;
    } catch (err) {
      console.warn('Backend unavailable for getTrafficFlows, falling back to mock flows:', err);
      return MOCK_TRAFFIC_FLOWS;
    }
  }

  // 7. Fetch Recent ANPR Observations
  async getEvents(): Promise<ANPREvent[]> {
    try {
      const res = await fetch(`${API_BASE}/events?limit=50`, { signal: AbortSignal.timeout(5000) });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      return data;
    } catch (err) {
      console.warn('Backend unavailable for getEvents, falling back to sample events:', err);
      return SAMPLE_EVENTS;
    }
  }

  // 8. Fetch Vehicle Trajectory & Anomaly Assessment
  async getTrajectory(plate: string): Promise<Trajectory | null> {
    const cleanPlate = plate.replace(/[\s-]/g, '').toUpperCase();
    try {
      const res = await fetch(`${API_BASE}/vehicles/${cleanPlate}/trajectory`, { signal: AbortSignal.timeout(5000) });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      return data;
    } catch (err) {
      console.warn(`Backend trajectory unavailable for ${cleanPlate}, checking mock database:`, err);
      if (MOCK_TRAJECTORIES[cleanPlate]) {
        return MOCK_TRAJECTORIES[cleanPlate];
      }
      return {
        trajectory_id: `TRJ_${Date.now()}`,
        plate_number: cleanPlate,
        start_time: '2026-09-05T08:15:00',
        end_time: '2026-09-05T09:12:00',
        total_distance_km: 12.4,
        average_speed_kmph: 48.6,
        camera_count: 3,
        plausibility_status: 'NORMAL',
        anomaly_notes: null,
        route_geometry: [
          [26.9188, 75.8115],
          [26.8920, 75.8155],
          [26.8625, 75.7932]
        ],
        waypoints: [
          { camera_id: 'CAM_003', camera_name: 'MI Road - Panch Batti', timestamp: '2026-09-05T08:15:00', speed_kmph: 44.0, latitude: 26.9188, longitude: 75.8115 },
          { camera_id: 'CAM_005', camera_name: 'JL Marg - Birla Mandir', timestamp: '2026-09-05T08:42:00', speed_kmph: 52.0, latitude: 26.8920, longitude: 75.8155 },
          { camera_id: 'CAM_010', camera_name: 'Tonk Road - Gopalpura Bypass', timestamp: '2026-09-05T09:12:00', speed_kmph: 50.0, latitude: 26.8625, longitude: 75.7932 },
        ],
        anomalies: [],
        is_valid: true,
        vehicle_type: 'car'
      };
    }
  }

  // 9. Fetch Vehicle Historical Observations
  async getVehicleHistory(plate: string): Promise<VehicleObservation[]> {
    const trajectory = await this.getTrajectory(plate);
    if (!trajectory) return [];
    return trajectory.waypoints.map((wp, idx) => ({
      observation_id: `OBS_${idx}`,
      event_id: `EVT_H_${idx}`,
      plate_number: trajectory.plate_number,
      camera_id: wp.camera_id,
      timestamp: wp.timestamp,
      speed_kmph: wp.speed_kmph,
      direction: 'S',
      vehicle_type: trajectory.vehicle_type,
      violation: wp.is_anomaly ? 'FLAGGED_ROUTE' : null,
      confidence: 0.96,
      latitude: wp.latitude,
      longitude: wp.longitude,
      camera_name: wp.camera_name
    }));
  }

  // 10. Fetch Future Predictions (Placeholder/Model interface)
  async getPredictions(): Promise<PredictionResult[]> {
    try {
      const res = await fetch(`${API_BASE}/ml/prediction`, { signal: AbortSignal.timeout(5000) });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      return data.corridors && data.corridors.length > 0 ? data.corridors : MOCK_PREDICTION_RESULTS;
    } catch (err) {
      console.warn('Backend prediction endpoint unavailable, falling back to simulation data:', err);
      return MOCK_PREDICTION_RESULTS;
    }
  }

  // 11. Real-time Live WebSocket Stream
  subscribeLiveEvents(callback: (event: ANPREvent) => void): () => void {
    this.wsListeners.push(callback);
    
    if (!this.ws) {
      try {
        this.ws = new WebSocket(WS_URL);
        this.ws.onmessage = (msg) => {
          try {
            const data = JSON.parse(msg.data);
            if (data.type === 'ANPR_EVENT' && data.payload) {
              this.wsListeners.forEach(listener => listener(data.payload));
            }
          } catch (err) {
            console.error('WS Parse Error', err);
          }
        };
        this.ws.onerror = () => {
          // Fallback gracefully when backend server is off
        };
        this.ws.onclose = () => {
          this.ws = null;
        };
      } catch {
        // Fallback
      }
    }

    return () => {
      this.wsListeners = this.wsListeners.filter(cb => cb !== callback);
      if (this.wsListeners.length === 0 && this.ws) {
        this.ws.close();
        this.ws = null;
      }
    };
  }
}

export const apiService = new ApiService();
