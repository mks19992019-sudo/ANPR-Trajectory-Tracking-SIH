# ANPR Pipeline Restructure — Task List

## Backend Core
- [x] config.py — remove SQLite default, add journey gap config
- [x] database.py — PostgreSQL only, remove SQLite branch
- [x] seed.py — remove ANPR event/alert seeding, keep only roads/cameras/blacklist
- [x] main.py — fix health check, add correlation ID middleware
- [x] alembic migration — replace with complete schema migration

## Generator
- [x] generate_data.py — rewrite as HTTP-only client (no DB imports)

## Infrastructure
- [x] Dockerfile — remove SQLite ENV
- [x] docker-compose.yml — add missing env vars
- [x] .env — create with PostgreSQL credentials
- [x] traffic_anpr.db — delete SQLite file

## Frontend
- [x] mockData.ts — delete
- [x] api.ts — remove all mock imports/fallbacks
- [x] App.tsx — remove mock state initializers
- [x] types/index.ts — align types with real API
- [x] Dashboard.tsx — remove MOCK_ROADS, show real data
- [x] LiveEvents.tsx — remove SAMPLE_EVENTS fallback
- [x] Alerts.tsx — remove MOCK_ALERTS fallback
- [x] TrafficAnalysis.tsx — remove mock fallback
- [x] Congestion.tsx — remove mock fallback
- [x] VehicleSearch.tsx — remove mock trajectory fallback
- [x] Prediction.tsx — show model not available
- [x] CameraMap.tsx — remove mock cameras fallback
- [x] Reports.tsx — remove mock data

## Tests
- [x] conftest.py — fix seed_database call (no ANPR events)
- [x] test_trajectory.py — seed events via API, not direct DB
- [x] test_analytics.py — seed events via API, not direct DB
