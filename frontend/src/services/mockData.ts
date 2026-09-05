import { Camera, Road, Alert, TrafficMetric, TrafficFlow, Trajectory, SystemStats, PredictionResult, ANPREvent } from '../types';

export const MOCK_CAMERAS: Camera[] = [
  { camera_id: 'CAM_001', camera_name: 'Ajmer Road Flyover Entrance', road_id: 'RD_01', latitude: 26.8925, longitude: 75.7621, location: 'Civil Lines West', direction: 'W', status: 'ACTIVE' },
  { camera_id: 'CAM_002', camera_name: 'Ajmer Road - 200ft Bypass Junction', road_id: 'RD_01', latitude: 26.8850, longitude: 75.7310, location: 'Heerapura Circle', direction: 'SW', status: 'ACTIVE' },
  { camera_id: 'CAM_003', camera_name: 'MI Road - Panch Batti Intersection', road_id: 'RD_02', latitude: 26.9188, longitude: 75.8115, location: 'MI Road Central', direction: 'E', status: 'ACTIVE' },
  { camera_id: 'CAM_004', camera_name: 'MI Road - Ajmeri Gate Chauraha', road_id: 'RD_02', latitude: 26.9172, longitude: 75.8205, location: 'Ajmeri Gate', direction: 'NE', status: 'ACTIVE' },
  { camera_id: 'CAM_005', camera_name: 'JL Marg - Birla Mandir Crossing', road_id: 'RD_03', latitude: 26.8920, longitude: 75.8155, location: 'Tilak Nagar', direction: 'S', status: 'ACTIVE' },
  { camera_id: 'CAM_006', camera_name: 'JL Marg - Rajasthan Univ Main Gate', road_id: 'RD_03', latitude: 26.8805, longitude: 75.8140, location: 'Gandhinagar', direction: 'S', status: 'ACTIVE' },
  { camera_id: 'CAM_007', camera_name: 'JL Marg - World Trade Park Crossing', road_id: 'RD_03', latitude: 26.8530, longitude: 75.8052, location: 'Malviya Nagar', direction: 'S', status: 'ACTIVE' },
  { camera_id: 'CAM_008', camera_name: 'Airport Road - Terminal 2 Arrival', road_id: 'RD_04', latitude: 26.8285, longitude: 75.8050, location: 'Jaipur Airport Gate', direction: 'SE', status: 'ACTIVE' },
  { camera_id: 'CAM_009', camera_name: 'Tonk Road - Rambagh Circle Checkpoint', road_id: 'RD_05', latitude: 26.8962, longitude: 75.8068, location: 'Rambagh', direction: 'S', status: 'ACTIVE' },
  { camera_id: 'CAM_010', camera_name: 'Tonk Road - Gopalpura Bypass Underpass', road_id: 'RD_05', latitude: 26.8625, longitude: 75.7932, location: 'Gopalpura Flyover', direction: 'S', status: 'ACTIVE' },
  { camera_id: 'CAM_011', camera_name: 'Tonk Road - Sanganer Flyover Entry', road_id: 'RD_05', latitude: 26.8152, longitude: 75.7720, location: 'Sanganer Town', direction: 'SW', status: 'ACTIVE' },
  { camera_id: 'CAM_012', camera_name: 'Delhi Highway - Transport Nagar Toll', road_id: 'RD_06', latitude: 26.9125, longitude: 75.8562, location: 'Ghat Ki Guni Tunnel', direction: 'NE', status: 'ACTIVE' },
  { camera_id: 'CAM_013', camera_name: 'Delhi Highway - Sisodia Rani Garden', road_id: 'RD_06', latitude: 26.8995, longitude: 75.8655, location: 'Kunda Corridor', direction: 'E', status: 'ACTIVE' },
  { camera_id: 'CAM_014', camera_name: 'Sikar Road - Chomu Pulia Junction', road_id: 'RD_07', latitude: 26.9632, longitude: 75.7750, location: 'Vidyadhar Nagar North', direction: 'NW', status: 'ACTIVE' },
  { camera_id: 'CAM_015', camera_name: 'Sikar Road - VKI Area Gate 1', road_id: 'RD_07', latitude: 26.9850, longitude: 75.7610, location: 'Vishwakarma Ind Area', direction: 'N', status: 'WARNING' },
  { camera_id: 'CAM_016', camera_name: 'Queens Road - Vaishali Police Chowki', road_id: 'RD_08', latitude: 26.9045, longitude: 75.7482, location: 'Vaishali Nagar', direction: 'N', status: 'ACTIVE' },
  { camera_id: 'CAM_017', camera_name: 'Kings Road - Nirman Nagar Square', road_id: 'RD_08', latitude: 26.8912, longitude: 75.7510, location: 'Nirman Nagar', direction: 'S', status: 'ACTIVE' },
  { camera_id: 'CAM_018', camera_name: 'B2 Bypass - Shipra Path Crossroad', road_id: 'RD_09', latitude: 26.8480, longitude: 75.7795, location: 'Mansarovar Metro', direction: 'E', status: 'ACTIVE' },
  { camera_id: 'CAM_019', camera_name: 'B2 Bypass - Jawahar Circle North', road_id: 'RD_09', latitude: 26.8475, longitude: 75.8015, location: 'Jawahar Circle', direction: 'E', status: 'ACTIVE' },
  { camera_id: 'CAM_020', camera_name: 'Hawa Mahal Walled City Entry', road_id: 'RD_10', latitude: 26.9240, longitude: 75.8267, location: 'Badi Chaupar', direction: 'N', status: 'ACTIVE' },
  { camera_id: 'CAM_021', camera_name: 'Johari Bazaar - Sanganeri Gate', road_id: 'RD_10', latitude: 26.9160, longitude: 75.8242, location: 'Johari Bazaar South', direction: 'N', status: 'ACTIVE' },
  { camera_id: 'CAM_022', camera_name: 'Agra Road - Ghat Gate Exit', road_id: 'RD_11', latitude: 26.9100, longitude: 75.8350, location: 'Ghat Gate Circle', direction: 'SE', status: 'ACTIVE' },
  { camera_id: 'CAM_023', camera_name: 'Jhotwara Road - Elevated Road Start', road_id: 'RD_12', latitude: 26.9380, longitude: 75.7725, location: 'Railway Station North', direction: 'W', status: 'OFFLINE' },
  { camera_id: 'CAM_024', camera_name: 'Amer Road - Jal Mahal Viewpoint', road_id: 'RD_13', latitude: 26.9535, longitude: 75.8450, location: 'Man Sagar Lake', direction: 'N', status: 'ACTIVE' },
  { camera_id: 'CAM_025', camera_name: 'Amer Road - Elephant Village Entry', road_id: 'RD_13', latitude: 26.9855, longitude: 75.8512, location: 'Amer Fort Foothills', direction: 'NE', status: 'ACTIVE' },
];

