# Industry-Standard Execution Plan

Date: 2026-05-28

This plan turns the source research into the work needed for Ariva/Life Platform to feel like a serious public product, not a demo that happens to have many datasets.

## Definition Of Industry Standard

Ariva is industry-standard when all of these are true:

- Product: every page has a clear user job, a clear source trail, and a meaningful next action.
- Data: every metric has provenance, freshness, confidence, validation status, and a fallback state.
- Engineering: adapters are isolated, typed, tested, cached, observable, and resilient to upstream failure.
- UX: mobile and desktop layouts are polished, fast, accessible, and free from fake "live" claims.
- Security: secrets stay server-side, auth is additive, inputs are validated, and external calls are bounded.
- Operations: ingestion runs are inspectable, failures are visible, and CI covers API, frontend, and e2e smoke paths.
- Commercial: the free product is useful, while paid/pro paths are obvious and grounded in real buyer value.

## North Star

Ariva should become the Sri Lanka Living Intelligence OS:

- Citizens use it to understand daily cost, district quality, commute, weather/risk, and public changes.
- Families use it to compare where life is affordable and practical.
- SMBs use it to understand tourism, food supply, local demand, and operating conditions.
- Ardeno uses it as a flagship proof point for Sri Lanka-local data products.

## Product Pillars

### 1. Daily Life Desk

Current base:

- FoodLK, Octane, PropertyLK, AutoLens, utility/gas/retail/transport assumptions.

Industry-grade target:

- Cost basket with official/platform/derived separation.
- Meal and protein affordability, not only raw item price.
- Import-cost sensitivity from FX.
- Clear "what changed" insights.

### 2. District Atlas

Current base:

- Static `AREA_BASE` scoring and district heat panels.

Industry-grade target:

- District profiles from census/geography data.
- Weather/risk, source coverage, density, transport, and household context.
- Shareable district reports.
- Score methodology page.

### 3. Source Registry And Data Quality

Current base:

- `SourceRegistry`, source pills, pipeline endpoint, visible source classes.

Industry-grade target:

- Source owner, license status, collection method, last success, last failure, freshness SLA, and review status.
- Public source registry plus internal data-quality dashboard.
- No unreviewed source silently affects important scores.

### 4. Public Intelligence Feed

Current base:

- Static/generated insights from current domains.

Industry-grade target:

- Time-aware insights from source changes.
- Saved-district watch alerts.
- Public "why this matters" explainers.
- Confidence and caveat on every insight.

### 5. Business/Pro Layer

Current base:

- Optional account infrastructure and alerts.

Industry-grade target:

- Tourism demand reports.
- Food/retail operating signals.
- Property/vehicle buyer reports.
- Saved watchlists, exports, and digests.

## Implementation Phases

### Phase 0: Due Diligence And Registry

Goal: make the data foundation credible before scores depend on new inputs.

Tasks:

1. Add source governance metadata to docs and schema: owner, collection method, license status, review status, refresh cadence, and governance notes. Done for public source references and `source_registry`.
2. Add source rows for census, lanka_data, weather, rivers, DMC, irrigation, tourism, fisheries, Central Bank, acts, Hansards, elections, bus/train candidates.
3. Document source license, original source, derived repo, data size, update cadence, and allowed use.
4. Add tests that assert important source keys exist and carry confidence/freshness/governance notes.

Acceptance:

- `/life/domains` and source surfaces still work without auth.
- No score consumes a new source until the source has a reviewed confidence status.
- Unlicensed/no-license metadata sources are visible as `needs_review`, not production inputs.

### Phase 1: District Profiles And Atlas v2

Goal: replace hardcoded district assumptions with sourced district facts.

Status on 2026-05-28: in progress. The API now carries a seeded national + 25 district profile table from Census 2024 extracts and public Lanka Data admin-region metadata. `/life/atlas` returns selected profile facts, all displayed district profiles, score methodology, and source-keyed score components. Weather/risk pressure is now included as a labelled score component. `/life/source-validation` now checks registry uniqueness, district/weather coverage, governance metadata, scoring-source review status, and official cost/import source coverage. `/internal/source-import-run?live_fetch=true&promote=true` now provides the guarded path from healthy direct importer evidence into canonical district/weather snapshots plus 78 persisted area-score snapshots. Persisted source-import runs also write compact `source_import_artifacts` with normalized district/weather records and no raw upstream payload storage, and `/internal/source-import-artifacts` exposes those artifacts through a protected review endpoint. Promoted batches now write versioned `source_data_releases`; new promotions supersede older promoted releases; protected release note and rollback actions let operators document review decisions and withdraw a bad active batch while reactivating the previous complete release. Public Atlas/weather responses read the latest complete promoted release before falling back to reviewed seeds, and `/life/source-release` exposes the public-safe active release state, observed time, source keys, and snapshot counts on the Sources page without internal artifact ids, checks, or operator notes. The unlisted `/?page=operator` console now gives operators a runtime-token workflow to inspect releases, checks, artifact counts, notes, and rollback actions without direct DB access. Atlas now has a district-to-district comparison lens for score, population, household, density, household energy, age-share, and component gaps. The official cost tranche now registers Sri Lanka Customs tariff context, audits typed official cost seed rows, labels Cost Desk utility/transport/import source keys, validates source-specific parser fixtures for PUCSL tariff decisions, NWSDB domestic water tables, NTC fare indexes, CPC fuel price cards, CBSL exchange-rate page structure, and Sri Lanka Customs import-tariff metadata, and exposes `/internal/source-import-run?include_official_cost=true` as a review-only artifact path. The official tariff/import manifest still stays `needs_parser`; `promote=true` is rejected for this family until live source extraction, effective-date checks, and operator release notes are approved.

