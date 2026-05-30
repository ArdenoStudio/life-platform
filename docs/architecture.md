# Architecture

Ariva is a public-first Sri Lanka living-intelligence product. It does not copy scraper code from the existing domain platforms in v1. FoodLK, Octane, PropertyLK, and AutoLens remain the source-of-truth systems, while Ariva adapts their public APIs into one national signal desk and central warehouse.

Hybrid accounts are optional. The public atlas, search, source registry, and affordability views continue to work without login. Firebase Auth only unlocks saved profile preferences, watchlists, alert rules, and in-app notifications.

The operator release-review console is available as an unlisted `/?page=operator` frontend route. It asks for `LIFE_INTERNAL_TOKEN` at runtime and does not embed or persist the token in the browser app.

## Runtime Shape

- Frontend: Vite React app deployed on Vercel, with lazy page chunks and separate Firebase/chart vendor chunks so the public shell does not download optional auth or every dashboard chart up front.
- Backend: FastAPI app deployed on Fly.
- Database: Postgres in production, SQLite-compatible local development.
- ORM and migrations: SQLAlchemy and Alembic.
- CI: backend pytest plus frontend lint, tests, and build.

## Backend Flow

1. A public Ariva API request enters `/api/v1/life/*`.
2. `LifeService` asks each domain adapter for a normalized `DomainSignal`.
3. Each adapter calls its upstream API with a timeout and returns a degraded fallback signal if the upstream is unavailable.
4. The service records an `integration_runs` row for each adapter call.
5. Normalized summaries are stored in `domain_snapshots`.
6. Affordability calculations are stored in `life_index_snapshots`.
7. Authenticated `/me/*` requests verify Firebase ID tokens, upsert `user_profiles`, and combine the public overview with user-owned saved items, alert rules, and notifications.

## Central Tables

- `domains`: registry of source domains, API bases, platform URLs, and enabled flags.
- `domain_snapshots`: normalized time-series summaries, metrics, highlights, and source timestamps.
- `life_index_snapshots`: household-profile affordability outputs by district.
- `integration_runs`: per-domain adapter execution status, errors, and payload summaries.
- `source_import_artifacts`: compact direct-import artifacts with source keys, checks, normalized records, and no raw upstream payload storage.
- `district_profile_snapshots`, `weather_risk_snapshots`: promoted canonical serving snapshots produced from reviewed direct-import artifacts.
- `source_data_releases`: versioned promoted source-data batches with artifact ids, source keys, checks, snapshot counts, lifecycle status, rollback timestamps, and operator notes.
- `source_registry`, `tariff_snapshots`, `retail_offer_snapshots`, `transport_fare_snapshots`, `area_score_snapshots`, `public_insight_snapshots`: public source, tariff, transport, area-score, and insight history.
- Official utility, LPG, transport, fuel, CBSL exchange context, and Sri Lanka Customs tariff references are source-registry rows before direct parser automation; current tariff and fare rows are labelled planning inputs and are snapshotted when the public cost endpoints are called. Reviewed parser fixtures now cover the main official publication formats, but live tariff/import promotion remains operator-reviewed.
- `user_profiles`: Firebase subject, display metadata, saved locale, district, and household profile.
- `saved_items`: user-owned saved public-domain searches, source watches, or item references.
- `alert_rules`: user-owned source/metric alert conditions.
- `notifications`: in-app alert results with read state and user-level idempotency.

## Public API

- `GET /api/v1/life/overview`
- `GET /api/v1/life/domains`
- `GET /api/v1/life/search?q=...`
- `GET /api/v1/life/affordability?district=...&profile=...`
- `GET /api/v1/life/trends?domain=...`
- `GET /api/v1/life/pipeline`
- `GET /api/v1/life/source-validation`
- `GET /api/v1/life/source-release`
- `GET/PUT /api/v1/me/profile`
- `GET/POST/DELETE /api/v1/me/saved-items`
- `GET/POST/PATCH/DELETE /api/v1/me/alerts`
- `GET/PATCH /api/v1/me/notifications`
- `GET /api/v1/me/life-pulse`
- `POST /api/v1/internal/source-refresh`
- `POST /api/v1/internal/source-import-audit`
- `POST /api/v1/internal/source-import-plan`
- `POST /api/v1/internal/source-import-run`
- `GET /api/v1/internal/source-import-artifacts`
- `GET /api/v1/internal/source-data-releases`
- `POST /api/v1/internal/source-data-releases/{release_key}/notes`
- `POST /api/v1/internal/source-data-releases/{release_key}/rollback`
- `POST /api/v1/internal/alerts/evaluate`

## Product Rules

- Sri Lanka, LKR, district-aware data, and source transparency are defaults.
- Live-powered means short-cache live API calls plus visible freshness, not fake streaming.
- Food uses scheduled-refresh language.
- Fuel can be checked more frequently, but still carries a timestamp and source state.
- v1 stores normalized summaries and time-series snapshots first, not every raw listing or raw market quote.
- Internal source import audit validates typed district/weather seed import contracts and records source-run evidence in `integration_runs`.
- Internal source import plan records direct-import manifests for source-family promotion readiness before seed rows are replaced.
- Internal source import run executes guarded direct district-profile and weather/risk importers in offline contract or live-fetch mode, captures upstream checksums, persists compact normalized `source_import_artifacts`, and records reconciliation evidence before any scoring promotion.
- Adding `include_official_cost=true` to internal source import run appends a review-only official cost/import evidence run for PUCSL, NWSDB, NTC, CPC, CBSL, and Sri Lanka Customs; it persists artifacts but cannot be promoted.
- `promote=true` also writes canonical `district_profile_snapshots` and `weather_risk_snapshots`, records a `source_data_releases` row, and supersedes older promoted releases; public Atlas and weather/risk responses use the latest complete promoted release, otherwise they fall back to reviewed seed data.
- Public source-release transparency is deliberately smaller than internal release review: `/life/source-release` exposes active release key, source keys, observed time, snapshot counts, and seed-fallback state, while artifact ids, checks, and operator notes stay behind protected internal endpoints.
- Internal source import artifacts are exposed through a protected review endpoint; normalized records are omitted by default and only returned when `include_records=true`.
- Internal source data releases are exposed through protected review, note, and rollback endpoints so operators can inspect active batch identity, document decisions, withdraw a bad active release, and reactivate the previous complete release without direct DB access.
- The unlisted operator console can list source-data releases, display release checks and artifact counts, add review notes, and trigger rollback only after a runtime internal token is provided.
- Internal source import run accepts `promote=true` only with live-fetch persisted evidence; a fully healthy accepted run writes area-score snapshots for all districts and household profiles.
- Internal source refresh returns pipeline status, source-validation status, import-audit status, import-plan status, optional alert evaluation, and action notes from one protected operator endpoint.
- The official tariff/import manifest is deliberately `needs_parser`: PUCSL, NWSDB, NTC, CPC, CBSL, and Customs parser fixtures produce typed review evidence, but live source fetches, PDF/text extraction, effective-date checks, and operator notes are still required before replacing source-labelled planning rows.
- Auth is additive: missing Firebase frontend config hides sign-in controls, and missing backend Firebase config only affects authenticated endpoints.
- Personal alerts are in-app for v1; email, WhatsApp, and push are later notification channels.
