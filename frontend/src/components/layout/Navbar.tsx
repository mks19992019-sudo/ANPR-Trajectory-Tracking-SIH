import React, { useState, useEffect } from 'react';
import { Eye, EyeOff, Bell, ShieldCheck, User } from 'lucide-react';
import type { PageId } from './Sidebar';

interface NavbarProps {
  currentPage: PageId;
  maskPrivacy: boolean;
  onTogglePrivacy: () => void;
  activeAlertCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentPage,
  maskPrivacy,
  onTogglePrivacy,
  activeAlertCount
}) => {
  const [time, setTime] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTime(now.toLocaleTimeString('en-IN', { hour12: false }));
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  const pageNames: Record<PageId, string> = {
    dashboard: 'Surveillance & Traffic Overview',
    live: 'ANPR Observation Log',
    trajectory: 'Vehicle Trajectory Investigation',
    traffic: 'Traffic Density & Corridor Flow',
    congestion: 'Bottleneck & Congestion Index',
    alerts: 'Incident & Alert Management',
    cameras: 'Surveillance Camera Grid GIS',
    prediction: 'Short-Term Volume Forecast (XGBoost)',
    reports: 'Privacy Compliance & Audit Registry',
  };

  return (
    <header className="h-14 bg-white border-b border-slate-200 px-5 flex items-center justify-between z-20 select-none shrink-0">
      {/* Left: Current View & Operational Status */}
      <div className="flex items-center space-x-3">
        <h1 className="text-sm font-semibold text-slate-900 tracking-tight">
          {pageNames[currentPage] || 'Traffic Platform'}
        </h1>
        <span className="text-slate-300 font-normal">|</span>
        <div className="flex items-center space-x-1.5 text-xs text-slate-500 font-mono">
          <span className="w-2 h-2 rounded-full bg-emerald-600 inline-block"></span>
          <span>SYSTEM OPERATIONAL</span>
        </div>
      </div>

      {/* Center: service label */}
      <div className="hidden md:flex items-center">
        <span className="text-[11px] font-mono tracking-wider px-2 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-500 uppercase">
          LIVE API DATA
        </span>
      </div>

      {/* Right: Operational Controls */}
      <div className="flex items-center space-x-3">
        {/* Privacy Masking Toggle */}
        <button
          onClick={onTogglePrivacy}
          className={`flex items-center space-x-1.5 px-2.5 py-1 rounded text-xs font-medium border transition-colors ${
            maskPrivacy
              ? 'bg-amber-50/70 border-amber-300 text-amber-900'
              : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
          }`}
          title="Toggle Privacy Masking for Plate Numbers"
        >
          {maskPrivacy ? <EyeOff className="w-3.5 h-3.5 text-amber-700" /> : <Eye className="w-3.5 h-3.5 text-slate-600" />}
          <span>{maskPrivacy ? 'Plate Masking: ON' : 'Plate Masking: OFF'}</span>
        </button>

        {/* Alerts Pill */}
        <div className="relative">
          <div className="p-1.5 rounded border border-slate-200 bg-slate-50 text-slate-600">
            <Bell className="w-4 h-4" />
          </div>
          {activeAlertCount > 0 && (
            <span className="absolute -top-1.5 -right-1.5 flex h-4 min-w-4 px-1 items-center justify-center rounded-full bg-red-600 text-[10px] font-mono font-bold text-white shadow-sm">
              {activeAlertCount}
            </span>
          )}
        </div>

        {/* Operator Badge & Clock */}
        <div className="hidden sm:flex items-center space-x-3 border-l border-slate-200 pl-3 text-xs">
          <div className="text-right">
            <div className="font-mono font-semibold text-slate-800 text-[12px]">{time} IST</div>
            <div className="text-[10px] text-slate-600 uppercase">Jaipur Sector Control</div>
          </div>
        </div>
      </div>
    </header>
  );
};
