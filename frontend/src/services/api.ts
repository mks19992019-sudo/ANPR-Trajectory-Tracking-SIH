import type {
  Alert,
  ANPREvent,
  Camera,
  PredictionResult,
  SystemStats,
  TrafficFlow,
  TrafficMetric,
  Trajectory,
  VehicleObservation
} from '../types';

const base = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

async function get<T>(path: string): Promise<T> {
  const r = await fetch(base + path);
  if (!r.ok) throw new Error(`Request failed (${r.status})`);
  return r.json();
}

export const formatPlate = (plate: string, mask = false) =>
  mask && plate && plate.length > 6 ? `${plate.slice(0, 4)}••••${plate.slice(-2)}` : (plate || 'UNKNOWN');

class ApiService {
  async getCameras(): Promise<Camera[]> {
    return get<Camera[]>('/cameras');
  }

  async getSystemStats(): Promise<SystemStats> {
    const data = await get<any>('/traffic/summary');
    return {
      total_vehicles_today: data.total_vehicles_today ?? 0,
      active_cameras: data.active_cameras ?? 0,
      total_cameras: data.total_cameras ?? 0,
      average_speed_city: data.average_speed_city ?? 0,
      congested_corridors: data.congested_corridors ?? 0,
      active_alerts: data.active_alerts ?? 0,
      events_per_second: 1.0,
      system_health: (data.congested_corridors ?? 0) > 3 ? 'WARNING' : 'OPTIMAL'
    };
  }

  async getAlerts(): Promise<Alert[]> {
    const data = await get<any[]>('/alerts');
    return (data || []).map((a) => ({
      ...a,
      message: a.message ?? a.description ?? 'Incident detected',
      description: a.description ?? a.message ?? 'Incident detected',
      timestamp: a.timestamp ?? a.created_at ?? new Date().toISOString()
    }));
  }

  async updateAlertStatus(id: string, status: string): Promise<boolean> {
    const r = await fetch(`${base}/alerts/${id}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    if (!r.ok) throw new Error(`Request failed (${r.status})`);
    return true;
  }

  async getTrafficMetrics(): Promise<TrafficMetric[]> {
    return get<TrafficMetric[]>('/traffic/congestion');
  }

  async getTrafficFlows(): Promise<TrafficFlow[]> {
    return get<TrafficFlow[]>('/traffic/flow');
  }

  async getEvents(): Promise<ANPREvent[]> {
    const res = await get<{ items: any[] }>('/events?limit=50');
    return (res.items || []).map((e) => ({
      ...e,
      timestamp: e.timestamp ?? e.observed_at ?? new Date().toISOString(),
      observed_at: e.observed_at ?? e.timestamp ?? new Date().toISOString(),
      confidence: e.confidence ?? e.ocr_confidence ?? 0.95
    }));
  }

  async getTrajectory(plate: string): Promise<Trajectory | null> {
    try {
      const data = await get<any>(`/vehicles/${encodeURIComponent(plate)}/trajectory`);
      if (!data) return null;
      const anomalies = Array.isArray(data.anomalies)
        ? data.anomalies
        : data.anomaly_notes
        ? [data.anomaly_notes]
        : [];
      return {
        ...data,
        anomalies,
        is_valid: data.is_valid ?? data.plausibility_status === 'NORMAL',
        vehicle_type: data.vehicle_type ?? 'car',
        waypoints: (data.waypoints || []).map((wp: any) => ({
          ...wp,
          timestamp: wp.timestamp ? String(wp.timestamp) : new Date().toISOString()
        }))
      };
    } catch {
      return null;
    }
  }

  async getVehicleHistory(plate: string): Promise<VehicleObservation[]> {
    try {
      const data = await get<any[]>(`/vehicles/${encodeURIComponent(plate)}/history`);
      return (data || []).map((o, idx) => ({
        ...o,
        observation_id: o.observation_id ?? `OBS_${idx}`,
        event_id: o.event_id ?? `EVT_${idx}`,
        timestamp: o.timestamp ?? o.observed_at ?? new Date().toISOString(),
        confidence: o.confidence ?? o.ocr_confidence ?? 0.95
      }));
    } catch {
      return [];
    }
  }

  async getPredictions(): Promise<PredictionResult[]> {
    try {
      return await get<PredictionResult[]>('/ml/prediction');
    } catch {
      return [];
    }
  }

  subscribeLiveEvents(callback: (e: ANPREvent) => void): () => void {
    let wsUrl: string;
    const apiBase = import.meta.env.VITE_API_BASE_URL;
    if (apiBase && (apiBase.startsWith('http://') || apiBase.startsWith('https://'))) {
      const parsed = new URL(apiBase);
      const proto = parsed.protocol === 'https:' ? 'wss:' : 'ws:';
      wsUrl = `${proto}//${parsed.host}/ws/traffic`;
    } else {
      const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
      wsUrl = `${proto}//${location.host}/ws/traffic`;
    }
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.type === 'ANPR_EVENT' && data.payload) {
          callback({
            ...data.payload,
            timestamp: data.payload.timestamp ?? data.payload.observed_at ?? new Date().toISOString(),
            confidence: data.payload.confidence ?? data.payload.ocr_confidence ?? 0.95
          });
        }
      } catch (err) {
        console.error('WS parse error', err);
      }
    };
    ws.onerror = (err) => {
      console.warn('WS connection warning', err);
    };
    return () => {
      try {
        ws.close();
      } catch {}
    };
  }

  async resetData(): Promise<{ status: string; message: string }> {
    const r = await fetch(`${base}/system/reset-data`, { method: 'POST' });
    if (!r.ok) throw new Error(`Reset failed (${r.status})`);
    return r.json();
  }

  async generateData(events = 80): Promise<{ status: string; message: string; events_generated: number }> {
    const r = await fetch(`${base}/system/generate-data`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ events, include_anomalies: true })
    });
    if (!r.ok) throw new Error(`Generation failed (${r.status})`);
    return r.json();
  }
}

export const apiService = new ApiService();
