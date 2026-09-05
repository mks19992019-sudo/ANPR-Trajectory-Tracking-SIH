export type VehicleType = 'car' | 'truck' | 'bus' | 'motorcycle' | 'van';

export type CongestionLevel = 'LOW' | 'MODERATE' | 'HIGH' | 'SEVERE';

export type AlertType = 
  | 'BLACKLIST_MATCH'
  | 'SUSPICIOUS_ROUTE'
  | 'ANOMALOUS_MOVEMENT'
  | 'OVERSPEEDING'
  | 'HIGH_CONGESTION'
  | 'LOW_CONFIDENCE_ANPR';

export type AlertSeverity = 'CRITICAL' | 'WARNING' | 'INFO';

export interface ANPREvent {
  event_id: string;
  camera_id: string;
  plate_number: string;
  timestamp: string;
  speed_kmph: number;
  direction: string;
  vehicle_type: VehicleType;
  violation: string | null;
  confidence: number;
}

export interface Camera {
  camera_id: string;
  camera_name: string;
  road_id: string;
  latitude: number;
  longitude: number;
  location: string;
  direction: string;
  status: 'ACTIVE' | 'OFFLINE' | 'WARNING';
}

export interface Road {
  road_id: string;
  road_name: string;
  speed_limit: number;
  lanes: number;
  coordinates: [number, number][];
}

export interface VehicleObservation extends ANPREvent {
  observation_id: string;
  latitude: number;
  longitude: number;
  camera_name: string;
  created_at?: string;
}

export interface TrajectoryWaypoint {
  camera_id: string;
  camera_name: string;
  timestamp: string;
  speed_kmph: number;
  latitude: number;
  longitude: number;
  is_anomaly?: boolean;
  anomaly_reason?: string;
}

export interface Trajectory {
  trajectory_id: string;
  plate_number: string;
  start_time: string;
  end_time: string;
  total_distance_km: number;
  average_speed_kmph: number;
  camera_count: number;
  route_geometry: [number, number][];
  waypoints: TrajectoryWaypoint[];
  anomalies: string[];
  is_valid: boolean;
  vehicle_type: VehicleType;
}

export interface TrafficMetric {
  road_id: string;
  road_name: string;
  camera_id?: string;
  time_window: string;
  vehicle_count: number;
  average_speed: number;
  median_speed: number;
  congestion_score: number;
  congestion_level: CongestionLevel;
}

export interface TrafficFlow {
  source_camera: string;
  source_name: string;
  destination_camera: string;
  destination_name: string;
  vehicle_count: number;
  time_window: string;
  source_coords: [number, number];
  destination_coords: [number, number];
}

export interface Alert {
  alert_id: string;
  alert_type: AlertType;
  plate_number: string;
  camera_id: string;
  camera_name?: string;
  severity: AlertSeverity;
  message: string;
  timestamp: string;
  status: 'OPEN' | 'INVESTIGATING' | 'RESOLVED';
}

export interface BlacklistEntry {
  plate_number: string;
  reason: string;
  severity: AlertSeverity;
  active: boolean;
  created_at: string;
}

export interface PredictionResult {
  road_id: string;
  road_name: string;
  current_volume: number;
  predicted_volume_30m: number;
  predicted_congestion: CongestionLevel;
  confidence: number;
  model_loaded: boolean;
  feature_importance?: { feature: string; importance: number }[];
}

export interface SystemStats {
  total_vehicles_today: number;
  active_cameras: number;
  total_cameras: number;
  average_speed_city: number;
  congested_corridors: number;
  active_alerts: number;
  events_per_second: number;
  system_health: 'OPTIMAL' | 'DEGRADED' | 'WARNING';
}
