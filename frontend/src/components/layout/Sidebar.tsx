import React from 'react';
import { 
  Shield, 
  Activity, 
  Search, 
  BarChart2, 
  AlertCircle, 
  Camera, 
  TrendingUp, 
  FileText, 
  LayoutDashboard, 
  ListOrdered
} from 'lucide-react';

export type PageId = 
  | 'dashboard'
  | 'live'
  | 'trajectory'
  | 'traffic'
  | 'congestion'
  | 'alerts'
  | 'cameras'
  | 'prediction'
  | 'reports';

interface SidebarProps {
  currentPage: PageId;
  onSelectPage: (page: PageId) => void;
  activeAlertCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPage, onSelectPage, activeAlertCount }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'live', label: 'ANPR Events', icon: ListOrdered },
    { id: 'trajectory', label: 'Vehicle Trajectory', icon: Search },
    { id: 'traffic', label: 'Traffic Analytics', icon: BarChart2 },
    { id: 'congestion', label: 'Congestion Zones', icon: Activity },
    { id: 'alerts', label: 'Incidents & Alerts', icon: AlertCircle, count: activeAlertCount },
    { id: 'cameras', label: 'Camera Map', icon: Camera },
    { id: 'prediction', label: 'Volume Forecast', icon: TrendingUp },
    { id: 'reports', label: 'Privacy & Audit', icon: FileText },
  ];

  return (
    <aside className="w-60 bg-white border-r border-slate-200 flex flex-col h-screen select-none shrink-0">
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-200 flex items-center space-x-3 bg-slate-50/50">
        <div className="w-8 h-8 rounded bg-slate-900 text-white flex items-center justify-center font-bold text-xs shrink-0">
          <Shield className="w-4 h-4 text-blue-400" />
        </div>
        <div className="min-w-0">
          <div className="text-xs font-bold tracking-tight text-slate-900 truncate">ANPR COMMAND</div>
          <div className="text-[10px] text-slate-500 truncate">Jaipur City Police Grid</div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2.5 py-3 space-y-0.5 overflow-y-auto">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 px-2.5 py-1.5">
          SURVEILLANCE MODULES
        </div>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectPage(item.id as PageId)}
              className={`w-full flex items-center justify-between px-2.5 py-2 rounded text-xs transition-colors ${
                isActive
                  ? 'bg-slate-900 text-white font-medium shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              <div className="flex items-center space-x-2.5">
                <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.count && item.count > 0 ? (
                <span className={`text-[10px] font-mono font-bold px-1.5 py-0.2 rounded ${
                  isActive ? 'bg-red-600 text-white' : 'bg-red-100 text-red-700'
                }`}>
                  {item.count}
                </span>
              ) : null}
            </button>
          );
        })}
      </nav>

      {/* Operational Telemetry Summary */}
      <div className="p-3 border-t border-slate-200 bg-slate-50/60 text-[11px] text-slate-500 space-y-1.5 font-mono">
        <div className="flex items-center justify-between">
          <span>CHECKPOINTS</span>
          <span className="text-slate-900 font-semibold font-mono">23 / 25 ONLINE</span>
        </div>
        <div className="flex items-center justify-between">
          <span>OCR ACCURACY</span>
          <span className="text-emerald-700 font-semibold font-mono">98.2%</span>
        </div>
        <div className="flex items-center justify-between">
          <span>LATENCY</span>
          <span className="text-slate-900 font-semibold font-mono">14ms</span>
        </div>
      </div>
    </aside>
  );
};
