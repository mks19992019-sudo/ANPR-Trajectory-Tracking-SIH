import React, { useState } from 'react';
import { 
  Search, 
  Filter, 
  ArrowRight, 
  Car,
  ListOrdered
} from 'lucide-react';
import type { ANPREvent } from '../types';
import { formatPlate } from '../services/api';

interface LiveEventsProps {
  events: ANPREvent[];
  maskPrivacy: boolean;
  onTrackPlate: (plate: string) => void;
}

export const LiveEvents: React.FC<LiveEventsProps> = ({
  events,
  maskPrivacy,
  onTrackPlate
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [violationOnly, setViolationOnly] = useState<boolean>(false);

  const filteredEvents = events.filter((evt) => {
    const matchesSearch = 
      evt.plate_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      evt.camera_id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = selectedType === 'ALL' || evt.vehicle_type === selectedType;
    const matchesViolation = !violationOnly || evt.violation !== null;
    return matchesSearch && matchesType && matchesViolation;
  });

  return (
    <div className="p-5 space-y-4 max-h-[calc(100vh-3.5rem)] flex flex-col bg-slate-50">
      {/* Table Container Card */}
      <div className="bg-white border border-slate-200 rounded-lg shadow-sm flex flex-col flex-1 overflow-hidden">
        {/* Integrated Toolbar */}
        <div className="px-4 py-3 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-50/60">
          <div className="flex items-center space-x-2">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              ANPR Observation Records
            </h2>
            <span className="text-xs text-slate-400">•</span>
            <span className="text-xs text-slate-500 font-mono">{filteredEvents.length} Entries</span>
          </div>

          {/* Integrated Filter Controls */}
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Search */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
              <input
                type="text"
                placeholder="Search plate or camera..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-white border border-slate-200 rounded pl-8 pr-3 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-600 w-48 font-mono"
              />
            </div>

            {/* Type Filter */}
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="bg-white border border-slate-200 rounded px-2.5 py-1.5 text-xs text-slate-700 focus:outline-none focus:border-blue-600"
            >
              <option value="ALL">All Types</option>
              <option value="car">Cars</option>
              <option value="truck">Trucks</option>
              <option value="bus">Buses</option>
              <option value="motorcycle">Two-Wheelers</option>
              <option value="van">Vans</option>
            </select>

            {/* Violation Filter */}
            <button
              onClick={() => setViolationOnly(!violationOnly)}
              className={`px-2.5 py-1.5 rounded border text-xs font-medium transition-colors ${
                violationOnly
                  ? 'bg-red-50 border-red-300 text-red-700 font-semibold'
                  : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-100'
              }`}
            >
              {violationOnly ? 'Violations Only' : 'Filter Violations'}
            </button>
          </div>
        </div>

        {/* Compact Table */}
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-left border-collapse text-xs">
            <thead className="bg-slate-50 sticky top-0 z-10 text-slate-500 uppercase text-[10px] font-semibold tracking-wider border-b border-slate-200 font-mono">
              <tr>
                <th className="py-2.5 px-3.5">Timestamp</th>
                <th className="py-2.5 px-3.5">Plate Number</th>
                <th className="py-2.5 px-3.5">Camera ID</th>
                <th className="py-2.5 px-3.5">Type</th>
                <th className="py-2.5 px-3.5">Velocity</th>
                <th className="py-2.5 px-3.5">Heading</th>
                <th className="py-2.5 px-3.5">Violation</th>
                <th className="py-2.5 px-3.5">Confidence</th>
                <th className="py-2.5 px-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono">
              {filteredEvents.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-slate-400 text-xs">
                    No matching ANPR observations found.
                  </td>
                </tr>
              ) : (
                filteredEvents.map((evt) => {
                  const isSpeeding = evt.speed_kmph > 80;
                  return (
                    <tr key={evt.event_id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-2 px-3.5 text-slate-500 text-[11px]">
                        {evt.timestamp.replace('T', ' ')}
                      </td>
                      <td className="py-2 px-3.5 font-bold text-blue-900">
                        {formatPlate(evt.plate_number, maskPrivacy)}
                      </td>
                      <td className="py-2 px-3.5 text-slate-600 font-semibold">{evt.camera_id}</td>
                      <td className="py-2 px-3.5 capitalize font-sans text-slate-700 text-[11px]">
                        {evt.vehicle_type}
                      </td>
                      <td className="py-2 px-3.5">
                        <span className={`px-1.5 py-0.5 rounded text-[11px] font-semibold ${
                          isSpeeding ? 'bg-red-100 text-red-800' : 'text-slate-800'
                        }`}>
                          {evt.speed_kmph} km/h
                        </span>
                      </td>
                      <td className="py-2 px-3.5 text-slate-500">{evt.direction}</td>
                      <td className="py-2 px-3.5">
                        {evt.violation ? (
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-800 uppercase font-sans">
                            {evt.violation}
                          </span>
                        ) : (
                          <span className="text-slate-300">—</span>
                        )}
                      </td>
                      <td className="py-2 px-3.5 text-slate-600 text-[11px]">
                        {(evt.confidence * 100).toFixed(0)}%
                      </td>
                      <td className="py-2 px-3.5 text-right font-sans">
                        <button
                          onClick={() => onTrackPlate(evt.plate_number)}
                          className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-900 text-slate-700 hover:text-white border border-slate-200 hover:border-transparent text-[11px] font-medium transition-colors"
                        >
                          Track
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Footer */}
        <div className="px-4 py-2 border-t border-slate-200 bg-slate-50/50 text-[11px] text-slate-500 flex justify-between font-mono">
          <span>Buffer: {filteredEvents.length} observations indexed</span>
          <span>Optical Checkpoint Feed • Police Grid</span>
        </div>
      </div>
    </div>
  );
};
