"""
Geographically contiguous arterial corridors across Jaipur Metropolitan ANPR network.
All hops represent actual connected road transitions between adjacent cameras.
"""
from generator.cameras_data import CAMERAS, CAMERA_DICT
import math

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# Core physical corridors connecting adjacent checkpoint cameras
CORRIDORS_DEF = [
    {
        "route_id": "RT_JL_MARG_SB",
        "name": "JL Marg Southbound Corridor (MI Road -> Airport)",
        "camera_sequence": ["CAM_003", "CAM_005", "CAM_006", "CAM_007", "CAM_008"],
        "default_speeds": [42.0, 50.0, 52.0, 54.0, 50.0]
    },
    {
        "route_id": "RT_JL_MARG_NB",
        "name": "JL Marg Northbound Corridor (Airport -> MI Road)",
        "camera_sequence": ["CAM_008", "CAM_007", "CAM_006", "CAM_005", "CAM_003"],
        "default_speeds": [50.0, 52.0, 50.0, 45.0, 40.0]
    },
    {
        "route_id": "RT_TONK_ROAD_SB",
        "name": "Tonk Road National Highway Southbound (Panch Batti -> Sanganer)",
        "camera_sequence": ["CAM_003", "CAM_009", "CAM_010", "CAM_011"],
        "default_speeds": [45.0, 52.0, 55.0, 58.0]
    },
    {
        "route_id": "RT_TONK_ROAD_NB",
        "name": "Tonk Road National Highway Northbound (Sanganer -> Panch Batti)",
        "camera_sequence": ["CAM_011", "CAM_010", "CAM_009", "CAM_003"],
        "default_speeds": [55.0, 52.0, 48.0, 40.0]
    },
    {
        "route_id": "RT_MANSAROVAR_AIRPORT",
        "name": "Vaishali to Airport via B2 Bypass Ring",
        "camera_sequence": ["CAM_016", "CAM_017", "CAM_018", "CAM_019", "CAM_007", "CAM_008"],
        "default_speeds": [38.0, 40.0, 68.0, 72.0, 52.0, 50.0]
    },
    {
        "route_id": "RT_AIRPORT_MANSAROVAR",
        "name": "Airport to Vaishali via B2 Bypass Ring",
        "camera_sequence": ["CAM_008", "CAM_007", "CAM_019", "CAM_018", "CAM_017", "CAM_016"],
        "default_speeds": [50.0, 52.0, 70.0, 65.0, 38.0, 35.0]
    },
    {
        "route_id": "RT_WALLED_CITY_CENTRAL",
        "name": "Heritage Corridor (Amer Fort -> Hawa Mahal -> MI Road)",
        "camera_sequence": ["CAM_025", "CAM_024", "CAM_020", "CAM_021", "CAM_004", "CAM_003"],
        "default_speeds": [42.0, 35.0, 25.0, 22.0, 35.0, 38.0]
    },
    {
        "route_id": "RT_CENTRAL_WALLED_CITY",
        "name": "Heritage Corridor (MI Road -> Johari Bazaar -> Amer Fort)",
        "camera_sequence": ["CAM_003", "CAM_004", "CAM_021", "CAM_020", "CAM_024", "CAM_025"],
        "default_speeds": [35.0, 30.0, 22.0, 26.0, 38.0, 42.0]
    },
    {
        "route_id": "RT_DELHI_HIGHWAY_AGRA",
        "name": "Delhi Highway to Agra Road Bypass",
        "camera_sequence": ["CAM_025", "CAM_024", "CAM_012", "CAM_013", "CAM_022"],
        "default_speeds": [45.0, 48.0, 78.0, 82.0, 45.0]
    },
    {
        "route_id": "RT_SIKAR_TO_CENTRAL",
        "name": "Sikar Road to City Center (VKI -> Elevated Road -> MI Road)",
        "camera_sequence": ["CAM_015", "CAM_014", "CAM_023", "CAM_003", "CAM_009"],
        "default_speeds": [46.0, 45.0, 55.0, 40.0, 48.0]
    },
    {
        "route_id": "RT_AJMER_EXPRESSWAY_WB",
        "name": "Ajmer Expressway Westbound (Central -> 200ft Bypass)",
        "camera_sequence": ["CAM_003", "CAM_001", "CAM_002"],
        "default_speeds": [42.0, 72.0, 78.0]
    },
    {
        "route_id": "RT_AJMER_EXPRESSWAY_EB",
        "name": "Ajmer Expressway Eastbound (200ft Bypass -> Central)",
        "camera_sequence": ["CAM_002", "CAM_001", "CAM_003"],
        "default_speeds": [76.0, 70.0, 40.0]
    }
]

# Build detailed hops with precomputed physical distance and driving time
ROUTES = []
for c_def in CORRIDORS_DEF:
    seq = c_def["camera_sequence"]
    speeds = c_def["default_speeds"]
    hops = []
    total_km = 0.0

    for i, cam_id in enumerate(seq):
        cam = CAMERA_DICT[cam_id]
        if i == 0:
            dist_from_prev = 0.0
            time_sec_from_prev = 0
        else:
            prev_cam = CAMERA_DICT[seq[i - 1]]
            dist_from_prev = haversine_km(prev_cam["lat"], prev_cam["lng"], cam["lat"], cam["lng"])
            speed = speeds[i]
            time_sec_from_prev = int((dist_from_prev / speed) * 3600)
            total_km += dist_from_prev

        hops.append({
            "camera_id": cam_id,
            "camera_name": cam["name"],
            "direction": cam["direction"],
            "speed_kmph": speeds[i],
            "speed_limit": cam["limit"],
            "distance_from_prev_km": round(dist_from_prev, 2),
            "transit_seconds": time_sec_from_prev
        })

    ROUTES.append({
        "route_id": c_def["route_id"],
        "name": c_def["name"],
        "total_distance_km": round(total_km, 2),
        "hops": hops
    })

ROUTE_DICT = {r["route_id"]: r for r in ROUTES}
