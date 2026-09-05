import React, { useState } from 'react';
import { 
  ShieldAlert, 
  CheckCircle2, 
  ArrowRight, 
  AlertCircle,
  Filter,
  Check
} from 'lucide-react';
import type { Alert, AlertSeverity } from '../types';
import { formatPlate } from '../services/api';

interface AlertsProps {
  alerts: Alert[];
  maskPrivacy: boolean;
  onInvestigatePlate: (plate: string) => void;
}

export const Alerts: React.FC<AlertsProps> = ({ alerts, maskPrivacy, onInvestigatePlate }) => {
  const [filterSeverity, setFilterSeverity] = useState<string>('ALL');
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [alertList, setAlertList] = useState<Alert[]>(alerts);

  const filtered = alertList.filter((a) => {
    const matchesSeverity = filterSeverity === 'ALL' || a.severity === filterSeverity;
    const matchesStatus = filterStatus === 'ALL' || a.status === filterStatus;
    return matchesSeverity && matchesStatus;
  });

  const handleStatusChange = (alertId: string, newStatus: Alert['status']) => {
    setAlertList(prev => prev.map(a => a.alert_id === alertId ? { ...a, status: newStatus } : a));
  };

  const criticalCount = alertList.filter(a => a.severity === 'CRITICAL' && a.status !== 'RESOLVED').length;
  const warningCount = alertList.filter(a => a.severity === 'WARNING' && a.status !== 'RESOLVED').length;

  return (
    <div className="p-5 space-y-5 max-h-[calc(100vh-3.5rem)] overflow-y-auto bg-slate-50">
      {/* Incident Summary & Status Ribbon */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-600" />
            Operational Incident Queue
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Active triggers from criminal blacklists, cloned plate teleportation & speed sensors
          </p>
        </div>

        {/* Severity Counts */}
        <div className="flex items-center space-x-3 text-xs font-mono">
          <div className="px-3 py-1.5 rounded bg-red-50 border border-red-200 text-red-800 flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-red-600"></span>
            <span>CRITICAL: <strong>{criticalCount}</strong></span>
          </div>
          <div className="px-3 py-1.5 rounded bg-amber-50 border border-amber-200 text-amber-800 flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-amber-600"></span>
            <span>WARNING: <strong>{warningCount}</strong></span>
          </div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-3 rounded-lg border border-slate-200 shadow-sm text-xs">
        <div className="flex items-center space-x-2">
          <span className="text-slate-400 uppercase text-[10px] font-semibold tracking-wider">Severity:</span>
          <button
            onClick={() => setFilterSeverity('ALL')}
            className={`px-2.5 py-1 rounded transition-colors ${filterSeverity === 'ALL' ? 'bg-slate-900 text-white font-medium' : 'text-slate-600 hover:bg-slate-100'}`}
          >
            All Severities
          </button>
          <button
            onClick={() => setFilterSeverity('CRITICAL')}
            className={`px-2.5 py-1 rounded transition-colors ${filterSeverity === 'CRITICAL' ? 'bg-red-700 text-white font-medium' : 'text-slate-600 hover:bg-slate-100'}`}
          >
            Critical Only ({criticalCount})
          </button>
          <button
            onClick={() => setFilterSeverity('WARNING')}
            className={`px-2.5 py-1 rounded transition-colors ${filterSeverity === 'WARNING' ? 'bg-amber-700 text-white font-medium' : 'text-slate-600 hover:bg-slate-100'}`}
          >
            Warnings ({warningCount})
          </button>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-slate-400 uppercase text-[10px] font-semibold tracking-wider">Status:</span>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded px-2.5 py-1 text-xs text-slate-700 focus:outline-none focus:border-blue-600"
          >
            <option value="ALL">All Statuses</option>
            <option value="OPEN">Open Incidents</option>
            <option value="INVESTIGATING">Investigating</option>
            <option value="RESOLVED">Resolved</option>
          </select>
        </div>
      </div>

      {/* Incident Cards Queue */}
      <div className="space-y-3">
        {filtered.map((alt) => {
          const isCritical = alt.severity === 'CRITICAL';
          const isResolved = alt.status === 'RESOLVED';
          const isInvestigating = alt.status === 'INVESTIGATING';

          return (
            <div
              key={alt.alert_id}
              className={`bg-white rounded-lg border shadow-sm transition-colors ${
                isCritical
                  ? 'border-l-4 border-l-red-600 border-slate-200'
                  : 'border-l-4 border-l-amber-500 border-slate-200'
              }`}
            >
              <div className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center space-x-2.5">
                    <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded uppercase ${
                      isCritical ? 'bg-red-100 text-red-800' : 'bg-amber-100 text-amber-800'
                    }`}>
                      {alt.severity}
                    </span>
                    <span className="text-xs font-bold text-slate-900 uppercase font-mono tracking-tight">
                      {alt.alert_type.replace(/_/g, ' ')}
                    </span>
                    <span className="text-xs text-slate-400">•</span>
                    <span className="text-xs text-slate-500 font-mono">
                      {(alt.timestamp || '').replace('T', ' ').slice(0, 19)}
                    </span>
                    <span className="text-xs text-slate-400">•</span>
                    <span className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded uppercase ${
                      isResolved ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                      isInvestigating ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'bg-slate-100 text-slate-700'
                    }`}>
                      {alt.status}
                    </span>
                  </div>

                  <div className="flex items-baseline space-x-3 pt-0.5">
                    <span className="font-mono text-sm font-bold text-slate-900">
                      {formatPlate(alt.plate_number, maskPrivacy)}
                    </span>
                    <span className="text-xs text-slate-500 font-mono">
                      Checkpoint: {alt.camera_name || alt.camera_id}
                    </span>
                  </div>

                  <p className="text-xs text-slate-700 leading-relaxed max-w-3xl">
                    {alt.message || alt.description || 'Incident flagged by detection rules'}
                  </p>
                </div>

                {/* Instant Actions */}
                <div className="flex items-center space-x-2 shrink-0 self-start md:self-center">
                  {alt.plate_number !== 'CORRIDOR_ALERT' && (
                    <button
                      onClick={() => onInvestigatePlate(alt.plate_number)}
                      className="px-3 py-1.5 rounded bg-blue-700 hover:bg-blue-800 text-white text-xs font-medium flex items-center space-x-1.5 transition-colors shadow-sm"
                    >
                      <span>Track Route</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  )}

                  {!isResolved && (
                    <>
                      {alt.status === 'OPEN' && (
                        <button
                          onClick={() => handleStatusChange(alt.alert_id, 'INVESTIGATING')}
                          className="px-3 py-1.5 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium transition-colors border border-slate-200"
                        >
                          Acknowledge
                        </button>
                      )}
                      <button
                        onClick={() => handleStatusChange(alt.alert_id, 'RESOLVED')}
                        className="px-3 py-1.5 rounded bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-xs font-medium transition-colors border border-emerald-200 flex items-center space-x-1"
                      >
                        <Check className="w-3 h-3" />
                        <span>Resolve</span>
                      </button>
                    </>
                  )}

                  {isResolved && (
                    <span className="text-xs text-emerald-700 font-medium flex items-center space-x-1 px-2.5 py-1">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      <span>Case Closed</span>
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
