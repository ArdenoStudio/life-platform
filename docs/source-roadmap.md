# Source Roadmap

For the deeper research and execution path behind this roadmap, see:

- `docs/source-opportunity-map.md`
- `docs/source-deep-research.md`
- `docs/industry-standard-execution-plan.md`

## Active v1 Adapters

- FoodLK: hub summary, platform freshness, essentials basket, item/market quote-ready structure.
- Octane: latest fuel pricing, health, and trip-calculator-ready fuel rates.
- PropertyLK: national stats, districts, pipeline, rental-yield-ready structure.
- AutoLens: market stats, trends, listings/estimate-ready summaries, pipeline status.
- District Atlas v2 seed: Census 2024 and public Lanka Data district profile facts for national + 25 district comparisons.
- Weather and risk seed: Met Department 3-hour extract, DMC, public river datasets, and reviewed irrigation water-level context for district planning. Open-Meteo remains a visible candidate source until forecast ingestion is reviewed.
- Direct-import readiness manifests: protected operator manifests for DCS Census 2024, nuuuwan district extracts, Met Department 3-hour weather, DMC, public river extracts, and public-apis provider discovery.
- Direct district-profile import run: protected operator run can fetch raw nuuuwan Census 2024 population, household, and cooking-fuel JSON, normalize it into typed district rows, persist compact importer artifacts, compare it against reviewed seeds, and participate in guarded area-score snapshot promotion.
- Direct weather/risk import run: protected operator run can fetch raw `lk_weather_3h` station observations plus `lk_irrigation` water-level JSON, normalize them into typed planning rows, persist compact importer artifacts, compare station weather fields against reviewed seeds, and participate in guarded area-score snapshot promotion.
- Operator release console: unlisted frontend route for source-data release review, runtime-token loading, evidence inspection, review notes, and rollback actions.
- Atlas compare lens: public district-to-district comparison of score, population, household, density, household energy, age-share, and component gaps from the current sourced Atlas response.
- Official cost seed audit: typed PUCSL/NWSDB/LPG/NTC/CPC planning rows now participate in `/internal/source-import-audit`, write tariff/transport snapshots through public cost endpoints, surface source keys directly in the Cost Desk, and validate reviewed parser fixtures for PUCSL, NWSDB, NTC, CPC, CBSL, and Sri Lanka Customs.
- Official tariff/import manifest: `/internal/source-import-plan` now includes source-specific parser contracts for PUCSL tariff decisions, NWSDB domestic water tables, NTC fare indexes, CPC fuel price cards, CBSL exchange-rate page structure, Sri Lanka Customs import-tariff metadata, and optional Currency API review; it stays `needs_parser` until live fetch evidence and operator release notes are reviewed.
- Official cost direct review run: `/internal/source-import-run?include_official_cost=true` now persists review-only parser evidence artifacts for PUCSL, NWSDB, NTC, CPC, CBSL, and Sri Lanka Customs; `promote=true` is rejected for this family until live extraction and operator evidence are approved.
- Food protein basket signal: public food insights, search, and Cost Desk savings moves now expose a reviewed weekly protein-basket planning signal using FoodLK, CBSL/HARTI, Nuwan `lk_food`, official fisheries, and `lk_fisheries` context without double-counting it in the monthly cost total.

## Official Expansion

- Food: CBSL Daily Price Report, HARTI daily bulletin, CAA maximum retail prices, World Bank RTP food prices.
- Fuel, utilities, transport: CPC fuel pricing, PUCSL electricity tariffs, NTC bus fares.
- Imports and vehicle context: Sri Lanka Customs tariff, CBSL exchange rates.

## Affordability Index

The Ariva affordability index is a practical Sri Lanka-local planning basket. It combines weighted food, housing, fuel, vehicle, utilities, and transport signals. Numbeo-style basket categories are useful as a methodology reference, but Ariva should use Sri Lanka-local source data and clearly labelled assumptions.

## Limits

- The v1 property and vehicle contributions use conservative planning proxies when rental-yield or ownership-cost feeds are not normalized yet.
- Utility and transport inputs are source-labelled v1 planning rows backed by official references; reviewed parser fixtures now cover the major official cost/import formats, but live tariff/import promotion is still staged behind operator review before unattended use.
- Protein/meal affordability is a planning signal, not a nutrition prescription. It uses source-labelled seed quantities and prices until live item matching and official fisheries/food extraction are promoted.
- District profile facts are currently reviewed seed data plus a guarded direct importer. Use `promote=true` only after live direct evidence is healthy and persisted.
- Weather/risk rows are planning signals, not operational alerts. Weather-station and irrigation water-level direct imports can support planning-score promotion, but DMC warning automation remains a separate gate before emergency alerting.
- Source references now expose owner, collection method, license status, review status, refresh cadence, and governance notes. Derived or retail candidates stay marked as review/terms work until cleared.
- `/life/source-validation` is the current promotion gate: scoring dependencies must exist and be approved or reviewed before they influence Atlas outputs.
- `/internal/source-import-plan` is the current direct-import promotion gate: ready source jobs can be marked direct-ready, while unresolved parser contracts, terms review, and storage targets stay in watch status.
- `/internal/source-import-run` is the current execution gate for district profiles and weather/risk: it records live-fetch/offline-contract mode, upstream checksums, row counts, compact normalized `source_import_artifacts`, and seed reconciliation; `live_fetch=true&promote=true` is the explicit persisted promotion path and writes area-score snapshots only when every promotable direct run is healthy and accepted for scoring. Add `include_official_cost=true` only for review-only tariff/import evidence; that family does not promote.
- `/internal/source-import-artifacts` is the protected review gate for persisted importer artifacts: operators can list metadata by run key and opt into normalized records without exposing raw upstream payloads.
- Promoted direct runs now write canonical `district_profile_snapshots`, `weather_risk_snapshots`, and versioned `source_data_releases`; new promotions supersede older promoted releases, and public Atlas/weather responses read the latest complete promoted release before falling back to reviewed seeds.
- `/life/source-release` is the public transparency surface for the active release: it shows promoted/seed-fallback state, active release key, observed time, source keys, and snapshot counts without exposing internal artifact ids, checks, or operator notes.
- `/internal/source-data-releases` plus its protected note and rollback actions are the release review gate for promoted batches, including active release identity, artifact ids, source keys, checks, lifecycle status, operator notes, and snapshot counts.
- `/?page=operator` is the protected browser workflow for that release review gate; it must stay unlisted from public navigation and must require a runtime token before internal data loads.
- Upstream failures should degrade one domain, not fail the full platform.
