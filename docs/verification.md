# Verification

## Backend

```powershell
cd backend
python -m pip install -r requirements.txt
python -m pytest
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8090
```

Smoke checks:

```powershell
Invoke-WebRequest http://127.0.0.1:8090/api/v1/life/overview
Invoke-WebRequest http://127.0.0.1:8090/api/v1/life/pipeline
Invoke-WebRequest http://127.0.0.1:8090/api/v1/life/source-release
Invoke-WebRequest "http://127.0.0.1:8090/api/v1/life/search?q=petrol"
```

Authenticated local smoke with test auth:

```powershell
$headers = @{ Authorization = "Bearer life-test-token" }
$env:APP_ENV="test"
$env:LIFE_TEST_AUTH_TOKEN="life-test-token"
$env:LIFE_INTERNAL_TOKEN="internal-test-token"
Invoke-WebRequest http://127.0.0.1:8090/api/v1/me/profile -Headers $headers
Invoke-WebRequest http://127.0.0.1:8090/api/v1/me/life-pulse -Headers $headers
Invoke-WebRequest "http://127.0.0.1:8090/api/v1/internal/source-import-audit" -Method POST -Headers @{ Authorization = "Bearer internal-test-token" }
Invoke-WebRequest "http://127.0.0.1:8090/api/v1/internal/source-import-plan" -Method POST -Headers @{ Authorization = "Bearer internal-test-token" }
Invoke-WebRequest "http://127.0.0.1:8090/api/v1/internal/source-import-run?live_fetch=false" -Method POST -Headers @{ Authorization = "Bearer internal-test-token" }
Invoke-WebRequest "http://127.0.0.1:8090/api/v1/internal/source-import-run?live_fetch=false&include_official_cost=true" -Method POST -Headers @{ Authorization = "Bearer internal-test-token" }
Invoke-WebRequest "http://127.0.0.1:8090/api/v1/internal/source-import-run?live_fetch=true&promote=true" -Method POST -Headers @{ Authorization = "Bearer internal-test-token" }
Invoke-WebRequest "http://127.0.0.1:8090/api/v1/internal/source-import-artifacts" -Headers @{ Authorization = "Bearer internal-test-token" }
Invoke-WebRequest "http://127.0.0.1:8090/api/v1/internal/source-data-releases" -Headers @{ Authorization = "Bearer internal-test-token" }
Invoke-WebRequest "http://127.0.0.1:8090/api/v1/internal/source-data-releases/<release-key>/notes" -Method POST -Headers @{ Authorization = "Bearer internal-test-token" } -ContentType "application/json" -Body '{"note":"Reviewed release evidence."}'
Invoke-WebRequest "http://127.0.0.1:8090/api/v1/internal/source-data-releases/<release-key>/rollback" -Method POST -Headers @{ Authorization = "Bearer internal-test-token" } -ContentType "application/json" -Body '{"note":"Rollback after operator review.","reactivate_previous":true}'
Invoke-WebRequest "http://127.0.0.1:8090/api/v1/internal/source-refresh?force_refresh=true&evaluate_alerts=true" -Method POST -Headers @{ Authorization = "Bearer internal-test-token" }
Invoke-WebRequest http://127.0.0.1:8090/api/v1/internal/alerts/evaluate -Method POST -Headers @{ Authorization = "Bearer internal-test-token" }
```

## Frontend

```powershell
cd frontend
npm install
npm run lint
npm run test
npm run build
npm run dev
```

Smoke checks:

- Production build keeps the initial app chunk small and splits chart/auth code into separate lazy chunks; no Vite chunk-size warning should appear.
- Dashboard renders Ariva and Sri Lanka Living Intelligence.
- Eleven domains appear, including Food, Fuel, Property, Vehicle, District Life Scores, and Weather and Risk.
- Search finds a fuel or food signal.
- Sources page shows upstream health and limitations.
- Sources page shows source validation status plus the active promoted source-release state or reviewed seed fallback.
- `/?page=operator` renders the protected source-release review shell without exposing internal release data until a runtime token is entered.
- With `VITE_FIREBASE_*` configured, sign-in appears; without it, public pages render and account controls stay hidden.
- With `VITE_LIFE_TEST_AUTH_TOKEN`, My Ariva Pulse renders saved profile, watches, alert rules, and notifications in tests.
- Compare and affordability views do not overflow on mobile widths.

Playwright smoke after backend and frontend are running:

