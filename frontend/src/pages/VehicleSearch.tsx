import React, { useState, useEffect } from 'react';
import { 
  Search, 
  MapPin, 
  AlertTriangle, 
  CheckCircle2, 
  Navigation, 
  Clock, 
  Gauge, 
  Milestone, 
  ShieldAlert, 
  TrendingUp,
  FileSearch
} from 'lucide-react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import type { Trajectory } from '../types';
import { apiService, formatPlate } from '../services/api';

const createWaypointIcon = (index: number, isAnomaly = false) => {
  const bg = isAnomaly ? '#dc2626' : '#2563eb';
  return new L.DivIcon({
    className: 'waypoint-pin',
    html: `<div style="background-color: ${bg}; color: #ffffff; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; border: 2px solid #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.25);">${index}</div>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11]
  });
};

interface VehicleSearchProps {
  initialPlate?: string;
  maskPrivacy: boolean;
}

export const VehicleSearch: React.FC<VehicleSearchProps> = ({
  initialPlate = 'RJ14AB1234',
  maskPrivacy
}) => {
  const [plateInput, setPlateInput] = useState(initialPlate);
  const [trajectory, setTrajectory] = useState<Trajectory | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedWaypoint, setSelectedWaypoint] = useState<number | null>(null);

  useEffect(() => {
    if (initialPlate) {
      setPlateInput(initialPlate);
      loadTrajectory(initialPlate);
    }
  }, [initialPlate]);

  const loadTrajectory = async (plate: string) => {
    if (!plate.trim()) return;
    setLoading(true);
    setSelectedWaypoint(null);
    const data = await apiService.getTrajectory(plate);
    setTrajectory(data);
    setLoading(false);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadTrajectory(plateInput);
  };

  const speedChartData = trajectory?.waypoints.map((wp, i) => ({
    name: `Stop ${i + 1}`,
    camera: wp.camera_id,
    speed: wp.speed_kmph,
    time: wp.timestamp.split('T')[1]
  })) || [];

  return (
    <div className="p-5 space-y-5 max-h-[calc(100vh-3.5rem)] overflow-y-auto bg-slate-50">
      {/* 1. INVESTIGATION SEARCH & PRESET CASES */}
      <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm space-y-3">
        <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-2.5">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              placeholder="Enter Target Vehicle License Plate (e.g. RJ14AB1234, DL01CZ9999)..."
              value={plateInput}
              onChange={(e) => setPlateInput(e.target.value.toUpperCase())}
              className="w-full bg-slate-50 border border-slate-200 rounded pl-10 pr-4 py-2 text-xs font-mono font-bold text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:bg-white transition-colors"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-5 py-2 bg-slate-900 hover:bg-slate-800 text-white font-medium rounded text-xs transition-colors flex items-center justify-center space-x-2 shrink-0"
          >
            <Navigation className="w-3.5 h-3.5" />
            <span>{loading ? 'Reconstructing...' : 'Reconstruct Trajectory'}</span>
          </button>
        </form>

        {/* Presets */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100 text-xs">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Test Cases:</span>
          <button
            onClick={() => { setPlateInput('RJ14AB1234'); loadTrajectory('RJ14AB1234'); }}
            className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-mono text-[11px] font-medium transition-colors"
          >
            RJ14AB1234 (Normal Transit)
          </button>
          <button
            onClick={() => { setPlateInput('DL01CZ9999'); loadTrajectory('DL01CZ9999'); }}
            className="px-2.5 py-1 rounded bg-red-50 hover:bg-red-100 text-red-800 border border-red-200 font-mono text-[11px] font-medium transition-colors flex items-center space-x-1"
          >
            <ShieldAlert className="w-3 h-3 text-red-600" />
            <span>DL01CZ9999 (Stolen Blacklist Match)</span>
          </button>
          <button
            onClick={() => { setPlateInput('HR26XY4040'); loadTrajectory('HR26XY4040'); }}
            className="px-2.5 py-1 rounded bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 font-mono text-[11px] font-medium transition-colors flex items-center space-x-1"
          >
            <AlertTriangle className="w-3 h-3 text-amber-600" />
            <span>HR26XY4040 (592 km/h Impossible Hop)</span>
          </button>
        </div>
      </div>

      {trajectory && (
        <div className="space-y-5">
          {/* 2. CRITICAL ANOMALY BANNER IF TRIGGERED */}
          {trajectory.anomalies.length > 0 && (
            <div className="p-3.5 bg-red-50 border-l-4 border-red-600 rounded-r-lg shadow-sm flex items-start space-x-3 text-red-900">
              <ShieldAlert className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
              <div className="flex-1">
                <div className="text-xs font-bold uppercase tracking-wider text-red-800">
                  Spatial-Temporal Anomalies Flagged on This Trajectory
                </div>
                <div className="mt-1 space-y-0.5 text-xs">
                  {trajectory.anomalies.map((anom, idx) => (
                    <div key={idx} className="font-medium text-red-700">
                      • {anom}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 3. VEHICLE SUMMARY DOSSIER STRIP */}
          <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-sm">
            <div className="grid grid-cols-2 sm:grid-cols-6 divide-y sm:divide-y-0 sm:divide-x divide-slate-200 text-xs">
              <div className="px-3 py-1 first:pl-1">
                <span className="text-slate-400 uppercase text-[10px] font-semibold tracking-wider block">Target Plate</span>
                <span className="font-mono text-sm font-bold text-slate-900 mt-0.5 block">
                  {formatPlate(trajectory.plate_number, maskPrivacy)}
                </span>
              </div>

              <div className="px-3 py-1">
                <span className="text-slate-400 uppercase text-[10px] font-semibold tracking-wider block">Vehicle Type</span>
                <span className="capitalize font-medium text-slate-800 mt-0.5 block">{trajectory.vehicle_type}</span>
              </div>

              <div className="px-3 py-1">
                <span className="text-slate-400 uppercase text-[10px] font-semibold tracking-wider block">Total Distance</span>
                <span className="font-bold text-slate-900 font-mono mt-0.5 block">{trajectory.total_distance_km} km</span>
              </div>

              <div className="px-3 py-1">
                <span className="text-slate-400 uppercase text-[10px] font-semibold tracking-wider block">Reconstructed Speed</span>
                <span className="font-bold text-slate-900 font-mono mt-0.5 block">{trajectory.average_speed_kmph.toFixed(1)} km/h</span>
              </div>

              <div className="px-3 py-1">
                <span className="text-slate-400 uppercase text-[10px] font-semibold tracking-wider block">Checkpoints</span>
                <span className="font-bold text-slate-900 font-mono mt-0.5 block">{trajectory.camera_count} Nodes</span>
              </div>

              <div className="px-3 py-1">
                <span className="text-slate-400 uppercase text-[10px] font-semibold tracking-wider block">Plausibility</span>
                <span className={`inline-block mt-0.5 px-2 py-0.5 rounded font-mono font-bold text-[10px] uppercase ${
                  trajectory.is_valid ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                }`}>
                  {trajectory.is_valid ? 'PLAUSIBLE' : 'IMPLAUSIBLE'}
                </span>
              </div>
            </div>
          </div>

          {/* 4. SPLIT INVESTIGATION VIEW: GIS MAP (60%) + TIMELINE & SPEED (40%) */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch">
            {/* GIS Route Map */}
            <div className="lg:col-span-7 bg-white border border-slate-200 rounded-lg shadow-sm flex flex-col min-h-[460px]">
              <div className="px-4 py-2.5 border-b border-slate-200 flex items-center justify-between bg-slate-50/60">
                <div className="flex items-center space-x-2">
                  <Navigation className="w-4 h-4 text-blue-700" />
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                    Route Map Visualization
                  </h3>
                </div>
                <div className="text-[11px] font-mono text-slate-500">
                  Time: {trajectory.start_time.split('T')[1]} → {trajectory.end_time.split('T')[1]}
                </div>
              </div>

              <div className="flex-1 relative min-h-[400px]">
                <MapContainer
                  center={trajectory.route_geometry[0] || [26.9050, 75.8050]}
                  zoom={12}
                  scrollWheelZoom={true}
                  className="h-full w-full rounded-b-lg"
                >
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
                  />
                  <Polyline
                    positions={trajectory.route_geometry}
                    color={trajectory.is_valid ? '#2563eb' : '#dc2626'}
                    weight={4}
                    dashArray={trajectory.is_valid ? undefined : '6, 8'}
                  />

                  {trajectory.waypoints.map((wp, idx) => (
                    <Marker
                      key={idx}
                      position={[wp.latitude, wp.longitude]}
                      icon={createWaypointIcon(idx + 1, wp.is_anomaly)}
                      eventHandlers={{
                        click: () => setSelectedWaypoint(idx)
                      }}
                    >
                      <Popup>
                        <div className="text-xs p-1">
                          <div className="font-bold text-slate-900">Stop #{idx + 1}: {wp.camera_name}</div>
                          <div className="text-blue-700 font-mono mt-0.5">{wp.camera_id}</div>
                          <div className="text-slate-600 mt-1">Time: {wp.timestamp.replace('T', ' ')}</div>
                          <div className="text-slate-600">Velocity: <span className="font-bold">{wp.speed_kmph} km/h</span></div>
                          {wp.anomaly_reason && (
                            <div className="mt-1 text-red-700 font-semibold border-t border-red-200 pt-1">
                              ⚠️ {wp.anomaly_reason}
                            </div>
                          )}
                        </div>
                      </Popup>
                    </Marker>
                  ))}
                </MapContainer>
              </div>
            </div>

            {/* Checkpoint Sequence & Velocity Profile */}
            <div className="lg:col-span-5 flex flex-col space-y-5">
              {/* Chronological Checkpoints Table */}
              <div className="bg-white border border-slate-200 rounded-lg shadow-sm flex flex-col flex-1">
                <div className="px-4 py-2.5 border-b border-slate-200 flex items-center justify-between bg-slate-50/60">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                    Chronological Checkpoints
                  </h3>
                  <span className="text-[11px] text-slate-500 font-mono">{trajectory.waypoints.length} Nodes</span>
                </div>

                <div className="divide-y divide-slate-100 overflow-y-auto max-h-60 flex-1">
                  {trajectory.waypoints.map((wp, i) => {
                    const isSelected = selectedWaypoint === i;
                    return (
                      <div
                        key={i}
                        onClick={() => setSelectedWaypoint(i)}
                        className={`p-3 text-xs transition-colors cursor-pointer ${
                          isSelected ? 'bg-blue-50/70 border-l-4 border-blue-600' :
                          wp.is_anomaly ? 'bg-red-50/60 border-l-4 border-red-600' : 'hover:bg-slate-50'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <span className={`w-5 h-5 rounded-full flex items-center justify-center font-mono text-[10px] font-bold ${
                              wp.is_anomaly ? 'bg-red-600 text-white' : 'bg-slate-900 text-white'
                            }`}>
                              {i + 1}
                            </span>
                            <span className="font-mono font-bold text-slate-900">{wp.camera_id}</span>
                          </div>
                          <span className="font-mono text-slate-500 text-[11px]">
                            {(wp.timestamp || '').includes('T') ? wp.timestamp.split('T')[1].slice(0, 8) : (wp.timestamp || '')}
                          </span>
                        </div>

                        <div className="mt-1 text-slate-700 text-xs truncate pl-7">
                          {wp.camera_name}
                        </div>

                        <div className="mt-1.5 pl-7 flex items-center justify-between text-[11px]">
                          <span className="text-slate-500">Clocked Speed: <span className="font-bold text-slate-900">{wp.speed_kmph} km/h</span></span>
                          {wp.is_anomaly && (
                            <span className="text-red-700 font-bold uppercase text-[10px]">Anomaly Detected</span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Velocity Profile Chart */}
              <div className="bg-white border border-slate-200 rounded-lg shadow-sm p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-1.5">
                    <TrendingUp className="w-3.5 h-3.5 text-blue-700" />
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800">Velocity Profile</h4>
                  </div>
                  <span className="text-[10px] text-slate-400 font-mono">Speed across hops</span>
                </div>

                <div className="h-32 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={speedChartData} margin={{ top: 5, right: 10, left: -25, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                      <XAxis dataKey="name" stroke="#64748b" fontSize={10} tickLine={false} />
                      <YAxis stroke="#64748b" fontSize={10} tickLine={false} domain={[0, 'dataMax + 20']} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#ffffff', borderColor: '#cbd5e1', color: '#0f172a', fontSize: '11px', borderRadius: '4px' }}
                      />
                      <Line type="monotone" dataKey="speed" stroke="#2563eb" strokeWidth={2} dot={{ r: 3.5, fill: '#2563eb' }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
