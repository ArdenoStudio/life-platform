# Life Platform Source Opportunity Map

Research date: 2026-05-28

This note maps `marcelscruz/public-apis` and the public `nuuuwan/*` Sri Lanka repositories into practical Ariva/Life Platform expansion work. The current product is already shaped correctly for this: source registry rows, domain adapters, snapshot tables, public insights, district atlas scores, and optional user alerts.

Related artifacts:

- `docs/source-deep-research.md` - evidence-backed research dossier.
- `docs/industry-standard-execution-plan.md` - implementation phases, gates, and backlog.

## Starting Point

Ariva is not missing a generic API catalog. It is missing more Sri Lanka-specific source depth and normalized context around cost of living, districts, mobility, weather, public services, law, tourism, and food supply.

The useful split is:

- `public-apis`: discovery catalog for supporting APIs such as weather, currency, geocoding, Open Food Facts, OpenAQ, TransitLand, World Bank, and NHTSA-style vehicle metadata.
- `nuuuwan/*`: Sri Lanka data accelerator. The strongest repos are not app shells; they are public-data corpora and scripts around census, tourism, fisheries, food, weather, rivers, Hansards, acts, elections, transport, maps, and Central Bank data.
- Existing Ardeno platforms: live commercial/domain signals. FoodLK, Octane, PropertyLK, and AutoLens remain source-of-truth systems for price-intelligence domains.

## Highest-Value Product Direction

Build Ariva into a Sri Lanka Living Intelligence OS with three layers:

1. Daily Life Desk: what it costs to live, commute, cook, rent, buy, and move today.
2. District Atlas: where each district is improving or getting worse across cost, safety, weather, infrastructure, services, food supply, and opportunity.
3. Public Intelligence Feed: plain-language alerts and explainers for people and SMBs, sourced from official/public datasets and labelled by confidence.

The pitch is not "we scraped many repos." The pitch is "one Sri Lanka-local dashboard that explains daily life signals with source transparency."

## Best Nuwan Repos To Mine First

| Area | Repos | What Ariva can do |
| --- | --- | --- |
| Census and districts | `lk_census_2024`, `lk_census_2012`, `lk_census_2001`, `lanka_data`, `geo-data` | Replace static `AREA_BASE` assumptions with population, household, density, and district context. |
| Cost and economics | `lanka_data_search`, `lanka_data_timeseries`, `lk_food` | Add Central Bank and food-history context behind affordability, inflation, and basket movement. |
| Weather and climate | `lk_weather_3h`, `weather_lk`, `lk_rivers` | Add rain, river, flood-risk, and weather pressure into district life scores and alerts. |
| Tourism | `lk_tourism`, `tourism_lk`, `lk_tourism_2025` | Create a tourism demand layer for districts, hotels, transport, restaurants, and SMEs. |
| Fisheries and food supply | `lk_fisheries`, `lk_food` | Explain fish/food availability and supply pressure, not just retail prices. |
| Law and parliament | `lk_acts`, `lk_acts_data`, `lk_hansard`, `parliament_lk` | Build searchable public-law/policy context and plain-English change explainers. |
| Elections and civic data | `elections_lk`, `lk_elections`, `lg_election_lk_2025` | District civic history, turnout, political geography, and public-interest explainers. |
| Mobility and maps | `bus_routes_lk`, `lk_train_scheduler`, `sl-vis`, `sl-maps`, `address_lk` | Better commute scoring, route context, district map components, and local addressing. |

## Best `public-apis` Categories

`public-apis` currently works best as a provider shortlist:

- Weather: Open-Meteo for no-key forecast coverage; OpenWeatherMap if paid/API-key reliability is needed.
- Currency exchange: `Currency-api` or ExchangeRate-API for LKR import-cost and vehicle/import sensitivity.
- Geocoding: BigDataCloud free reverse geocoding, Geoapify, or OpenStreetMap/Nominatim with usage-policy care.
- Food: Open Food Facts for packaged-product metadata, not local market prices.
- Environment: OpenAQ for air-quality context where Sri Lanka coverage exists.
- Open data/science: World Bank for macro context and Sri Lanka comparison lines.
- Transportation: TransitLand only if Sri Lanka feeds exist; otherwise keep NTC/rail/local route sources primary.
- Vehicle: NHTSA/CarAPI-style metadata can enrich vehicle model specs, but AutoLens should remain the local market source.

## Integration Architecture

Do not wire these sources directly into React pages. Add them through the existing backend pattern:

