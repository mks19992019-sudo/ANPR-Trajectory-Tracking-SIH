import type { Alert, ANPREvent, Camera, PredictionResult, SystemStats, TrafficFlow, TrafficMetric, Trajectory, VehicleObservation } from '../types';
const base=import.meta.env.VITE_API_BASE_URL ?? '/api/v1';
async function get<T>(path:string):Promise<T> { const r=await fetch(base+path); if(!r.ok) throw new Error(`Request failed (${r.status})`); return r.json(); }
export const formatPlate=(plate:string,mask=false)=>mask&&plate.length>6?`${plate.slice(0,4)}••••${plate.slice(-2)}`:plate;
class ApiService {
  async getCameras(){return get<Camera[]>('/cameras')}
  async getSystemStats(){return get<SystemStats>('/traffic/summary')}
  async getAlerts(){return get<Alert[]>('/alerts')}
  async updateAlertStatus(id:string,status:string){const r=await fetch(`${base}/alerts/${id}/status`,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({status})});if(!r.ok)throw new Error(`Request failed (${r.status})`);return true}
  async getTrafficMetrics(){return get<TrafficMetric[]>('/traffic/congestion')}
  async getTrafficFlows(){return get<TrafficFlow[]>('/traffic/flow')}
  async getEvents(){return (await get<{items:ANPREvent[]}>('/events?limit=50')).items}
  async getTrajectory(plate:string){return get<Trajectory>(`/vehicles/${encodeURIComponent(plate)}/trajectory`)}
  async getVehicleHistory(plate:string){return get<VehicleObservation[]>(`/vehicles/${encodeURIComponent(plate)}/history`)}
  async getPredictions(){return get<PredictionResult[]>('/ml/prediction')}
  subscribeLiveEvents(callback:(e:ANPREvent)=>void){const ws=new WebSocket((location.protocol==='https:'?'wss':'ws')+`://${location.host}/ws/traffic`);ws.onmessage=e=>{const data=JSON.parse(e.data);if(data.type==='ANPR_EVENT')callback(data.payload)};return()=>ws.close()}
}
export const apiService=new ApiService();
