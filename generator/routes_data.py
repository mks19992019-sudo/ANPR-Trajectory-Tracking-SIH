ROUTES = [
    # Route 1: JL Marg Arterial to Airport (4 hops)
    {
        "route_id": "RT_JL_AIRPORT",
        "name": "JL Marg Southbound to Airport",
        "hops": [
            {"camera_id": "CAM_005", "delay_min": 0, "avg_speed": 48.0},
            {"camera_id": "CAM_006", "delay_min": 7, "avg_speed": 52.0},
            {"camera_id": "CAM_007", "delay_min": 14, "avg_speed": 55.0},
            {"camera_id": "CAM_008", "delay_min": 12, "avg_speed": 54.0},
        ]
    },
    # Route 2: Tonk Road Southbound (3 hops)
    {
        "route_id": "RT_TONK_HIGHWAY",
        "name": "Tonk Road National Highway Corridor",
        "hops": [
            {"camera_id": "CAM_009", "delay_min": 0, "avg_speed": 50.0},
            {"camera_id": "CAM_010", "delay_min": 9, "avg_speed": 45.0},
            {"camera_id": "CAM_011", "delay_min": 15, "avg_speed": 58.0},
        ]
    },
    # Route 3: Ajmer Expressway (2 hops)
    {
        "route_id": "RT_AJMER_EXPRESSWAY",
        "name": "Ajmer Road Expressway Westbound",
        "hops": [
            {"camera_id": "CAM_001", "delay_min": 0, "avg_speed": 72.0},
            {"camera_id": "CAM_002", "delay_min": 6, "avg_speed": 76.0},
        ]
    },
    # Route 4: Walled City Heritage Spine (3 hops)
    {
        "route_id": "RT_WALLED_CITY",
        "name": "Heritage Walled City Spine",
        "hops": [
            {"camera_id": "CAM_021", "delay_min": 0, "avg_speed": 22.0},
            {"camera_id": "CAM_020", "delay_min": 6, "avg_speed": 18.0},
            {"camera_id": "CAM_022", "delay_min": 8, "avg_speed": 26.0},
        ]
    },
    # Route 5: Delhi Highway Toll Corridor (2 hops)
    {
        "route_id": "RT_DELHI_HIGHWAY",
        "name": "Jaipur-Delhi Highway Corridor",
        "hops": [
            {"camera_id": "CAM_012", "delay_min": 0, "avg_speed": 82.0},
            {"camera_id": "CAM_013", "delay_min": 8, "avg_speed": 85.0},
        ]
    },
    # Route 6: Sikar Road Belt (2 hops)
    {
        "route_id": "RT_SIKAR_BELT",
        "name": "Sikar Road Industrial Belt",
        "hops": [
            {"camera_id": "CAM_014", "delay_min": 0, "avg_speed": 44.0},
            {"camera_id": "CAM_015", "delay_min": 9, "avg_speed": 48.0},
        ]
    },
    # Route 7: B2 Bypass Ring (3 hops)
    {
        "route_id": "RT_B2_BYPASS",
        "name": "B2 Bypass Ring Road",
        "hops": [
            {"camera_id": "CAM_018", "delay_min": 0, "avg_speed": 68.0},
            {"camera_id": "CAM_019", "delay_min": 7, "avg_speed": 72.0},
            {"camera_id": "CAM_007", "delay_min": 8, "avg_speed": 55.0},
        ]
    }
]
