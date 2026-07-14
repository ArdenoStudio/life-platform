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

Smoke checks (District Life Pulse MVP IA):

- Production build keeps the initial app chunk small and splits chart/auth code into separate lazy chunks; no Vite chunk-size warning should appear.
- **Today** (`/?page=today` or default home): renders Ariva District Life Pulse hero with **Cost of Life** score, three sister cards (**Food**, **Fuel**, **Shelter**), trust strip (release badge + degradation banner when any sister is degraded/offline), and sticky district in shell chrome.
- Sister cards expose source-class pills, freshness notes, and platform deep links with `utm_source=ariva_life_pulse`.
- **Trust** (`/?page=trust`): sister adapter list (food / fuel / property), source validation, active source-release card, and source-class glossary.
- **Decide** (`/?page=decide`): two-district compare loads without horizontal overflow; district and profile selectors work.
- Search finds a fuel or food signal.
- `/?page=operator` renders the protected source-release review shell without exposing internal release data until a runtime token is entered.
- With `VITE_FIREBASE_*` configured, sign-in appears; without it, public pages render and account controls stay hidden.
- With `VITE_LIFE_TEST_AUTH_TOKEN`, My Ariva Pulse renders saved profile, watches, alert rules, and notifications in tests.
- Cost Desk and Decide views do not overflow on mobile widths.

Playwright smoke after backend and frontend are running:

```powershell
$env:LIFE_E2E_BASE_URL="http://127.0.0.1:3001"
npm run test:e2e
```

Targeted Life Pulse routes (same `LIFE_E2E_BASE_URL`):

```powershell
# Today IA — sisters + Cost of Life hero
npx playwright test tests/e2e/life-dashboard.spec.ts -g "Ariva home"

# Trust tab — registry, validation, release card
npx playwright test tests/e2e/life-dashboard.spec.ts -g "sources and trilingual"

# Decide — covered by Playwright smoke (`decide page loads with compare params`)
# Open http://127.0.0.1:3001/?page=decide&district=Colombo&profile=family

# Manual deep-link spot check (sister platform URLs from overview)
curl -s "http://127.0.0.1:8090/api/v1/life/overview?district=Colombo&profile=family" | python -m json.tool | rg homepage_url

# Deep-link rot script (when present under repo root)
node scripts/check-deep-links.mjs
```

Manual URL smoke:

```text
http://127.0.0.1:3001/?page=today&district=Kandy&profile=family&locale=en
http://127.0.0.1:3001/?page=trust&district=Colombo&locale=en
http://127.0.0.1:3001/?page=decide&district=Colombo&compare=Kandy&profile=family
```

## Kill-criteria telemetry (60-day review — 2026-09-11)

Revival **fails** if any kill criterion is true at evaluation. **Continuation** requires ≥4 of 5 category groups passing (Adoption, Reliability, Trust, Product). Full thresholds: [`docs/superpowers/specs/2026-07-13-ariva-revival-design.md`](superpowers/specs/2026-07-13-ariva-revival-design.md#60-day-kill-criteria).

| Category | Criterion | Threshold | How to measure |
|----------|-----------|-----------|----------------|
| Adoption | Weekly active district users | ≥ 500 WAU | Analytics: unique clients with `GET /life/overview` + `district != Sri Lanka` (event `pulse.today_view` + district param) |
| Adoption | D7 return rate | ≥ 15% | Cohort: users with `pulse.today_view` on day 0 returning within 7 days |
| Adoption | Sticky district rate | ≥ 40% | Sessions where `pulse.district_change` district matches first session district in week |
| Reliability | Sister live rate | ≥ 85% each | `integration_runs`: `success / total` per `domain_key` in `food`, `fuel`, `property` over trailing 14 days |
| Reliability | Overview p95 latency | ≤ 2.5s | API telemetry / load-test p95 for `GET /api/v1/life/overview` |
| Reliability | Silent fallback incidents | 0 | Incidents where degraded sister data rendered without Today degradation banner (`signalsDegradedBanner`) |
| Trust | Trust chrome completeness | 100% on sisters | UI audit: each sister card has source class, confidence, freshness; contract tests in `frontend/tests/e2e/life-dashboard.spec.ts` + `backend/tests/test_life_api.py` |
| Trust | Deep link rot | ≤ 10% broken | Weekly `node scripts/check-deep-links.mjs` against sister `homepage_url` samples from overview |
| Trust | Source-release transparency | Present on Today | Manual QA: Trust strip shows promoted or seed-fallback release key on Today |
| Product | Cost score comprehension | ≥ 50% “understand score” | In-app micro-survey (n ≥ 100) after Cost tab visit (`pulse.cost_detail_view`) |
| Product | Deep link CTR | ≥ 5% | `pulse.deep_link_click` / `pulse.today_view` ratio by sister |

**Pre-review SQL (Postgres, adjust window):**

```sql
-- Sister adapter uptime (14-day window)
SELECT domain_key,
       COUNT(*) FILTER (WHERE status = 'success')::float / NULLIF(COUNT(*), 0) AS success_rate
FROM integration_runs
WHERE domain_key IN ('food', 'fuel', 'property')
  AND started_at >= NOW() - INTERVAL '14 days'
GROUP BY domain_key;

-- Latest Cost of Life snapshots (derived index persistence)
SELECT district, profile, total_lkr, confidence, observed_at
FROM life_index_snapshots
ORDER BY observed_at DESC
LIMIT 20;
```

**Pre-review checklist (week of 2026-09-04):**

1. Run full E2E suite (`npm run test:e2e`) against preview + production URLs.
2. Run `node scripts/check-deep-links.mjs` and attach failure list if any.
3. Export analytics counts for `pulse.*` events (30-day window).
4. Confirm Today shows three sisters + Cost of Life + trust strip on production.
5. File kill / re-park / continue decision with evidence in `docs/superpowers/specs/`.

## Production

- `GET /api/v1/life/overview` returns `survival_index` labelled **Cost of Life** (MVP weights: food 45%, fuel 20%, shelter 35%) plus domain signals; Today consumes the three sister keys (`food`, `fuel`, `property`) only.
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
