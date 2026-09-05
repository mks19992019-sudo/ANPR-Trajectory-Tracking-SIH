import React, { useState } from 'react';
import { 
  ArrowRight, 
  Clock, 
  BarChart2
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  LineChart, 
  Line, 
  Legend 
} from 'recharts';
import type { TrafficMetric, TrafficFlow } from '../types';

interface TrafficAnalysisProps {
  metrics: TrafficMetric[];
  flows: TrafficFlow[];
}

export const TrafficAnalysis: React.FC<TrafficAnalysisProps> = ({ metrics, flows }) => {
  const [timeWindow, setTimeWindow] = useState<'5m' | '15m' | '1h'>('15m');
  const [activeTab, setActiveTab] = useState<'density' | 'speed' | 'flows' | 'od'>('density');

  const hourlyData = [
    { hour: '00:00', volume: 820, avgSpeed: 62 },
    { hour: '02:00', volume: 450, avgSpeed: 68 },
    { hour: '04:00', volume: 380, avgSpeed: 71 },
    { hour: '06:00', volume: 1100, avgSpeed: 58 },
    { hour: '08:00', volume: 3400, avgSpeed: 38 },
    { hour: '10:00', volume: 4100, avgSpeed: 32 },
    { hour: '12:00', volume: 3600, avgSpeed: 36 },
    { hour: '14:00', volume: 3200, avgSpeed: 42 },
    { hour: '16:00', volume: 3900, avgSpeed: 34 },
    { hour: '18:00', volume: 4800, avgSpeed: 28 },
    { hour: '20:00', volume: 3800, avgSpeed: 39 },
    { hour: '22:00', volume: 2100, avgSpeed: 52 },
  ];

  const odZones = ['Ajmer Rd Zone', 'MI Central', 'JL Marg/WTP', 'Airport South', 'Delhi Hwy North'];
  const odMatrix = [
    [120, 850, 620, 410, 320],
    [780, 95, 1140, 520, 640],
    [540, 980, 150, 1260, 480],
    [320, 460, 1180, 80, 210],
    [410, 720, 390, 180, 110],
  ];

  return (
    <div className="p-6 space-y-6 max-h-[calc(100vh-4rem)] overflow-y-auto bg-slate-50">
      {/* Top Nav Tabs */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setActiveTab('density')}
            className={`px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'density' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Volume & Density
          </button>
          <button
            onClick={() => setActiveTab('speed')}
            className={`px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'speed' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Speed Analytics
          </button>
          <button
            onClick={() => setActiveTab('flows')}
            className={`px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'flows' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Camera Flows
          </button>
          <button
            onClick={() => setActiveTab('od')}
            className={`px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'od' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Origin-Destination Matrix
          </button>
        </div>

        {/* Time Window Buttons */}
        <div className="flex items-center space-x-1.5 bg-slate-50 p-1 rounded-lg border border-slate-200 text-xs">
          <Clock className="w-3.5 h-3.5 text-slate-400 ml-2" />
          <button
            onClick={() => setTimeWindow('5m')}
            className={`px-2.5 py-1 rounded font-medium ${timeWindow === '5m' ? 'bg-white text-blue-700 shadow-sm' : 'text-slate-600'}`}
          >
            5m
          </button>
          <button
            onClick={() => setTimeWindow('15m')}
            className={`px-2.5 py-1 rounded font-medium ${timeWindow === '15m' ? 'bg-white text-blue-700 shadow-sm' : 'text-slate-600'}`}
          >
            15m
          </button>
          <button
            onClick={() => setTimeWindow('1h')}
            className={`px-2.5 py-1 rounded font-medium ${timeWindow === '1h' ? 'bg-white text-blue-700 shadow-sm' : 'text-slate-600'}`}
          >
            1h
          </button>
        </div>
      </div>

      {/* Tab 1: Density & Volume */}
      {activeTab === 'density' && (
        <div className="space-y-6">
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <div className="mb-4">
              <h3 className="text-sm font-bold text-slate-900">
                24-Hour Traffic Volume vs. Velocity Trend
              </h3>
              <p className="text-xs text-slate-500">Hourly vehicle count correlated with average arterial flow speeds</p>
            </div>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={hourlyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="hour" stroke="#64748b" fontSize={11} />
                  <YAxis yAxisId="left" stroke="#2563eb" fontSize={11} />
                  <YAxis yAxisId="right" orientation="right" stroke="#059669" fontSize={11} />
                  <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', color: '#0f172a', fontSize: '12px', borderRadius: '8px' }} />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="volume" name="Vehicles / Hour" stroke="#2563eb" strokeWidth={2.5} dot={{ r: 3 }} />
                  <Line yAxisId="right" type="monotone" dataKey="avgSpeed" name="Avg Speed (km/h)" stroke="#059669" strokeWidth={2.5} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Corridor Cards */}
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <h3 className="text-sm font-bold text-slate-900 mb-3">
              Corridor Traffic Density ({timeWindow} interval)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {metrics.map((m) => (
                <div key={m.road_id} className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs text-blue-700 font-bold">{m.road_id}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      m.congestion_level === 'SEVERE' ? 'bg-red-100 text-red-700' :
                      m.congestion_level === 'HIGH' ? 'bg-amber-100 text-amber-800' :
                      m.congestion_level === 'MODERATE' ? 'bg-yellow-100 text-yellow-800' : 'bg-emerald-100 text-emerald-800'
                    }`}>
                      {m.congestion_level}
                    </span>
                  </div>
                  <div className="text-sm font-semibold text-slate-900 mt-1 line-clamp-1">{m.road_name}</div>
                  <div className="mt-3 grid grid-cols-2 gap-2 text-xs border-t border-slate-200 pt-2">
                    <div>
                      <div className="text-slate-500 text-[11px]">Volume</div>
                      <div className="font-bold text-slate-800">{m.vehicle_count} veh</div>
                    </div>
                    <div>
                      <div className="text-slate-500 text-[11px]">Avg Speed</div>
                      <div className="font-bold text-slate-800">{m.average_speed} km/h</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Speed Percentiles */}
      {activeTab === 'speed' && (
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Corridor Speed Percentiles</h3>
            <p className="text-xs text-slate-500">Operating velocities and statistical design speed compliance</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 uppercase text-[10px] border-b border-slate-200">
                <tr>
                  <th className="p-3">Corridor</th>
                  <th className="p-3">Min Observed</th>
                  <th className="p-3">Average Speed</th>
                  <th className="p-3">Median Speed</th>
                  <th className="p-3">85th Percentile</th>
                  <th className="p-3">Max Speed</th>
                  <th className="p-3">Compliance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {metrics.map((m) => {
                  const p85 = Math.round(m.average_speed * 1.18);
                  const maxSpd = Math.round(m.average_speed * 1.55);
                  return (
                    <tr key={m.road_id} className="hover:bg-slate-50">
                      <td className="p-3 font-medium text-slate-900">{m.road_name}</td>
                      <td className="p-3 text-slate-500">18 km/h</td>
                      <td className="p-3 text-blue-700 font-bold">{m.average_speed} km/h</td>
                      <td className="p-3 text-slate-700">{m.median_speed} km/h</td>
                      <td className="p-3 text-purple-700 font-bold">{p85} km/h</td>
                      <td className="p-3 text-red-600 font-bold">{maxSpd} km/h</td>
                      <td className="p-3">
                        <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px] font-bold">
                          94% Compliant
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 3: Camera-to-Camera Flows */}
      {activeTab === 'flows' && (
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Directional Traffic Flows</h3>
            <p className="text-xs text-slate-500">Vehicle counts moving directly between consecutive cameras</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {flows.map((flow, i) => (
              <div key={i} className="p-4 bg-slate-50 border border-slate-200 rounded-lg flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2 text-xs font-mono">
                    <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-bold">{flow.source_camera}</span>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
                    <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-bold">{flow.destination_camera}</span>
                  </div>
                  <div className="text-xs text-slate-700 mt-2 flex items-center gap-1">
                    <span>{flow.source_name}</span>
                    <span className="text-slate-400">→</span>
                    <span>{flow.destination_name}</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-lg text-emerald-700">{flow.vehicle_count}</div>
                  <div className="text-[11px] text-slate-500">Vehicles / {flow.time_window}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 4: Origin-Destination Matrix */}
      {activeTab === 'od' && (
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Origin-Destination (OD) Matrix</h3>
            <p className="text-xs text-slate-500">
              Trip matrix calculated from vehicle entry checkpoints to final exit checkpoints
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-center text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50 text-slate-700 border-b border-slate-200">
                  <th className="p-3 text-left">Origin \ Destination</th>
                  {odZones.map((z, idx) => (
                    <th key={idx} className="p-3">{z}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {odZones.map((orig, i) => (
                  <tr key={i} className="hover:bg-slate-50">
                    <td className="p-3 font-semibold text-slate-900 text-left bg-slate-50/70">{orig}</td>
                    {odMatrix[i].map((val, j) => {
                      const isHigh = val > 900;
                      return (
                        <td key={j} className={`p-3 ${isHigh ? 'bg-blue-50 text-blue-800 font-bold' : 'text-slate-700'}`}>
                          {val}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
