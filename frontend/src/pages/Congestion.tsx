import React from 'react';
import { Gauge, Activity } from 'lucide-react';
import type { TrafficMetric } from '../types';

interface CongestionProps {
  metrics: TrafficMetric[];
}

export const Congestion: React.FC<CongestionProps> = ({ metrics }) => {
  const getLevelBadge = (level: string) => {
    switch (level) {
      case 'SEVERE': return 'bg-red-100 text-red-800 border-red-200';
      case 'HIGH': return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'MODERATE': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.85) return 'text-red-600';
    if (score >= 0.65) return 'text-amber-600';
    if (score >= 0.45) return 'text-yellow-700';
    return 'text-emerald-600';
  };

  return (
    <div className="p-6 space-y-6 max-h-[calc(100vh-4rem)] overflow-y-auto bg-slate-50">
      {/* Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-600" />
            Corridor Bottlenecks & Congestion Scores
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Calculated from Volume-to-Capacity ratio and speed reduction against posted speed limits
          </p>
        </div>

        <div className="bg-slate-50 px-4 py-2 rounded-lg border border-slate-200 text-xs font-mono text-slate-700">
          <span className="text-blue-700 font-bold">Congestion Index</span> = (Volume / Capacity) × (1 - (v / v_limit))
        </div>
      </div>

      {/* Corridor Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {metrics.map((m) => (
          <div key={m.road_id} className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-xs font-bold text-blue-700">{m.road_id}</span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${getLevelBadge(m.congestion_level)}`}>
                    {m.congestion_level}
                  </span>
                </div>
                <h3 className="text-sm font-bold text-slate-900 mt-1">{m.road_name}</h3>
              </div>
              <div className="text-right">
                <div className={`text-2xl font-bold ${getScoreColor(m.congestion_score)}`}>
                  {(m.congestion_score * 100).toFixed(0)}
                </div>
                <div className="text-[10px] text-slate-400 font-semibold uppercase">Score</div>
              </div>
            </div>

            {/* Speed & Volume comparison */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-slate-500 flex items-center gap-1">
                  <Gauge className="w-3.5 h-3.5 text-slate-400" />
                  Observed Velocity
                </span>
                <span className="font-bold text-slate-800">{m.average_speed} km/h</span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden border border-slate-200">
                <div
                  className={`h-full ${
                    m.congestion_level === 'SEVERE' ? 'bg-red-500' :
                    m.congestion_level === 'HIGH' ? 'bg-amber-500' :
                    m.congestion_level === 'MODERATE' ? 'bg-yellow-500' : 'bg-emerald-500'
                  }`}
                  style={{ width: `${Math.max(10, 100 - m.congestion_score * 100)}%` }}
                ></div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 pt-3 border-t border-slate-100 text-xs">
              <div>
                <span className="text-slate-500 text-[11px]">15m Volume</span>
                <div className="font-bold text-slate-800">{m.vehicle_count} vehicles</div>
              </div>
              <div>
                <span className="text-slate-500 text-[11px]">Median Velocity</span>
                <div className="font-bold text-slate-800">{m.median_speed} km/h</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