```powershell
$env:LIFE_E2E_BASE_URL="http://127.0.0.1:3001"
npm run test:e2e
```

## Production

- `GET /api/v1/life/overview` returns all four domains.
- `GET /api/v1/life/pipeline` returns a domain status list, even if one upstream is degraded.
- `GET /api/v1/life/source-validation` returns the current registry and score-source validation state.
- `GET /api/v1/life/source-release` returns active public release identity, observed time, source keys, snapshot counts, and seed-fallback state without internal artifact ids, checks, or operator notes.
- `GET /api/v1/me/profile` returns 401 without a Firebase ID token.
- `POST /api/v1/internal/source-import-audit` is protected by `LIFE_INTERNAL_TOKEN` and returns typed importer checks for district/weather source families.
- `POST /api/v1/internal/source-import-audit` includes the official cost seed importer for typed PUCSL/NWSDB/LPG/NTC/CPC planning rows, tariff/transport snapshot targets, and reviewed parser fixtures for PUCSL, NWSDB, NTC, CPC, CBSL, and Sri Lanka Customs.
- `POST /api/v1/internal/source-import-plan` is protected by `LIFE_INTERNAL_TOKEN` and returns direct-import manifests for source promotion readiness, including a `needs_parser` official tariff/import manifest with passing source-specific parser fixtures plus a live-promotion watch gate for PUCSL, NWSDB, NTC, CPC, CBSL, Sri Lanka Customs, and isolated Currency API fallback review.
- `POST /api/v1/internal/source-import-run?live_fetch=true` is protected by `LIFE_INTERNAL_TOKEN` and runs the district-profile direct importer against raw nuuuwan Census 2024 JSON plus `lk_admin_regions` geography JSON, and the weather/risk direct importer against `lk_weather_3h` plus `lk_irrigation` JSON, for promotion review. Persisted runs write compact `source_import_artifacts` with normalized records and do not store raw payloads.
- `POST /api/v1/internal/source-import-run?include_official_cost=true` is protected by `LIFE_INTERNAL_TOKEN` and adds a review-only official cost/import run with parser evidence artifacts for PUCSL, NWSDB, NTC, CPC, CBSL, and Sri Lanka Customs. `promote=true&include_official_cost=true` must return 400 because tariff/import promotion is not cleared.
- `POST /api/v1/internal/source-import-run?live_fetch=true&promote=true` is protected by `LIFE_INTERNAL_TOKEN`, requires persisted live evidence, rejects offline promotion, writes canonical `district_profile_snapshots` and `weather_risk_snapshots`, writes a `source_data_releases` row, supersedes older promoted releases, and writes 78 `area_score_snapshots` only when every direct run is healthy and accepted for scoring.
- `GET /api/v1/internal/source-import-artifacts` is protected by `LIFE_INTERNAL_TOKEN` and returns stored artifact metadata; normalized records are returned only when `include_records=true`.
- `GET /api/v1/internal/source-data-releases` is protected by `LIFE_INTERNAL_TOKEN` and returns active release identity, lifecycle status, operator notes, promoted release keys, artifact ids, source keys, checks, and snapshot counts.
- `POST /api/v1/internal/source-data-releases/{release_key}/notes` is protected by `LIFE_INTERNAL_TOKEN` and appends operator review notes without changing serving state.
- `POST /api/v1/internal/source-data-releases/{release_key}/rollback` is protected by `LIFE_INTERNAL_TOKEN`, marks the active promoted release as `rolled_back`, and reactivates the previous complete superseded release when `reactivate_previous=true`.
- The frontend operator route `/?page=operator` must not call `/internal/source-data-releases` until a token is entered, and requests must send the token as a bearer header rather than a query parameter.
- The Cost Desk must show source keys on cost, utility, and transport rows so official, platform, and derived inputs are not visually collapsed.
- Food search, food insights, and Cost Desk savings moves must expose the source-labelled protein-basket planning signal without adding it as a duplicate monthly cost item.
- `POST /api/v1/internal/source-refresh` is protected by `LIFE_INTERNAL_TOKEN` and returns refresh, validation, import-audit, import-plan, pipeline, and action summaries.
- `POST /api/v1/internal/alerts/evaluate` is protected by `LIFE_INTERNAL_TOKEN`.
- Dashboard renders from the deployed Vercel frontend with `VITE_API_URL` pointing to the Fly backend.
