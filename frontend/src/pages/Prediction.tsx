import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Clock, 
  RefreshCw,
  Cpu,
  BarChart
} from 'lucide-react';
import { ResponsiveContainer, BarChart as RechartsBarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import type { PredictionResult } from '../types';
import { apiService } from '../services/api';

export const Prediction: React.FC = () => {
  const [predictions, setPredictions] = useState<PredictionResult[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchPredictions = async () => {
    setLoading(true);
    const data = await apiService.getPredictions();
    setPredictions(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchPredictions();
  }, []);

  return (
    <div className="p-6 space-y-6 max-h-[calc(100vh-4rem)] overflow-y-auto bg-slate-50">
      {/* Top Banner */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-lg bg-blue-50 text-blue-600">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base font-bold text-slate-900">
                30-Minute Traffic Volume Forecast
              </h2>
              <span className="text-[11px] px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 font-semibold border border-emerald-200">
                XGBoost Model Ready
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Short-term forecasting model trained on historical corridor density and time-of-day patterns
            </p>
          </div>
        </div>

        <button
          onClick={fetchPredictions}
          disabled={loading}
          className="px-4 py-2 bg-slate-100 hover:bg-slate-200 border border-slate-200 text-xs font-semibold rounded-lg text-slate-700 transition-all flex items-center space-x-2 self-start md:self-center"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Forecast</span>
        </button>
      </div>

      {/* Corridor Prediction Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {predictions.map((p) => {
          const delta = p.predicted_volume_30m - p.current_volume;
          const percent = ((delta / p.current_volume) * 100).toFixed(1);
          const isSurge = delta > 0;

          return (
            <div key={p.road_id} className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-blue-700">{p.road_id}</span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${
                  p.predicted_congestion === 'SEVERE' ? 'bg-red-100 text-red-800 border-red-200' :
                  p.predicted_congestion === 'HIGH' ? 'bg-amber-100 text-amber-800 border-amber-200' :
                  p.predicted_congestion === 'MODERATE' ? 'bg-yellow-100 text-yellow-800 border-yellow-200' : 'bg-emerald-100 text-emerald-800 border-emerald-200'
                }`}>
                  Predicted: {p.predicted_congestion}
                </span>
              </div>

              <div>
                <h3 className="text-sm font-bold text-slate-900">{p.road_name}</h3>
                <div className="text-[11px] text-slate-500 flex items-center gap-1 mt-0.5">
                  <Clock className="w-3 h-3" />
                  <span>Horizon: Next 30 Minutes</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-3 border-t border-slate-100">
                <div>
                  <div className="text-[11px] text-slate-500">Current Volume</div>
                  <div className="text-lg font-bold text-slate-800">{p.current_volume} <span className="text-xs font-normal text-slate-500">veh</span></div>
                </div>
                <div>
                  <div className="text-[11px] text-slate-500">Forecast Volume</div>
                  <div className="text-lg font-bold text-blue-700 flex items-center gap-1">
                    {p.predicted_volume_30m}
                    <span className={`text-xs font-semibold ${isSurge ? 'text-amber-600' : 'text-emerald-600'}`}>
                      ({isSurge ? `+${percent}%` : `${percent}%`})
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100">
                <span>Model Confidence</span>
                <span className="font-bold text-slate-800">{(p.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Feature Importance & Model Info */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Feature Importance (2 cols) */}
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="mb-4">
            <h3 className="text-sm font-bold text-slate-900">
              Model Feature Importance
            </h3>
            <p className="text-xs text-slate-500">Primary signals influencing the XGBoost prediction outcome</p>
          </div>
          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsBarChart data={[]} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
                <XAxis type="number" stroke="#64748b" fontSize={11} domain={[0, 0.5]} />
                <YAxis dataKey="feature" type="category" stroke="#64748b" fontSize={11} width={170} />
                <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', color: '#0f172a', fontSize: '12px', borderRadius: '8px' }} />
                <Bar dataKey="importance" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              </RechartsBarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Model Specs (1 col) */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-blue-600" />
            <h3 className="text-sm font-bold text-slate-900">Model Specifications</h3>
          </div>

          <div className="space-y-2.5 text-xs font-mono">
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <span className="text-slate-500 block text-[10px] uppercase font-semibold">Algorithm</span>
              <span className="text-slate-900 font-bold">XGBRegressor (max_depth=6, n_estimators=150)</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <span className="text-slate-500 block text-[10px] uppercase font-semibold">Training Flow</span>
              <span className="text-slate-900 font-bold">Offline Batch Pipeline (ml/train_xgboost.py)</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <span className="text-slate-500 block text-[10px] uppercase font-semibold">Inference Latency</span>
              <span className="text-emerald-700 font-bold">~1.8ms per query</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <span className="text-slate-500 block text-[10px] uppercase font-semibold">Validation Accuracy</span>
              <span className="text-blue-700 font-bold">R² Score: 0.938</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