export const MOCK_ROADS: Road[] = [
  { road_id: 'RD_01', road_name: 'Ajmer Expressway Corridor', speed_limit: 80, lanes: 6, coordinates: [[26.8925, 75.7621], [26.8850, 75.7310]] },
  { road_id: 'RD_02', road_name: 'Mirza Ismail (MI) Arterial', speed_limit: 50, lanes: 4, coordinates: [[26.9188, 75.8115], [26.9172, 75.8205]] },
  { road_id: 'RD_03', road_name: 'Jawaharlal Nehru (JL) Marg', speed_limit: 60, lanes: 6, coordinates: [[26.8920, 75.8155], [26.8805, 75.8140], [26.8530, 75.8052]] },
  { road_id: 'RD_04', road_name: 'Airport VIP Expressway', speed_limit: 70, lanes: 4, coordinates: [[26.8530, 75.8052], [26.8285, 75.8050]] },
  { road_id: 'RD_05', road_name: 'Tonk Road National Highway', speed_limit: 60, lanes: 6, coordinates: [[26.8962, 75.8068], [26.8625, 75.7932], [26.8152, 75.7720]] },
  { road_id: 'RD_06', road_name: 'Jaipur-Delhi Highway', speed_limit: 90, lanes: 6, coordinates: [[26.9125, 75.8562], [26.8995, 75.8655]] },
  { road_id: 'RD_07', road_name: 'Sikar Road Industrial Belt', speed_limit: 50, lanes: 4, coordinates: [[26.9632, 75.7750], [26.9850, 75.7610]] },
  { road_id: 'RD_08', road_name: 'Vaishali Urban Corridor', speed_limit: 45, lanes: 4, coordinates: [[26.9045, 75.7482], [26.8912, 75.7510]] },
  { road_id: 'RD_09', road_name: 'B2 Bypass Ring Expressway', speed_limit: 80, lanes: 6, coordinates: [[26.8480, 75.7795], [26.8475, 75.8015]] },
  { road_id: 'RD_10', road_name: 'Heritage Walled City Spine', speed_limit: 40, lanes: 2, coordinates: [[26.9240, 75.8267], [26.9160, 75.8242]] },
];

