# Ariva

Ariva is Sri Lanka Living Intelligence: one public-first signal desk for daily costs, places, mobility, and market context, powered by the existing Ardeno Studio price-intelligence domains:
FoodLK, Octane, PropertyLK, and AutoLens.

## Shape

- `backend/` - FastAPI API, domain adapters, central snapshot schema, affordability engine.
- `frontend/` - Vite React dashboard for the public Ariva UI.
- `.github/workflows/` - CI and snapshot refresh automation.

## Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
alembic upgrade head
uvicorn app.main:app --reload --port 8090
```

Useful local settings:

```env
DATABASE_URL=sqlite:///./life_platform.db
LIFE_USE_FIXTURES=false
LIFE_CACHE_SECONDS=180
FOOD_API_BASE=https://food-platform-backend.fly.dev/api/v1
FUEL_API_BASE=https://octane-api.fly.dev
PROPERTY_API_BASE=https://property-price-intelligence-an-ardeno-production.fly.dev
VEHICLE_API_BASE=https://vehicle-platform-backend.fly.dev/api/v1
```

Optional hybrid-account settings:

```env
FIREBASE_PROJECT_ID=your-firebase-project
FIREBASE_CREDENTIALS_JSON={"type":"service_account",...}
# or FIREBASE_CREDENTIALS_PATH=C:\secure\firebase-service-account.json
LIFE_INTERNAL_TOKEN=replace-with-a-long-random-token
```

The public dashboard does not require auth. Firebase Auth only enables saved profile preferences, saved watch items, alert rules, and the in-app notification inbox.

## Frontend

```powershell
cd frontend
npm install
npm run lint
npm run test
npm run build
npm run dev
```

Default local frontend API base is `http://127.0.0.1:8090/api/v1`.
When backend and frontend are both running, `npm run test:e2e` runs the desktop/mobile Playwright smoke suite.

Set the `VITE_FIREBASE_*` values from the Firebase web app config to show the optional sign-in control. If they are absent, the UI remains public-only and hides account controls.

Operators can open `/?page=operator` to review promoted source-data releases. This page is unlisted in the public nav and asks for `LIFE_INTERNAL_TOKEN` at runtime; the token is not compiled into the frontend or stored by the app.

## Deployment

- Backend: Fly app from `backend/fly.toml`; run Alembic migrations before the Uvicorn server starts.
- Frontend: Vercel Vite build from `frontend/vercel.json`; set `VITE_API_URL` to the deployed backend `/api/v1` base.
- CI: `.github/workflows/ci.yml` runs backend tests, frontend lint, frontend tests, and frontend build.
- Snapshot refresh: `.github/workflows/snapshot-refresh.yml` can call the deployed Ariva API when `LIFE_API_BASE` is configured as a repository secret.

## Public API

- `GET /api/v1/life/overview`
- `GET /api/v1/life/domains`
- `GET /api/v1/life/search?q=rice`
- `GET /api/v1/life/affordability?district=Colombo&profile=family`
- `GET /api/v1/life/trends?domain=food`
- `GET /api/v1/life/weather-risk?district=Ratnapura`
- `GET /api/v1/life/pipeline`
- `GET /api/v1/life/source-validation`
- `GET /api/v1/life/source-release`
- `GET /api/v1/me/life-pulse` with a Firebase ID token
- `GET/PUT /api/v1/me/profile` with a Firebase ID token
- `GET/POST/DELETE /api/v1/me/saved-items` with a Firebase ID token
- `GET/POST/PATCH/DELETE /api/v1/me/alerts` with a Firebase ID token
- `GET/PATCH /api/v1/me/notifications` with a Firebase ID token
- `POST /api/v1/internal/source-refresh` with `LIFE_INTERNAL_TOKEN`
- `POST /api/v1/internal/source-import-audit` with `LIFE_INTERNAL_TOKEN`
- `POST /api/v1/internal/source-import-plan` with `LIFE_INTERNAL_TOKEN`
- `POST /api/v1/internal/source-import-run?live_fetch=true` with `LIFE_INTERNAL_TOKEN`
- `POST /api/v1/internal/source-import-run?include_official_cost=true` with `LIFE_INTERNAL_TOKEN`
- `POST /api/v1/internal/source-import-run?live_fetch=true&promote=true` with `LIFE_INTERNAL_TOKEN`
- `GET /api/v1/internal/source-import-artifacts` with `LIFE_INTERNAL_TOKEN`
- `GET /api/v1/internal/source-data-releases` with `LIFE_INTERNAL_TOKEN`
- `POST /api/v1/internal/source-data-releases/{release_key}/notes` with `LIFE_INTERNAL_TOKEN`
- `POST /api/v1/internal/source-data-releases/{release_key}/rollback` with `LIFE_INTERNAL_TOKEN`
- `POST /api/v1/internal/alerts/evaluate` with `LIFE_INTERNAL_TOKEN`

