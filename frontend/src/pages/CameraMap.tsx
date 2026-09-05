import React, { useState } from 'react';
import { 
  Camera, 
  Layers,
  X,
  Radio,
  Clock,
  ArrowUpRight,
  Filter
} from 'lucide-react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle } from 'react-leaflet';
import L from 'leaflet';
import type { Camera as CameraType } from '../types';

const createCameraIcon = (status: CameraType['status'], isSelected = false) => {
  let color = '#2563eb';
  if (status === 'WARNING') color = '#d97706';
  if (status === 'OFFLINE') color = '#dc2626';

  const size = isSelected ? 16 : 12;
  const border = isSelected ? '3px solid #0f172a' : '2px solid #ffffff';

  return new L.DivIcon({
    className: 'camera-map-pin',
    html: `<div style="background-color: ${color}; width: ${size}px; height: ${size}px; border-radius: 50%; border: ${border}; box-shadow: 0 1px 4px rgba(0,0,0,0.3);"></div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2]
  });
};

interface CameraMapProps {
  cameras: CameraType[];
  flows?: any[];
}

export const CameraMap: React.FC<CameraMapProps> = ({ cameras }) => {
  const [selectedCamera, setSelectedCamera] = useState<CameraType | null>(cameras[0] || null);
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'ACTIVE' | 'WARNING' | 'OFFLINE'>('ALL');
  const [showRoads, setShowRoads] = useState<boolean>(true);

  const filteredCameras = cameras.filter(
    (c) => statusFilter === 'ALL' || c.status === statusFilter
  );

  return (
    <div className="h-[calc(100vh-3.5rem)] flex flex-col md:flex-row relative overflow-hidden bg-slate-100">
      {/* 1. DOMINANT GIS MAP WORKSPACE */}
      <div className="flex-1 h-full relative">
        <MapContainer
          center={[26.9050, 75.8050]}
          zoom={12}
          scrollWheelZoom={true}
          className="h-full w-full"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          />

          {/* Checkpoints */}
          {filteredCameras.map((cam) => {
            const isSelected = selectedCamera?.camera_id === cam.camera_id;
            return (
              <React.Fragment key={cam.camera_id}>
                <Marker
                  position={[cam.latitude, cam.longitude]}
                  icon={createCameraIcon(cam.status, isSelected)}
                  eventHandlers={{
                    click: () => setSelectedCamera(cam)
                  }}
                >
                  <Popup>
                    <div className="p-1 text-xs">
                      <div className="font-bold text-slate-900">{cam.camera_name}</div>
                      <div className="text-blue-700 font-mono mt-0.5">{cam.camera_id} • {cam.location}</div>
                      <div className="mt-1 text-slate-600">
                        Status: <span className="font-bold uppercase text-[11px]" style={{
                          color: cam.status === 'ACTIVE' ? '#15803d' : cam.status === 'WARNING' ? '#b45309' : '#b91c1c'
                        }}>{cam.status}</span>
                      </div>
                    </div>
                  </Popup>
                </Marker>
                {cam.status === 'ACTIVE' && (
                  <Circle
                    center={[cam.latitude, cam.longitude]}
                    radius={200}
                    pathOptions={{ color: '#2563eb', fillColor: '#2563eb', fillOpacity: 0.05, weight: 1 }}
                  />
                )}
              </React.Fragment>
            );
          })}
        </MapContainer>

        {/* Floating Map Controls */}
        <div className="absolute top-4 left-4 z-[1000] bg-white/95 backdrop-blur border border-slate-200 rounded-lg p-3 shadow-md space-y-2 text-xs">
          <div className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-1.5">
            <Layers className="w-3.5 h-3.5 text-blue-700" />
            <span>Grid Filters</span>
          </div>

          <div className="flex items-center space-x-2 pt-0.5">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as any)}
              className="bg-slate-50 border border-slate-200 rounded px-2 py-1 text-slate-700 text-xs focus:outline-none"
            >
              <option value="ALL">All Statuses ({cameras.length})</option>
              <option value="ACTIVE">Active (23)</option>
              <option value="WARNING">Warning (1)</option>
              <option value="OFFLINE">Offline (1)</option>
            </select>
          </div>

          <div className="pt-1 text-slate-600">
            <label className="flex items-center space-x-1.5 cursor-pointer">
              <input
                type="checkbox"
                checked={showRoads}
                onChange={(e) => setShowRoads(e.target.checked)}
                className="rounded border-slate-300 text-blue-600"
              />
              <span>Arterial Corridors</span>
            </label>
          </div>
        </div>

        {/* Legend */}
        <div className="absolute bottom-4 left-4 z-[1000] bg-white/95 backdrop-blur border border-slate-200 px-3 py-2 rounded text-[11px] font-mono text-slate-600 shadow-sm space-y-1">
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-600"></span>
            <span>Active Checkpoint</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-600"></span>
            <span>Optical Calibration Warning</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-red-600"></span>
            <span>Offline Node</span>
          </div>
        </div>
      </div>

      {/* 2. SMOOTH CAMERA INSPECTION SIDE DRAWER */}
      {selectedCamera && (
        <div className="w-full md:w-88 bg-white border-l border-slate-200 p-5 flex flex-col justify-between overflow-y-auto z-10 shrink-0 shadow-lg transition-all">
          <div className="space-y-4">
            {/* Header with Close */}
            <div className="flex items-start justify-between border-b border-slate-100 pb-3">
              <div>
                <div className="flex items-center space-x-2">
                  <Camera className="w-4 h-4 text-blue-700" />
                  <span className="font-mono text-xs font-bold text-blue-900">{selectedCamera.camera_id}</span>
                </div>
                <h3 className="text-sm font-bold text-slate-900 mt-1 leading-snug">{selectedCamera.camera_name}</h3>
                <p className="text-xs text-slate-500 mt-0.5">{selectedCamera.location}</p>
              </div>

              <span className={`text-[10px] font-bold px-2 py-0.5 rounded font-mono uppercase ${
                selectedCamera.status === 'ACTIVE' ? 'bg-emerald-100 text-emerald-800' :
                selectedCamera.status === 'WARNING' ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'
              }`}>
                {selectedCamera.status}
              </span>
            </div>

            {/* Checkpoint Coordinates & Specs */}
            <div className="bg-slate-50 p-3 rounded border border-slate-200 space-y-2 text-xs font-mono">
              <div className="flex justify-between">
                <span className="text-slate-500">Corridor</span>
                <span className="text-slate-900 font-semibold">{selectedCamera.road_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Heading</span>
                <span className="text-slate-900 font-semibold">{selectedCamera.direction}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Latitude</span>
                <span className="text-slate-900">{selectedCamera.latitude.toFixed(4)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Longitude</span>
                <span className="text-slate-900">{selectedCamera.longitude.toFixed(4)}</span>
              </div>
            </div>

            {/* Telemetry Numbers */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="bg-slate-50 p-3 rounded border border-slate-200">
                <div className="text-slate-500 text-[11px]">Today's Scans</div>
                <div className="text-lg font-bold text-slate-900 mt-0.5 font-mono">4,280</div>
              </div>
              <div className="bg-slate-50 p-3 rounded border border-slate-200">
                <div className="text-slate-500 text-[11px]">Mean Speed</div>
                <div className="text-lg font-bold text-blue-800 mt-0.5 font-mono">48 km/h</div>
              </div>
            </div>

            <div className="p-3 bg-blue-50/60 rounded border border-blue-200 text-xs text-blue-900 space-y-1">
              <div className="font-semibold flex items-center gap-1">
                <Radio className="w-3.5 h-3.5 text-blue-700" />
                Optical Telemetry Stream
              </div>
              <p className="text-[11px] text-blue-800 leading-snug">
                Checkpoint connected to municipal high-speed fiber backbone. Real-time OCR active.
              </p>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-200 text-[11px] text-slate-400 font-mono text-center">
            City Surveillance Checkpoint Node
          </div>
        </div>
      )}
    </div>
  );
};