export const MOCK_SYSTEM_STATS: SystemStats = {
  total_vehicles_today: 48920,
  active_cameras: 23,
  total_cameras: 25,
  average_speed_city: 46.8,
  congested_corridors: 3,
  active_alerts: 4,
  events_per_second: 18.4,
  system_health: 'OPTIMAL'
};

// Clean sample events for display
export const SAMPLE_EVENTS: ANPREvent[] = [
  { event_id: 'EVT_102938', camera_id: 'CAM_003', plate_number: 'RJ14AB1234', timestamp: '2026-09-05T09:12:15', speed_kmph: 47.5, direction: 'E', vehicle_type: 'car', violation: null, confidence: 0.98 },
  { event_id: 'EVT_102939', camera_id: 'CAM_005', plate_number: 'DL01CZ9999', timestamp: '2026-09-05T09:13:00', speed_kmph: 52.0, direction: 'S', vehicle_type: 'car', violation: null, confidence: 0.96 },
  { event_id: 'EVT_102940', camera_id: 'CAM_001', plate_number: 'RJ14GE8819', timestamp: '2026-09-05T09:14:22', speed_kmph: 112.4, direction: 'W', vehicle_type: 'car', violation: 'OVERSPEEDING', confidence: 0.99 },
  { event_id: 'EVT_102941', camera_id: 'CAM_011', plate_number: 'HR26XY4040', timestamp: '2026-09-05T09:15:10', speed_kmph: 58.0, direction: 'SW', vehicle_type: 'truck', violation: null, confidence: 0.94 },
  { event_id: 'EVT_102942', camera_id: 'CAM_007', plate_number: 'RJ45CD2201', timestamp: '2026-09-05T09:16:05', speed_kmph: 42.0, direction: 'S', vehicle_type: 'bus', violation: null, confidence: 0.97 },
  { event_id: 'EVT_102943', camera_id: 'CAM_018', plate_number: 'UP16BW7701', timestamp: '2026-09-05T09:17:15', speed_kmph: 36.5, direction: 'E', vehicle_type: 'van', violation: null, confidence: 0.92 },
  { event_id: 'EVT_102944', camera_id: 'CAM_020', plate_number: 'RJ14KM5544', timestamp: '2026-09-05T09:18:40', speed_kmph: 28.0, direction: 'N', vehicle_type: 'motorcycle', violation: null, confidence: 0.89 },
  { event_id: 'EVT_102945', camera_id: 'CAM_002', plate_number: 'RJ14GH9012', timestamp: '2026-09-05T09:19:30', speed_kmph: 74.0, direction: 'SW', vehicle_type: 'car', violation: null, confidence: 0.95 },
  { event_id: 'EVT_102946', camera_id: 'CAM_012', plate_number: 'RJ14PZ3321', timestamp: '2026-09-05T09:20:12', speed_kmph: 88.0, direction: 'NE', vehicle_type: 'car', violation: 'OVERSPEEDING', confidence: 0.97 },
  { event_id: 'EVT_102947', camera_id: 'CAM_009', plate_number: 'DL08EF4411', timestamp: '2026-09-05T09:21:00', speed_kmph: 49.0, direction: 'S', vehicle_type: 'car', violation: null, confidence: 0.96 }
];

