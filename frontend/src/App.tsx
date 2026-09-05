import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import type { PageId } from './components/layout/Sidebar';
import { Navbar } from './components/layout/Navbar';
import { Dashboard } from './pages/Dashboard';
import { LiveEvents } from './pages/LiveEvents';
import { VehicleSearch } from './pages/VehicleSearch';
import { TrafficAnalysis } from './pages/TrafficAnalysis';
import { Congestion } from './pages/Congestion';
import { Alerts } from './pages/Alerts';
import { CameraMap } from './pages/CameraMap';
import { Prediction } from './pages/Prediction';
import { Reports } from './pages/Reports';

import type { Camera, Alert, TrafficMetric, TrafficFlow, SystemStats, ANPREvent } from './types';
import { apiService } from './services/api';
import { MOCK_SYSTEM_STATS, SAMPLE_EVENTS } from './services/mockData';

export function App() {
  const [currentPage, setCurrentPage] = useState<PageId>('dashboard');
  const [maskPrivacy, setMaskPrivacy] = useState<boolean>(true);
  const [selectedPlate, setSelectedPlate] = useState<string>('RJ14AB1234');

  const [cameras, setCameras] = useState<Camera[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [metrics, setMetrics] = useState<TrafficMetric[]>([]);
  const [flows, setFlows] = useState<TrafficFlow[]>([]);
  const [stats, setStats] = useState<SystemStats>(MOCK_SYSTEM_STATS);
  const [events, setEvents] = useState<ANPREvent[]>(SAMPLE_EVENTS);

  // Initial data loading
  useEffect(() => {
    const initData = async () => {
      const [c, a, m, f, s, evts] = await Promise.all([
        apiService.getCameras(),
        apiService.getAlerts(),
        apiService.getTrafficMetrics(),
        apiService.getTrafficFlows(),
        apiService.getSystemStats(),
        apiService.getEvents()
      ]);
      setCameras(c);
      setAlerts(a);
      setMetrics(m);
      setFlows(f);
      setStats(s);
      if (evts && evts.length > 0) {
        setEvents(evts);
      }
    };
    initData();
  }, []);

  // Subscribe to real WebSocket if available
  useEffect(() => {
    const unsubscribe = apiService.subscribeLiveEvents((newEvent: ANPREvent) => {
      setEvents((prev) => [newEvent, ...prev.slice(0, 49)]);
      setStats((prev) => ({
        ...prev,
        total_vehicles_today: prev.total_vehicles_today + 1
      }));
    });

    return () => unsubscribe();
  }, []);

  const handleSelectPlateForTrajectory = (plate: string) => {
    setSelectedPlate(plate);
    setCurrentPage('trajectory');
  };

  return (
    <div className="flex h-screen w-screen bg-slate-50 text-slate-800 overflow-hidden font-sans">
      {/* Sidebar */}
      <Sidebar
        currentPage={currentPage}
        onSelectPage={setCurrentPage}
        activeAlertCount={alerts.filter((a) => a.status === 'OPEN').length}
      />

      {/* Main Viewport */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <Navbar
          currentPage={currentPage}
          maskPrivacy={maskPrivacy}
          onTogglePrivacy={() => setMaskPrivacy(!maskPrivacy)}
          activeAlertCount={alerts.filter((a) => a.status === 'OPEN').length}
        />

        <main className="flex-1 overflow-hidden bg-slate-50">
          {currentPage === 'dashboard' && (
            <Dashboard
              stats={stats}
              cameras={cameras}
              alerts={alerts}
              metrics={metrics}
              recentEvents={events}
              maskPrivacy={maskPrivacy}
              onNavigate={setCurrentPage}
              onSelectPlateForTrajectory={handleSelectPlateForTrajectory}
            />
          )}

          {currentPage === 'live' && (
            <LiveEvents
              events={events}
              maskPrivacy={maskPrivacy}
              onTrackPlate={handleSelectPlateForTrajectory}
            />
          )}

          {currentPage === 'trajectory' && (
            <VehicleSearch
              initialPlate={selectedPlate}
              maskPrivacy={maskPrivacy}
            />
          )}

          {currentPage === 'traffic' && (
            <TrafficAnalysis
              metrics={metrics}
              flows={flows}
            />
          )}

          {currentPage === 'congestion' && (
            <Congestion
              metrics={metrics}
            />
          )}

          {currentPage === 'alerts' && (
            <Alerts
              alerts={alerts}
              maskPrivacy={maskPrivacy}
              onInvestigatePlate={handleSelectPlateForTrajectory}
            />
          )}

          {currentPage === 'cameras' && (
            <CameraMap
              cameras={cameras}
              flows={flows}
            />
          )}

          {currentPage === 'prediction' && (
            <Prediction />
          )}

          {currentPage === 'reports' && (
            <Reports
              maskPrivacy={maskPrivacy}
              onTogglePrivacy={() => setMaskPrivacy(!maskPrivacy)}
            />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