1. Add source definitions to `backend/app/services/living_atlas_data.py`.
2. Normalize source-specific data in new adapters or importer services.
3. Store outputs in existing snapshot tables where possible:
   - `SourceRegistry`
   - `TariffSnapshot`
   - `TransportFareSnapshot`
   - `AreaScoreSnapshot`
   - `PublicInsightSnapshot`
   - `DomainSnapshot`
4. Only add new tables when the data shape is genuinely durable, such as `district_profile_snapshots`, `weather_risk_snapshots`, or `public_document_index`.
5. Expose public read endpoints first; make alerts optional through the existing `/me/*` layer later.

## Fastest Useful Builds

### Phase 1: Source Registry Upgrade

Add source registry rows for census, weather, rivers, tourism, fisheries, law, and Central Bank data. This is low risk because it improves transparency without changing scores yet.

Success criteria:

- `/life/sources` and `/life/pipeline` show the broader roadmap.
- Existing public pages continue working without auth.
- Every source has type, URL, confidence, freshness note, and Sinhala/Tamil labels when useful.

### Phase 2: District Atlas v2

Use census, geo, weather, and transport datasets to replace the current hardcoded district base scores.

New user value:

- "Best districts for a commuter family under LKR X/month."
- "Rent pressure vs food pressure vs transport pressure by district."
- "Weather/flood risk as a public planning signal."

Likely backend work:

- Add `district_profiles` or `district_profile_snapshots`.
- Add a `DistrictDataAdapter`.
- Extend `AreaScoreAdapter` to consume normalized district facts instead of static constants.

### Phase 3: Living Alerts

Add public insights and optional account alerts for:

- Heavy rain/river/flood watch for a saved district.
- Food basket movement or supply pressure.
- Fuel/import-cost sensitivity from LKR exchange movement.
- Tourism surge signals for SMBs.
- Transport fare or route changes.

This fits the existing `alert_rules` and `notifications` model. Do in-app first; WhatsApp/email can come later.

### Phase 4: Public Document Intelligence

Build a searchable public-document layer over acts, Hansards, tourism reports, fisheries reports, and selected government PDFs.

Keep it narrow:

- Store metadata and extracted summaries first.
- Link back to original sources.
- Avoid giving legal advice. Use "public explainer" language.

## What To Avoid

- Do not depend on repos with no license for copied code or data without manual review.
- Do not hide source provenance inside the backend. Public UI can present official original sources cleanly, but internal source lineage must stay traceable.
- Do not claim uniqueness or official status. Say "public-source living intelligence" and show confidence/freshness.
- Do not ingest multi-GB document corpora into the main app database on day one. Start with metadata, summaries, and a search index.
- Do not let global APIs replace local truth. They should fill gaps or add context, not override Sri Lanka official/local data.

## Recommended Next Implementation

The best first implementation is `District Atlas v2`.

Why:

- It uses the Nuwan corpus where it is strongest: census, maps, weather, rivers, and local datasets.
- It improves the visible product immediately.
- It makes the existing affordability score more defensible.
- It gives all other Ardeno platforms a shared Sri Lanka context layer.

Concrete first ticket:

1. Add a normalized `district_profiles` seed dataset with district, province, population, household count, density, and source keys.
2. Add census/weather/river source registry rows.
3. Replace static `AREA_BASE` values with derived `source`, `transport`, `weather`, and `density` components where data exists.
4. Add tests for `/life/atlas`, `/life/areas/score`, and source registry output.
5. Keep all missing data visibly low-confidence instead of inventing precision.

## Source Links

- Public APIs catalog: https://github.com/marcelscruz/public-apis
- Public APIs resources JSON: https://github.com/marcelscruz/public-apis/blob/main/db/resources.json
- Nuwan GitHub profile: https://github.com/nuuuwan
- `lk_census_2024`: https://github.com/nuuuwan/lk_census_2024
- `lanka_data`: https://github.com/nuuuwan/lanka_data
- `lk_weather_3h`: https://github.com/nuuuwan/lk_weather_3h
- `lk_rivers`: https://github.com/nuuuwan/lk_rivers
- `lk_tourism`: https://github.com/nuuuwan/lk_tourism
- `lk_fisheries`: https://github.com/nuuuwan/lk_fisheries
- `lk_food`: https://github.com/nuuuwan/lk_food
- `lk_acts`: https://github.com/nuuuwan/lk_acts
- `lk_hansard`: https://github.com/nuuuwan/lk_hansard
- `elections_lk`: https://github.com/nuuuwan/elections_lk
- `bus_routes_lk`: https://github.com/nuuuwan/bus_routes_lk
- `sl-vis`: https://github.com/nuuuwan/sl-vis