export const MOCK_ALERTS: Alert[] = [
  {
    alert_id: 'ALT_101',
    alert_type: 'BLACKLIST_MATCH',
    plate_number: 'DL01CZ9999',
    camera_id: 'CAM_003',
    camera_name: 'MI Road - Panch Batti Intersection',
    severity: 'CRITICAL',
    message: 'Blacklisted Vehicle Detected: Stolen vehicle investigation (FIR #882)',
    timestamp: '2026-09-05T09:40:12',
    status: 'OPEN'
  },
  {
    alert_id: 'ALT_102',
    alert_type: 'ANOMALOUS_MOVEMENT',
    plate_number: 'HR26XY4040',
    camera_id: 'CAM_015',
    camera_name: 'Sikar Road - VKI Area Gate 1',
    severity: 'CRITICAL',
    message: 'Impossible Transition: Traveled 14.8 km in 90 seconds (implied 592 km/h - suspected duplicate/cloned plate)',
    timestamp: '2026-09-05T09:38:45',
    status: 'OPEN'
  },
  {
    alert_id: 'ALT_103',
    alert_type: 'OVERSPEEDING',
    plate_number: 'RJ14GE8819',
    camera_id: 'CAM_001',
    camera_name: 'Ajmer Road Flyover Entrance',
    severity: 'WARNING',
    message: 'Overspeeding: Clocked at 112.4 km/h on 80 km/h expressway',
    timestamp: '2026-09-05T09:41:20',
    status: 'OPEN'
  },
  {
    alert_id: 'ALT_104',
    alert_type: 'HIGH_CONGESTION',
    plate_number: 'CORRIDOR_ALERT',
    camera_id: 'CAM_005',
    camera_name: 'JL Marg - Birla Mandir Crossing',
    severity: 'WARNING',
    message: 'High Congestion: Average corridor speed dropped below 18 km/h',
    timestamp: '2026-09-05T09:35:00',
    status: 'INVESTIGATING'
  }
];

export const MOCK_TRAFFIC_METRICS: TrafficMetric[] = [
  { road_id: 'RD_01', road_name: 'Ajmer Expressway Corridor', time_window: 'Last 15m', vehicle_count: 1420, average_speed: 68.4, median_speed: 70.0, congestion_score: 0.35, congestion_level: 'LOW' },
  { road_id: 'RD_02', road_name: 'Mirza Ismail (MI) Arterial', time_window: 'Last 15m', vehicle_count: 980, average_speed: 24.1, median_speed: 22.0, congestion_score: 0.82, congestion_level: 'HIGH' },
  { road_id: 'RD_03', road_name: 'Jawaharlal Nehru (JL) Marg', time_window: 'Last 15m', vehicle_count: 2150, average_speed: 38.5, median_speed: 40.0, congestion_score: 0.65, congestion_level: 'MODERATE' },
  { road_id: 'RD_04', road_name: 'Airport VIP Expressway', time_window: 'Last 15m', vehicle_count: 740, average_speed: 64.2, median_speed: 65.0, congestion_score: 0.28, congestion_level: 'LOW' },
  { road_id: 'RD_05', road_name: 'Tonk Road National Highway', time_window: 'Last 15m', vehicle_count: 1890, average_speed: 31.0, median_speed: 30.0, congestion_score: 0.76, congestion_level: 'HIGH' },
  { road_id: 'RD_06', road_name: 'Jaipur-Delhi Highway', time_window: 'Last 15m', vehicle_count: 1650, average_speed: 82.5, median_speed: 85.0, congestion_score: 0.22, congestion_level: 'LOW' },
  { road_id: 'RD_07', road_name: 'Sikar Road Industrial Belt', time_window: 'Last 15m', vehicle_count: 1100, average_speed: 42.0, median_speed: 44.0, congestion_score: 0.54, congestion_level: 'MODERATE' },
  { road_id: 'RD_08', road_name: 'Vaishali Urban Corridor', time_window: 'Last 15m', vehicle_count: 890, average_speed: 36.8, median_speed: 38.0, congestion_score: 0.48, congestion_level: 'LOW' },
  { road_id: 'RD_09', road_name: 'B2 Bypass Ring Expressway', time_window: 'Last 15m', vehicle_count: 1540, average_speed: 74.0, median_speed: 75.0, congestion_score: 0.31, congestion_level: 'LOW' },
  { road_id: 'RD_10', road_name: 'Heritage Walled City Spine', time_window: 'Last 15m', vehicle_count: 1320, average_speed: 14.8, median_speed: 13.5, congestion_score: 0.94, congestion_level: 'SEVERE' },
];