Tasks:

1. Create a normalized district profile dataset/module. Done as a reviewed seed table.
2. Add fields: district, province, population, households, area, density, center lat/lng, source keys, confidence. Done in API responses.
3. Add backend response types for district profile and score methodology. Done.
4. Update `AreaScoreAdapter` to use district profile inputs while retaining low-confidence fallback values. Done for density, household energy, source coverage, transport proxy, and rent-pressure proxy.
5. Add frontend Atlas refinements: source coverage, methodology, district facts, and compare mode.

Acceptance:

- `/life/atlas` returns district fact evidence for every displayed district.
- `/life/areas/score` score components can explain source domains and confidence.
- `/life/source-validation` passes before a scored source dependency is promoted.
- Tests cover valid district, unknown district fallback, profile variations, and source presence.
- Browser check confirms mobile and desktop layouts do not overflow.

### Phase 2: Weather And Risk Domain

Goal: add a first real new public domain after Atlas is grounded.

Status on 2026-05-28: in progress. Ariva now has a `weather` domain, `/life/weather-risk`, source-labelled district weather/risk observations, and a Signals-page weather/risk watch. `/internal/source-import-run?live_fetch=true` can validate raw `lk_weather_3h` station observations plus `lk_irrigation` water-level context, persist compact normalized weather/risk artifacts, promote canonical weather/risk snapshots, and `promote=true` only persists scoring snapshots after every direct run passes. This is still not an emergency alert feed; the production next step is DMC warning ingestion plus Open-Meteo forecast enrichment.

Tasks:

1. Add `weather` or `risk` domain key after schema/type update.
2. Add station/district mapping and latest weather/rain pressure snapshots.
3. Add source registry rows for Department of Meteorology, DMC, rivers, and irrigation candidates.
4. Add public insights: heavy rain, heat/humidity, river/flood watch where data supports it.
5. Add optional account alert rules for saved district risk.

Acceptance:

- Upstream failure degrades only the weather/risk domain.
- Weather/risk cards show observed time, source, confidence, and station coverage.
- No user alert is generated without source-backed evidence and idempotency.

### Phase 3: Food, Nutrition, And Supply Upgrade

Goal: make FoodLK plus `lk_food`/fisheries context feel smarter than a price table.

Status on 2026-05-30: started. Ariva now exposes a reviewed weekly protein-basket planning signal in public food insights, food/nutrition search, and Cost Desk savings moves. The signal uses FoodLK, CBSL/HARTI, Nuwan `lk_food`, official fisheries, and `lk_fisheries` source keys, keeps confidence visible, and does not double-count the protein basket inside the monthly cost total.

Tasks:

1. Add meal/protein basket calculations with clear assumptions.
2. Add substitution suggestions from item categories and nutrition.
3. Add fisheries reports as context for fish/protein supply pressure.
4. Add public insights for "food basket moved because..." style explanations.

Acceptance:

- Food insights distinguish market price, retail offer, nutrition, and supply context.
- Missing nutrition/supply data lowers confidence instead of hiding uncertainty.
- Search for common food items returns price and nutrition/supply context where available.

### Phase 4: Tourism Demand Module

Goal: create a business-facing reason to pay.

Tasks:

1. Add tourism source registry rows and import metadata for SLTDA weekly/monthly reports.
2. Build a tourism demand signal: arrivals, trend, seasonality note, source freshness.
3. Add a public tourism overview and a pro report concept.
4. Connect district/tourism context to Ardeno SMB lead and custom-dashboard positioning.

Acceptance:

- Tourism data is clearly sourced to official reports.
- Free page gives useful summary.
- Pro plan has a concrete report/export/digest value, not vague "analytics."

### Phase 5: Public Document Intelligence

Goal: build a defensible public-document layer without overloading the app.

Tasks:

1. Build metadata-only index first: title, source, date, language, domain, URL, extraction status.
2. Add summary and search pipeline outside request path.
3. Add document explainers with strict disclaimers.
4. Keep law/parliament content separate from daily-cost scoring unless a human-reviewed methodology connects it.

