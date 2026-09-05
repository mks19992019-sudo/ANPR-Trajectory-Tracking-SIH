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

const API_BASE = 'http://localhost:8000/api/v1';
const WS_URL = 'ws://localhost:8000/ws/traffic';

// Privacy masking helper
export function formatPlate(plate: string, maskPrivacy = false): string {
  if (!maskPrivacy || plate.length < 6) return plate;
  return `${plate.slice(0, 4)}••••${plate.slice(-2)}`;
}

class ApiService {
  private ws: WebSocket | null = null;
  private wsListeners: ((event: ANPREvent) => void)[] = [];

  async getCameras(): Promise<Camera[]> {
    try {
      const res = await fetch(`${API_BASE}/cameras`, { signal: AbortSignal.timeout(1000) });
      if (!res.ok) throw new Error();
      return await res.json();
    } catch {
      return MOCK_CAMERAS;
    }
  }

  async getSystemStats(): Promise<SystemStats> {
    try {
      const res = await fetch(`${API_BASE}/analytics/summary`, { signal: AbortSignal.timeout(1000) });
      if (!res.ok) throw new Error();
      return await res.json();
    } catch {
      return MOCK_SYSTEM_STATS;
    }
  }

  async getAlerts(): Promise<Alert[]> {
    try {
      const res = await fetch(`${API_BASE}/alerts`, { signal: AbortSignal.timeout(1000) });
      if (!res.ok) throw new Error();
      return await res.json();
    } catch {
      return MOCK_ALERTS;
    }
  }

  async getTrafficMetrics(): Promise<TrafficMetric[]> {
    try {
      const res = await fetch(`${API_BASE}/traffic/congestion`, { signal: AbortSignal.timeout(1000) });
      if (!res.ok) throw new Error();
      return await res.json();
    } catch {
      return MOCK_TRAFFIC_METRICS;
    }
  }

  async getTrafficFlows(): Promise<TrafficFlow[]> {
    try {
      const res = await fetch(`${API_BASE}/traffic/flow`, { signal: AbortSignal.timeout(1000) });
      if (!res.ok) throw new Error();
      return await res.json();
    } catch {
      return MOCK_TRAFFIC_FLOWS;
    }
  }

  async getEvents(): Promise<ANPREvent[]> {
    try {
      const res = await fetch(`${API_BASE}/anpr/events`, { signal: AbortSignal.timeout(1000) });
      if (!res.ok) throw new Error();
      return await res.json();
    } catch {
      return SAMPLE_EVENTS;
    }
  }

  async getTrajectory(plate: string): Promise<Trajectory | null> {
    const cleanPlate = plate.replace(/[\s-]/g, '').toUpperCase();
    try {
      const res = await fetch(`${API_BASE}/vehicles/${cleanPlate}/trajectory`, { signal: AbortSignal.timeout(1000) });
      if (!res.ok) throw new Error();
      return await res.json();
    } catch {
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

  async getPredictions(): Promise<PredictionResult[]> {
    try {
      const res = await fetch(`${API_BASE}/ml/prediction`, { signal: AbortSignal.timeout(1000) });
      if (!res.ok) throw new Error();
      return await res.json();
    } catch {
      return MOCK_PREDICTION_RESULTS;
    }
  }

  // Subscribe to real WebSocket when backend is running
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
          // Silent when backend is not yet started
        };
        this.ws.onclose = () => {
          this.ws = null;
        };
      } catch {
        // Backend not yet running
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
