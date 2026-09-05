import React from 'react';
import { 
  Lock, 
  Clock, 
  Download, 
  EyeOff, 
  UserCheck 
} from 'lucide-react';
import { formatPlate } from '../services/api';

interface ReportsProps {
  maskPrivacy: boolean;
  onTogglePrivacy: () => void;
}

export const Reports: React.FC<ReportsProps> = ({ maskPrivacy, onTogglePrivacy }) => {
  const auditLogs = [
    { id: 'AUD_901', officer: 'SI Rajesh Sharma (ID: POL-4402)', action: 'TRAJECTORY_QUERY', target: 'RJ14AB1234', reason: 'Corridor surveillance verification', timestamp: '2026-09-05 09:32:14' },
    { id: 'AUD_902', officer: 'Insp. Vikram Singh (ID: POL-1092)', action: 'BLACKLIST_CHECK', target: 'DL01CZ9999', reason: 'FIR #882 Stolen vehicle investigation', timestamp: '2026-09-05 09:28:40' },
    { id: 'AUD_903', officer: 'System Engine', action: 'ANOMALY_LOG', target: 'HR26XY4040', reason: 'High velocity hop flagged (592 km/h)', timestamp: '2026-09-05 09:25:01' },
    { id: 'AUD_904', officer: 'Analyst Meena (ID: POL-7731)', action: 'OD_EXPORT', target: 'City-Wide Grid', reason: 'Traffic signal timing optimization', timestamp: '2026-09-05 09:15:22' },
  ];

  return (
    <div className="p-6 space-y-6 max-h-[calc(100vh-4rem)] overflow-y-auto bg-slate-50">
      {/* Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Plate Anonymization</span>
            <div className="p-2 rounded-lg bg-blue-50 text-blue-600">
              <EyeOff className="w-5 h-5" />
            </div>
          </div>
          <div className="text-base font-bold text-slate-900 font-mono">
            {maskPrivacy ? 'Active (RJ14••••34)' : 'Disabled (Full Plate)'}
          </div>
          <p className="text-xs text-slate-500">
            Masks middle characters to comply with privacy frameworks in public traffic views.
          </p>
          <button
            onClick={onTogglePrivacy}
            className="mt-2 text-xs font-semibold text-blue-600 hover:text-blue-700 transition-colors"
          >
            Toggle Masking State
          </button>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Data Retention Policy</span>
            <div className="p-2 rounded-lg bg-indigo-50 text-indigo-600">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="text-base font-bold text-slate-900">90-Day Auto Purge</div>
          <p className="text-xs text-slate-500">
            Raw vehicle camera observations automatically purge after 90 days. Aggregated statistics remain preserved.
          </p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Storage Boundary</span>
            <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600">
              <Lock className="w-5 h-5" />
            </div>
          </div>
          <div className="text-base font-bold text-slate-900">Metadata Only</div>
          <p className="text-xs text-slate-500">
            Zero raw camera pixel frames stored. Only structured OCR events, timestamps, and GPS coordinates are indexed.
          </p>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <UserCheck className="w-4 h-4 text-blue-600" />
              Surveillance Inquiry Audit Trail
            </h3>
            <p className="text-xs text-slate-500">
              Audit record of user queries, trajectory reconstructions, and official lookups
            </p>
          </div>
          <button
            onClick={() => alert('Audit log exported.')}
            className="px-3.5 py-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 border border-slate-200 text-xs font-medium text-slate-700 flex items-center space-x-1.5 transition-colors self-start md:self-center shadow-sm"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-slate-50 text-slate-600 uppercase text-[10px] border-b border-slate-200">
              <tr>
                <th className="p-3">Log ID</th>
                <th className="p-3">User / Officer</th>
                <th className="p-3">Action</th>
                <th className="p-3">Target</th>
                <th className="p-3">Reason / Case</th>
                <th className="p-3">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono">
              {auditLogs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-50 transition-colors">
                  <td className="p-3 text-slate-500">{log.id}</td>
                  <td className="p-3 font-sans font-medium text-slate-800">{log.officer}</td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-700 text-[10px] font-bold border border-blue-200">
                      {log.action}
                    </span>
                  </td>
                  <td className="p-3 font-bold text-slate-900">
                    {formatPlate(log.target, maskPrivacy)}
                  </td>
                  <td className="p-3 font-sans text-slate-600">{log.reason}</td>
                  <td className="p-3 text-slate-500">{log.timestamp}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
