import React, { useState } from 'react';
import { 
  Car, 
  Camera, 
  Gauge, 
  AlertTriangle, 
  Activity, 
  ArrowUpRight, 
  ShieldAlert, 
  CheckCircle2, 
  Layers,
  Search,
  Clock,
  ArrowRight
} from 'lucide-react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import type { Camera as CameraType, Alert, TrafficMetric, SystemStats, ANPREvent } from '../types';
import { formatPlate } from '../services/api';
import type { PageId } from '../components/layout/Sidebar';

// Operational pins
const cameraIcon = new L.DivIcon({
  className: 'custom-pin',
  html: `<div style="background-color: #2563eb; width: 11px; height: 11px; border-radius: 50%; border: 2px solid #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.3);"></div>`,
  iconSize: [11, 11],
  iconAnchor: [5, 5]
});

const alertCameraIcon = new L.DivIcon({
  className: 'custom-pin-alert',
  html: `<div style="background-color: #dc2626; width: 14px; height: 14px; border-radius: 50%; border: 2px solid #ffffff;" class="incident-marker"></div>`,
  iconSize: [14, 14],
  iconAnchor: [7, 7]
});

interface DashboardProps {
  stats: SystemStats;
  cameras: CameraType[];
  alerts: Alert[];
  metrics: TrafficMetric[];
  recentEvents: ANPREvent[];
  maskPrivacy: boolean;
  onNavigate: (page: PageId) => void;
  onSelectPlateForTrajectory: (plate: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  stats,
  cameras,
  alerts,
  metrics,
  recentEvents,
  maskPrivacy,
  onNavigate,
  onSelectPlateForTrajectory
}) => {
  const [filterAlertsOnly, setFilterAlertsOnly] = useState(false);

  const speedData = [
    { range: '<30', count: 420 },
    { range: '30-50', count: 1850 },
    { range: '50-70', count: 2420 },
    { range: '70-90', count: 980 },
    { range: '>90', count: 215 },
  ];

  const displayedCameras = filterAlertsOnly
    ? cameras.filter(cam => alerts.some(a => a.camera_id === cam.camera_id))
    : cameras;

  return (
    <div className="p-5 space-y-5 overflow-y-auto max-h-[calc(100vh-3.5rem)] bg-slate-50">
      {/* 1. TOP OPERATIONAL KPI SUMMARY STRIP */}
      <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-sm">
        <div className="grid grid-cols-2 sm:grid-cols-5 divide-y sm:divide-y-0 sm:divide-x divide-slate-200">
          {/* KPI 1 */}
          <div className="px-4 py-1.5 first:pl-2">
            <div className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">Total Detections</div>
            <div className="flex items-baseline space-x-1.5 mt-0.5">
              <span className="text-xl font-bold font-mono text-slate-900 num-mono">{stats.total_vehicles_today.toLocaleString()}</span>
              <span className="text-[11px] font-medium text-slate-500">vehicles</span>
            </div>
          </div>

          {/* KPI 2 */}
          <div className="px-4 py-1.5">
            <div className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">Active Checkpoints</div>
            <div className="flex items-baseline space-x-1.5 mt-0.5">
              <span className="text-xl font-bold font-mono text-slate-900 num-mono">{stats.active_cameras}</span>
              <span className="text-xs text-slate-500 font-mono">/ {stats.total_cameras}</span>
              <span className="text-[11px] text-emerald-700 font-semibold ml-1">(92%)</span>
            </div>
          </div>

          {/* KPI 3 */}
          <div className="px-4 py-1.5">
            <div className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">Arterial Flow Velocity</div>
            <div className="flex items-baseline space-x-1.5 mt-0.5">
              <span className="text-xl font-bold font-mono text-slate-900 num-mono">{stats.average_speed_city}</span>
              <span className="text-xs text-slate-500 font-mono">km/h</span>
            </div>
          </div>

          {/* KPI 4 */}
          <div className="px-4 py-1.5">
            <div className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">Congested Corridors</div>
            <div className="flex items-baseline space-x-1.5 mt-0.5">
              <span className="text-xl font-bold font-mono text-amber-700 num-mono">{stats.congested_corridors}</span>
              <span className="text-xs text-slate-500">Roads slow</span>
            </div>
          </div>

          {/* KPI 5: Alerts (High Priority) */}
          <div className="px-4 py-1.5 bg-red-50/50 rounded-r">
            <div className="text-[11px] font-bold text-red-700 uppercase tracking-wider flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5 text-red-600" />
              <span>Active Incidents</span>
            </div>
            <div className="flex items-baseline space-x-1.5 mt-0.5">
              <span className="text-xl font-bold font-mono text-red-700 num-mono">{alerts.length}</span>
              <span className="text-[11px] font-medium text-red-800">Action Required</span>
            </div>
          </div>
        </div>
      </div>

      {/* 2. MAIN COMMAND WORKSPACE: LARGE GIS MAP (68%) + PRIORITY ALERTS (32%) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch">
        {/* Large GIS Map */}
        <div className="lg:col-span-8 bg-white border border-slate-200 rounded-lg shadow-sm flex flex-col min-h-[460px]">
          {/* Map Header Toolbar */}
          <div className="px-4 py-2.5 border-b border-slate-200 flex items-center justify-between bg-slate-50/60 shrink-0">
            <div className="flex items-center space-x-2">
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                City Surveillance GIS Grid
              </h2>
              <span className="text-xs text-slate-400">•</span>
              <span className="text-xs text-slate-500 font-mono">Jaipur Metropolitan Grid</span>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => setFilterAlertsOnly(!filterAlertsOnly)}
                className={`text-[11px] px-2.5 py-1 rounded font-medium border transition-colors ${
                  filterAlertsOnly 
                    ? 'bg-red-50 border-red-300 text-red-700 font-semibold' 
                    : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-100'
                }`}
              >
                {filterAlertsOnly ? 'Showing Incidents Only' : 'Filter Incident Checkpoints'}
              </button>
              <button
                onClick={() => onNavigate('cameras')}
                className="text-[11px] font-semibold text-blue-700 hover:text-blue-800 flex items-center space-x-1 pl-2 border-l border-slate-200"
              >
                <span>Full Map</span>
                <ArrowUpRight className="w-3 h-3" />
              </button>
            </div>
          </div>

          {/* Leaflet GIS Map Container */}
          <div className="flex-1 relative min-h-[400px]">
            <MapContainer
              center={[26.9050, 75.8050]}
              zoom={12}
              scrollWheelZoom={true}
              className="h-full w-full rounded-b-lg"
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
              />

              {/* Checkpoint Markers */}
              {displayedCameras.map((cam) => {
                const hasAlert = alerts.some(a => a.camera_id === cam.camera_id);
                return (
                  <Marker
                    key={cam.camera_id}
                    position={[cam.latitude, cam.longitude]}
                    icon={hasAlert ? alertCameraIcon : cameraIcon}
                  >
                    <Popup>
                      <div className="text-xs p-1">
                        <div className="font-bold text-slate-900">{cam.camera_name}</div>
                        <div className="text-blue-700 font-mono text-[11px] mt-0.5">{cam.camera_id} • {cam.location}</div>
                        <div className="mt-1 text-slate-600">
                          Status: <span className="font-semibold text-emerald-700">{cam.status}</span>
                        </div>
                      </div>
                    </Popup>
                  </Marker>
                );
              })}
            </MapContainer>

            {/* In-Map Legend Overlay */}
            <div className="absolute bottom-3 right-3 bg-white/95 backdrop-blur border border-slate-200 px-3 py-2 rounded text-[11px] font-mono text-slate-600 shadow-sm z-[1000] space-y-1">
              <div className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-600"></span>
                <span>Active Checkpoint</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full bg-red-600"></span>
                <span>Active Incident Flagged</span>
              </div>
            </div>
          </div>
        </div>

        {/* Priority Incidents Feed (Operational Alert Command) */}
        <div className="lg:col-span-4 bg-white border border-slate-200 rounded-lg shadow-sm flex flex-col">
          <div className="px-4 py-2.5 border-b border-slate-200 flex items-center justify-between bg-slate-50/60 shrink-0">
            <div className="flex items-center space-x-2">
              <ShieldAlert className="w-4 h-4 text-red-600" />
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                Priority Incident Queue
              </h2>
            </div>
            <button
              onClick={() => onNavigate('alerts')}
              className="text-[11px] font-semibold text-blue-700 hover:text-blue-800 flex items-center space-x-1"
            >
              <span>View All ({alerts.length})</span>
              <ArrowUpRight className="w-3 h-3" />
            </button>
          </div>

          <div className="p-3 space-y-2.5 flex-1 overflow-y-auto max-h-[460px]">
            {alerts.map((alt) => {
              const isCritical = alt.severity === 'CRITICAL';
              return (
                <div
                  key={alt.alert_id}
                  className={`p-3 rounded border transition-colors ${
                    isCritical 
                      ? 'bg-red-50/60 border-red-200' 
                      : 'bg-amber-50/50 border-amber-200'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded font-mono uppercase ${
                      isCritical ? 'bg-red-200 text-red-900' : 'bg-amber-200 text-amber-900'
                    }`}>
                      {alt.severity} • {alt.alert_type.replace(/_/g, ' ')}
                    </span>
                    <span className="text-[10px] font-mono text-slate-500">
                      {(alt.timestamp || '').includes('T') ? alt.timestamp.split('T')[1].slice(0, 8) : (alt.timestamp || '')}
                    </span>
                  </div>

                  <div className="mt-1.5 flex items-center justify-between">
                    <div className="font-mono text-xs font-bold text-slate-900">
                      {formatPlate(alt.plate_number, maskPrivacy)}
                    </div>
                    <span className="text-[11px] text-slate-500 font-mono">
                      {alt.camera_id}
                    </span>
                  </div>

                  <p className="text-xs text-slate-600 mt-1 leading-snug">
                    {alt.message || alt.description || 'Incident flagged by detection rules'}
                  </p>

                  <div className="mt-2.5 pt-2 border-t border-slate-200/80 flex items-center justify-between">
                    <span className="text-[11px] text-slate-500">Status: <span className="font-semibold text-slate-700">{alt.status}</span></span>
                    {alt.plate_number !== 'CORRIDOR_ALERT' && (
                      <button
                        onClick={() => {
                          onSelectPlateForTrajectory(alt.plate_number);
                          onNavigate('trajectory');
                        }}
                        className="inline-flex items-center space-x-1 text-[11px] font-bold text-blue-700 hover:text-blue-900"
                      >
                        <span>Investigate Route</span>
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* 3. BOTTOM SECTION: CORRIDOR CONGESTION + VELOCITY TREND + RECENT LOG */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Corridor Bottleneck Status Table */}
        <div className="bg-white border border-slate-200 rounded-lg shadow-sm flex flex-col">
          <div className="px-4 py-2.5 border-b border-slate-200 flex items-center justify-between bg-slate-50/60">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              Corridor Congestion Status
            </h3>
            <button
              onClick={() => onNavigate('congestion')}
              className="text-[11px] font-semibold text-blue-700 hover:text-blue-800"
            >
              Details
            </button>
          </div>
          <div className="overflow-x-auto flex-1">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] border-b border-slate-200 font-medium">
                <tr>
                  <th className="py-2 px-3">Corridor</th>
                  <th className="py-2 px-3">Velocity</th>
                  <th className="py-2 px-3">Level</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {metrics.slice(0, 5).map((m) => (
                  <tr key={m.road_id} className="hover:bg-slate-50">
                    <td className="py-2 px-3 font-sans text-slate-900 truncate max-w-[140px]" title={m.road_name}>
                      {m.road_name}
                    </td>
                    <td className="py-2 px-3 text-slate-700 font-semibold">{m.average_speed} km/h</td>
                    <td className="py-2 px-3">
                      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded uppercase ${
                        m.congestion_level === 'SEVERE' ? 'bg-red-100 text-red-800' :
                        m.congestion_level === 'HIGH' ? 'bg-amber-100 text-amber-800' :
                        m.congestion_level === 'MODERATE' ? 'bg-yellow-100 text-yellow-800' : 'bg-emerald-100 text-emerald-800'
                      }`}>
                        {m.congestion_level}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Speed Distribution Bins */}
        <div className="bg-white border border-slate-200 rounded-lg shadow-sm p-4 flex flex-col">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              Velocity Distribution
            </h3>
            <span className="text-[11px] text-slate-500 font-mono">City Artery Scan</span>
          </div>
          <p className="text-[11px] text-slate-500 mb-2">Detections binned by clocked speed (km/h)</p>
          <div className="h-44 w-full flex-1">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={speedData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="range" stroke="#64748b" fontSize={10} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={10} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#cbd5e1', color: '#0f172a', fontSize: '11px', borderRadius: '4px' }}
                />
                <Bar dataKey="count" fill="#2563eb" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Detections Mini Log */}
        <div className="bg-white border border-slate-200 rounded-lg shadow-sm flex flex-col">
          <div className="px-4 py-2.5 border-b border-slate-200 flex items-center justify-between bg-slate-50/60">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              Recent Observations
            </h3>
            <button
              onClick={() => onNavigate('live')}
              className="text-[11px] font-semibold text-blue-700 hover:text-blue-800"
            >
              Full Log
            </button>
          </div>
          <div className="divide-y divide-slate-100 flex-1 overflow-y-auto max-h-56">
            {recentEvents.slice(0, 5).map((evt) => (
              <div
                key={evt.event_id}
                onClick={() => {
                  onSelectPlateForTrajectory(evt.plate_number);
                  onNavigate('trajectory');
                }}
                className="p-2.5 hover:bg-slate-50 cursor-pointer flex items-center justify-between transition-colors"
              >
                <div>
                  <div className="font-mono text-xs font-bold text-blue-800">
                    {formatPlate(evt.plate_number, maskPrivacy)}
                  </div>
                  <div className="text-[11px] text-slate-500 font-mono mt-0.5">
                    {evt.camera_id} • {(evt.timestamp || '').includes('T') ? evt.timestamp.split('T')[1].slice(0, 8) : (evt.timestamp || '')}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-mono text-xs font-semibold text-slate-800">{evt.speed_kmph} km/h</div>
                  <span className="text-[10px] uppercase text-slate-500 font-medium">{evt.vehicle_type}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