## Data Truth

Ariva is live-powered, not fake streaming. It calls the upstream domain APIs with short caching, records integration runs, and stores normalized domain snapshots for central history. If an upstream is unavailable, the API returns a degraded domain state with fixture-backed structure instead of breaking the dashboard. Personal account data never overrides source labels, confidence, freshness notes, or source governance fields. `/life/source-validation` checks registry uniqueness, governance fields, district/weather coverage, scoring-source review status, and official cost/import source coverage. `/life/source-release` gives the public UI the active promoted release key, source keys, observed time, snapshot counts, and seed-fallback state without exposing protected artifact ids, checks, or operator notes. `/internal/source-import-audit` validates typed district/weather import contracts plus source-labelled official cost seed rows, reviewed PUCSL/NWSDB/NTC/CPC/CBSL/Customs parser fixtures, and source-run evidence. `/internal/source-import-plan` records the direct-import manifest for DCS, Met/DMC/Irrigation, nuuuwan extracts, official tariff/import sources, and public-apis provider discovery before seed rows are replaced. `/internal/source-import-run` can execute direct district-profile and weather/risk importers in offline contract mode or live-fetch mode against raw nuuuwan Census 2024, `lk_admin_regions`, `lk_weather_3h`, and `lk_irrigation` JSON, then records checksum and reconciliation evidence for promotion review. Adding `include_official_cost=true` appends a review-only official cost/import evidence run for PUCSL, NWSDB, NTC, CPC, CBSL, and Sri Lanka Customs; `promote=true` is rejected for that family. Persisted runs now also write compact `source_import_artifacts` with source keys, checks, and normalized district/weather or official-cost review records, without storing raw upstream payloads. `/internal/source-import-artifacts` gives operators a protected review path for those stored artifacts, with normalized records hidden unless requested. Adding `promote=true` is guarded to live-fetch, persisted, fully healthy district/weather direct runs; it promotes normalized records into canonical `district_profile_snapshots` and `weather_risk_snapshots`, stores 78 area score snapshots for the national view plus 25 districts across 3 household profiles, and writes a versioned `source_data_releases` record. New promotions automatically supersede older promoted releases. Public Atlas and weather/risk responses use the latest complete promoted release and fall back to reviewed seeds when coverage is incomplete. `/internal/source-data-releases` exposes active release identity, source artifacts, source keys, checks, lifecycle status, operator notes, and snapshot counts for operator review. Protected release note and rollback endpoints let operators document review decisions and withdraw the active release while reactivating the previous complete release when available. `/internal/source-refresh` gives operators one protected refresh path that returns pipeline state, source-validation state, import-audit state, import-plan state, optional alert evaluation, and action notes. Weather/risk rows are labelled planning signals, not emergency alerts; Cost Desk tariff/import rows are labelled planning signals until live PUCSL/NWSDB/NTC/CPC/CBSL/Customs fetch evidence and operator review allow promotion.

## Docs

- `docs/architecture.md` - product and technical architecture.
- `docs/source-roadmap.md` - official source expansion and limitations.
- `docs/source-opportunity-map.md` - source opportunity map for public APIs, Sri Lanka datasets, and Ardeno platforms.
- `docs/source-deep-research.md` - evidence-backed research dossier for the next source expansion.
- `docs/industry-standard-execution-plan.md` - phased roadmap, backlog, and quality gates.
- `docs/verification.md` - local and production smoke checks.