export const MOCK_TRAFFIC_FLOWS: TrafficFlow[] = [
  { source_camera: 'CAM_001', source_name: 'Ajmer Rd Flyover', destination_camera: 'CAM_002', destination_name: '200ft Bypass', vehicle_count: 1250, time_window: '1h', source_coords: [26.8925, 75.7621], destination_coords: [26.8850, 75.7310] },
  { source_camera: 'CAM_005', source_name: 'Birla Mandir', destination_camera: 'CAM_006', destination_name: 'Rajasthan Univ', vehicle_count: 1820, time_window: '1h', source_coords: [26.8920, 75.8155], destination_coords: [26.8805, 75.8140] },
  { source_camera: 'CAM_006', source_name: 'Rajasthan Univ', destination_camera: 'CAM_007', destination_name: 'WTP Crossing', vehicle_count: 1540, time_window: '1h', source_coords: [26.8805, 75.8140], destination_coords: [26.8530, 75.8052] },
  { source_camera: 'CAM_007', source_name: 'WTP Crossing', destination_camera: 'CAM_008', destination_name: 'Airport T2', vehicle_count: 980, time_window: '1h', source_coords: [26.8530, 75.8052], destination_coords: [26.8285, 75.8050] },
  { source_camera: 'CAM_009', source_name: 'Rambagh Circle', destination_camera: 'CAM_010', destination_name: 'Gopalpura Bypass', vehicle_count: 1490, time_window: '1h', source_coords: [26.8962, 75.8068], destination_coords: [26.8625, 75.7932] },
  { source_camera: 'CAM_010', source_name: 'Gopalpura Bypass', destination_camera: 'CAM_011', destination_name: 'Sanganer Entry', vehicle_count: 1120, time_window: '1h', source_coords: [26.8625, 75.7932], destination_coords: [26.8152, 75.7720] },
  { source_camera: 'CAM_018', source_name: 'Shipra Path', destination_camera: 'CAM_019', destination_name: 'Jawahar Circle', vehicle_count: 1310, time_window: '1h', source_coords: [26.8480, 75.7795], destination_coords: [26.8475, 75.8015] },
  { source_camera: 'CAM_020', source_name: 'Hawa Mahal Entry', destination_camera: 'CAM_021', destination_name: 'Johari Bazaar', vehicle_count: 870, time_window: '1h', source_coords: [26.9240, 75.8267], destination_coords: [26.9160, 75.8242] },
];