Acceptance:

- Search results link to original documents.
- Summaries include extraction date and confidence.
- Legal/policy pages do not present advice or official interpretation.

## Engineering Standards

### Backend

- Add one adapter/importer per source family.
- Validate every external payload with typed schemas before storage.
- Use timeouts, retries with caps, and cache windows.
- Store raw-source identifiers but avoid storing huge raw files in the app DB.
- Record `IntegrationRun` status for every automated ingestion.
- Use `/internal/source-import-audit` to run typed seed/import-family checks and record source-run evidence before promotion.
- Use `/internal/source-import-plan` to record direct-import manifests, parser contracts, upstream URLs, promotion status, and next action before replacing reviewed seed rows.
- Use `/internal/source-import-run` for guarded execution: offline contract mode in CI, live-fetch mode for operator checks, and `live_fetch=true&promote=true` for persisted scoring promotion only after the live DCS Census 2024 plus `lk_admin_regions` district lineage checks and the `lk_weather_3h` plus `lk_irrigation` planning-risk lineage checks pass. Use `include_official_cost=true` for review-only tariff/import evidence; do not combine it with `promote=true`.
- Route scheduled operator refreshes through `/internal/source-refresh` so each run returns pipeline health, source-validation state, import-audit state, import-plan state, optional alert evaluation, and clear action notes.
- Keep official tariff/import automation behind `/internal/source-import-plan`: parser fixtures may pass for PUCSL, NWSDB, NTC, CPC, CBSL, and Sri Lanka Customs, but live promotion still requires source fetch checks, PDF/text extraction evidence where needed, effective-date evidence, and operator review notes.
- Tests must cover success, degraded source, malformed payload, and no-data fallback.

### Frontend

- Keep the first screen useful, not a marketing landing page.
- Keep the public shell fast: lazy-load page modules, split heavy chart/auth vendors, and preload destination chunks on navigation hover/focus.
- Source labels must be one click away from every important number.
- Avoid visual clutter; use dense, scannable cards and tables.
- Mobile must be checked for overflow and text fit.
- Public pages must work without Firebase config.

### Data Governance

- Each source gets owner, URL, source type, confidence, freshness note, license status, and review status.
- No unreviewed source drives high-confidence metrics.
- Derived scores must expose formula, weights, and source domains.
- Every public insight needs source keys and observed timestamp.
- Official and derived numbers must never be visually indistinguishable.

### Security And Privacy

- Do not put API keys in frontend builds.
- Validate query inputs and keep external URLs allowlisted where possible.
- Do not scrape or store unnecessary personal data.
- Keep user alerts in-app first; add email/WhatsApp only after consent, suppression, and rate-limiting design.
- Keep auth additive so public browsing remains open.

## Industry-Grade Backlog

| Priority | Item | Why it matters | Proof of done |
| --- | --- | --- | --- |
| P0 | Source due-diligence registry | Prevents messy data trust problems later | Source rows include review status, license note, confidence, freshness, source URL |
| P0 | District profile seed | Removes the biggest fake-looking part of Atlas | Atlas shows sourced population/household/area facts |
| P0 | Atlas methodology | Makes scores defensible | Public methodology text and tests for score components |
| P1 | Weather/risk domain | Adds daily practical value | New domain degrades independently and displays observed source time |
| P1 | Food nutrition/meal basket | Makes food intelligence differentiated | Protein/meal affordability appears with assumptions and tests |
| P1 | Tourism demand module | Creates first credible B2B monetization wedge | Tourism report page or API backed by SLTDA report metadata |
| P2 | Document intelligence index | Adds high-value civic/search layer | Searchable metadata with original source links |
| P2 | Pro reports and digests | Turns platform into sellable product | Export/digest flow with clear pricing hypothesis |
| P2 | Data-quality dashboard | Makes operations trustworthy | Internal/admin pipeline health view |

## First Sprint Recommendation

Build this first:

1. Add source-review metadata docs and source registry rows for census/weather/rivers/tourism/fisheries/civic sources.
2. Create district profile seed data and backend accessors.
3. Update Atlas to show district facts and confidence, while keeping existing score UI stable.
4. Add tests around source registry, district profiles, and `/life/atlas`.
5. Run backend tests, frontend lint/tests/build, and Playwright smoke.

This sprint is the best balance of visible quality, data credibility, and low blast radius.

## Launch Standard

Do not call a release industry-grade until this checklist is green:

- Backend tests pass.
- Frontend lint, tests, and build pass.
- Browser smoke passes on desktop and mobile.
- Source registry has no unlabelled production source.
- Every public metric has source/confidence/freshness.
- New data sources have license/reuse notes.
- Source data releases have an active release identity, operator notes, and a tested rollback path.
- Degraded upstreams do not break public pages.
- README and docs match actual runtime behavior.
- No product copy claims official status, guaranteed accuracy, or legal/financial advice.