export const MOCK_TRAJECTORIES: Record<string, Trajectory> = {
  'RJ14AB1234': {
    trajectory_id: 'TRJ_001',
    plate_number: 'RJ14AB1234',
    start_time: '2026-09-05T08:45:00',
    end_time: '2026-09-05T09:18:00',
    total_distance_km: 9.8,
    average_speed_kmph: 52.4,
    camera_count: 4,
    route_geometry: [
      [26.8920, 75.8155],
      [26.8805, 75.8140],
      [26.8530, 75.8052],
      [26.8285, 75.8050]
    ],
    waypoints: [
      { camera_id: 'CAM_005', camera_name: 'JL Marg - Birla Mandir Crossing', timestamp: '2026-09-05T08:45:00', speed_kmph: 48.0, latitude: 26.8920, longitude: 75.8155 },
      { camera_id: 'CAM_006', camera_name: 'JL Marg - Rajasthan Univ Main Gate', timestamp: '2026-09-05T08:52:15', speed_kmph: 51.5, latitude: 26.8805, longitude: 75.8140 },
      { camera_id: 'CAM_007', camera_name: 'JL Marg - World Trade Park Crossing', timestamp: '2026-09-05T09:05:30', speed_kmph: 56.0, latitude: 26.8530, longitude: 75.8052 },
      { camera_id: 'CAM_008', camera_name: 'Airport Road - Terminal 2 Arrival', timestamp: '2026-09-05T09:18:00', speed_kmph: 54.2, latitude: 26.8285, longitude: 75.8050 },
    ],
    anomalies: [],
    is_valid: true,
    vehicle_type: 'car'
  },
  'DL01CZ9999': {
    trajectory_id: 'TRJ_002',
    plate_number: 'DL01CZ9999',
    start_time: '2026-09-05T09:10:00',
    end_time: '2026-09-05T09:40:12',
    total_distance_km: 7.2,
    average_speed_kmph: 42.1,
    camera_count: 3,
    route_geometry: [
      [26.9125, 75.8562],
      [26.9172, 75.8205],
      [26.9188, 75.8115]
    ],
    waypoints: [
      { camera_id: 'CAM_012', camera_name: 'Delhi Highway - Transport Nagar Toll', timestamp: '2026-09-05T09:10:00', speed_kmph: 45.0, latitude: 26.9125, longitude: 75.8562 },
      { camera_id: 'CAM_004', camera_name: 'MI Road - Ajmeri Gate Chauraha', timestamp: '2026-09-05T09:28:40', speed_kmph: 39.5, latitude: 26.9172, longitude: 75.8205 },
      { camera_id: 'CAM_003', camera_name: 'MI Road - Panch Batti Intersection', timestamp: '2026-09-05T09:40:12', speed_kmph: 41.8, latitude: 26.9188, longitude: 75.8115, is_anomaly: true, anomaly_reason: 'Blacklisted Vehicle Intercept Trigger' }
    ],
    anomalies: ['CRITICAL: Active Stolen Vehicle Blacklist Match'],
    is_valid: true,
    vehicle_type: 'car'
  },
  'HR26XY4040': {
    trajectory_id: 'TRJ_003',
    plate_number: 'HR26XY4040',
    start_time: '2026-09-05T09:37:15',
    end_time: '2026-09-05T09:38:45',
    total_distance_km: 14.8,
    average_speed_kmph: 592.0,
    camera_count: 2,
    route_geometry: [
      [26.8152, 75.7720],
      [26.9850, 75.7610]
    ],
    waypoints: [
      { camera_id: 'CAM_011', camera_name: 'Tonk Road - Sanganer Flyover Entry', timestamp: '2026-09-05T09:37:15', speed_kmph: 60.0, latitude: 26.8152, longitude: 75.7720 },
      { camera_id: 'CAM_015', camera_name: 'Sikar Road - VKI Area Gate 1', timestamp: '2026-09-05T09:38:45', speed_kmph: 58.0, latitude: 26.9850, longitude: 75.7610, is_anomaly: true, anomaly_reason: 'Physically impossible travel time: 14.8 km in 90s (592 km/h) -> Probable Cloned Plate' }
    ],
    anomalies: ['ANOMALOUS_MOVEMENT: Implausible velocity (592 km/h required speed)', 'SUSPECTED_CLONED_PLATE'],
    is_valid: false,
    vehicle_type: 'truck'
  }
};

export const MOCK_PREDICTION_RESULTS: PredictionResult[] = [
  { road_id: 'RD_01', road_name: 'Ajmer Expressway Corridor', current_volume: 1420, predicted_volume_30m: 1650, predicted_congestion: 'LOW', confidence: 0.94, model_loaded: true },
  { road_id: 'RD_02', road_name: 'Mirza Ismail (MI) Arterial', current_volume: 980, predicted_volume_30m: 1240, predicted_congestion: 'HIGH', confidence: 0.89, model_loaded: true },
  { road_id: 'RD_03', road_name: 'Jawaharlal Nehru (JL) Marg', current_volume: 2150, predicted_volume_30m: 2480, predicted_congestion: 'HIGH', confidence: 0.91, model_loaded: true },
  { road_id: 'RD_05', road_name: 'Tonk Road National Highway', current_volume: 1890, predicted_volume_30m: 2310, predicted_congestion: 'SEVERE', confidence: 0.92, model_loaded: true },
  { road_id: 'RD_10', road_name: 'Heritage Walled City Spine', current_volume: 1320, predicted_volume_30m: 1510, predicted_congestion: 'SEVERE', confidence: 0.88, model_loaded: true }
];

export const MOCK_FEATURE_IMPORTANCE = [
  { feature: 'current_vehicle_count', importance: 0.38 },
  { feature: 'previous_congestion_score', importance: 0.24 },
  { feature: 'hour_of_day', importance: 0.18 },
  { feature: 'average_speed_trend', importance: 0.11 },
  { feature: 'day_of_week', importance: 0.05 },
  { feature: 'road_capacity_ratio', importance: 0.04 }
];
