# Source Deep Research

Research date: 2026-05-28

This is the deeper evidence pack behind `docs/source-opportunity-map.md`. It looks at what the Life Platform can realistically become using the current Ariva architecture, the `marcelscruz/public-apis` catalog, the public `nuuuwan/*` Sri Lanka repositories, and Ardeno Studio's existing domain platforms.

## Current Product Reality

The local repo is already a good base for an industry-grade public intelligence product:

- FastAPI backend with domain adapters and source snapshots.
- Vite React frontend with public pages for home, cost, atlas, intelligence, and sources.
- Public-first behavior with optional Firebase accounts for saved items, alerts, notifications, and profile preferences.
- Existing source-of-truth domain adapters for FoodLK, Octane, PropertyLK, and AutoLens.
- Existing normalized tables for source registry, domain snapshots, tariff snapshots, retail offers, transport fares, area scores, public insights, account alerts, and notifications.

The gap is not "more UI." The gap is stronger source depth, normalized Sri Lanka context, proof-grade methodology, and an execution discipline that keeps the product honest.

## External Inventory

### `public-apis`

Current live fetches show:

- 52 API categories.
- 1,588 cataloged resources.
- 478 resources in categories relevant to Ariva: Weather, Currency Exchange, Geocoding, Government, Open Data, Transportation, Vehicle, Food and Drink, Health, News, Science and Math, and Environment.

Use `public-apis` as a shortlist and due-diligence source. Do not treat it as a trusted data source by itself. Every provider still needs a direct review for terms, limits, reliability, auth, CORS, freshness, and Sri Lanka coverage.

Best supporting providers to evaluate:

| Provider | Category | Life Platform use | Caveat |
| --- | --- | --- | --- |
| Open-Meteo | Weather | Public forecast context for district/risk panels | Non-commercial terms need review before production/commercial use. |
| OpenWeatherMap | Weather | Backup paid weather source | API key and pricing dependency. |
| Data Commons | Weather/Open Data | Disaster and macro context | Requires careful coverage validation for Sri Lanka. |
| Currency-api | Currency Exchange | LKR import-cost and vehicle sensitivity | Check maintenance and cache policy. |
| ExchangeRate-API | Currency Exchange | Backup FX source | API key and free-tier limits. |
| Open Food Facts | Food | Packaged-product metadata | Not a local price source. |
| OpenAQ | Environment | Air-quality context | Sri Lanka station coverage must be verified. |
| BigDataCloud / Geoapify | Geocoding | Reverse geocoding and address enrichment | API limits and privacy review required. |
| OpenStreetMap/Nominatim | Geocoding | Base geography and place context | Must respect usage policy; do not hammer public endpoints. |
| World Bank | Science and Math | Macro context and comparison lines | Not local enough for daily pricing. |
| NHTSA / vehicle metadata APIs | Vehicle | Vehicle make/model/spec enrichment | Does not replace AutoLens local market truth. |

### Nuwan Sri Lanka Repos

Authenticated GitHub metadata on 2026-05-28 showed:

- 377 public repositories.
- 299 repositories with MIT license metadata.
- 78 repositories without license metadata and requiring manual review before reuse.
- Language mix: Python 215, JavaScript 64, HTML 14, TeX 3, CSS 1, BibTeX Style 1, and 79 without language metadata.

High-value clusters from the live repo inventory:

| Cluster | Matched repos | Examples |
| --- | ---: | --- |
| Census, maps, addressing, district data | 33 | `lk_census_2024`, `lanka_data`, `lanka_data_timeseries`, `geo-data`, `address_lk`, `sl-vis`, `sl-maps` |
| Weather, rivers, risk | 10 | `lk_weather_3h`, `weather_lk`, `lk_rivers`, `lk_dmc_vis`, `lk_irrigation` |
| Tourism and travel | 7 | `lk_tourism`, `lk_air_travel`, `tourism_lk`, `lk_tourism_2025` |
| Food and fisheries | 3 | `lk_food`, `lk_fisheries`, `food` |
| Civic, law, parliament, elections | 24 | `lk_hansard`, `lk_acts`, `lk_acts_data`, `parliament_lk`, `elections_lk`, `lg_election_lk_2025` |
| Mobility and transport | 9 | `transport_timetable_lk`, `bus_routes_lk`, `lk_train_scheduler`, `fuel_lk` |
| News and public text | 13 | `lk_news`, `news_long_lk`, `news_lk3_data`, `news_lk_digest` |
| Document/report infrastructure | 16 | `lk_hansard`, `lk_acts`, `census_lk_pdf_parser`, `pdf2html`, `nopdf` |

The strongest takeaway: this is not mainly a set of apps to copy. It is a Sri Lanka public-data corpus and extraction toolkit that can make Ariva's data layer much more credible.

## Evidence From Priority Repos

| Source | Evidence found | Product meaning |
| --- | --- | --- |
| `lk_census_2024` | Includes original DCS source documents and extracted PDF tables. The README shows district/province/DSD data, population, sex/age, ethnicity, religion, housing structure, cooking fuel, drinking water, and validation warnings. | Replace static district assumptions with sourced district profiles and confidence flags. |
| `lanka_data` | Provides a query interface over Sri Lanka data with Census 2012, Census 2024, DCS, and Election Commission sources. Example output includes region id, name, type, area, center lat/lng, source, and source URL. | Best candidate for normalized geography and district metadata. |
| `lk_weather_3h` | Scrapes and stores Department of Meteorology 3-hourly reports, with station-level rain, temperature, and humidity examples. | Add weather pressure, rain watch, and district risk cards. |
| `lk_tourism` | Two datasets, 176 documents, 468.7 MB. Weekly tourist arrival reports from 2023-01-01 to 2026-05-01 and monthly reports from 2015-01-01 to 2026-04-01, sourced from SLTDA. | Tourism demand layer for districts, hotels, restaurants, tour operators, and SMB campaigns. |
| `lk_fisheries` | Four datasets, 457 documents, 104.1 MB. Includes fisheries annual statistics and monthly fish production reports sourced from fisheries.gov.lk. | Food supply pressure and fish-price explainers beyond retail price snapshots. |
| `lk_food` | Food-for-Sri-Lanka toolkit with scraped food items, nutrient data, cost tables, and a Bath Packet Index example. README showed 3,854 scraped items at fetch time. | Nutrition-aware affordability: "cheapest calories" is not enough; compare protein, meal baskets, and substitutions. |
| `lk_hansard` | Three datasets, 247 documents, 3.3 GB. 2020s Hansards include 227 documents from 2023-11-17 to 2026-05-19, in Sinhala, Tamil, and English. | Public document intelligence, policy explainers, and searchable civic context. |
| `lk_acts` / `lk_acts_data` | Public Sri Lanka acts metadata and PDFs from parliament sources. | Legal/policy document search, with strict "not legal advice" framing. |
| `elections_lk` | Python library for Sri Lankan elections data, MIT license metadata. | Civic/district context and election history overlays. |
| `bus_routes_lk` / `transport_timetable_lk` | Bus-route and timetable source candidates. | Commute scoring and transport planning context. |
| `sl-vis` / `sl-maps` | Sri Lanka map React components and map assets, some without license metadata. | Useful design/reference candidates, but license must be reviewed before reuse. |

## Product Brainstorm

### 1. District Atlas v2

Turn the Atlas page into the clearest Sri Lanka-local product surface.

Capabilities:

- District profile: province, population, households, area, density, center point, source.
- Life score: affordability, food, rent, transport, utility, weather/risk, and source coverage.
- Confidence panel: official, platform, derived, and low-confidence assumptions separated.
- Public heat panels: compare districts without login.
- Shareable district report URLs.

Why it is first:

- It upgrades visible product quality fast.
- It fits the existing `AreaScoreAdapter`, `AtlasResponse`, and source registry.
- It creates reusable context for FoodLK, AutoLens, PropertyLK, Dinaya, and tourism products.

### 2. Weather and Risk Watch

Make weather/risk a real domain, not an incidental insight.

Capabilities:

- Station-to-district weather mapping.
- Rain, heat, humidity, and river-pressure indicators.
- Saved-district in-app alerts.
- Business-facing "weather may affect demand/supply" signals.

Sources:

- `lk_weather_3h`, `weather_lk`, `lk_rivers`, `lk_irrigation`, `lk_dmc_vis`.
- Open-Meteo or OpenWeatherMap as supplemental forecast providers after terms review.

### 3. Food, Nutrition, and Supply Intelligence

Move from price-only to meal-affordability intelligence.

Capabilities:

- Essentials basket plus protein basket.
- Bath Packet Index style local meal estimate.
- Substitution suggestions when specific items move.
- Fish production/supply context next to fish price changes.
- Packaged-product metadata where useful.

Sources:

- FoodLK remains live market source.
- `lk_food` adds nutrition and meal index logic.
- `lk_fisheries` adds fish-supply reporting.
- Open Food Facts can enrich packaged-product metadata, not local price truth.

### 4. Tourism and SMB Demand Layer

Build a business-grade module for tourism SMBs.

Capabilities:

- Arrival trend dashboard.
- District-level demand context.
- Hotel/restaurant/transport opportunity signals.
- "This week/month in tourism demand" digest.
- Future paid report exports for businesses.

Sources:

- `lk_tourism`, `lk_air_travel`, `tourism_lk`, SLTDA originals.
- Existing Ardeno agency/product ecosystem for SMB packaging.

### 5. Public Document Intelligence

Create a source-linked civic intelligence surface.

Capabilities:

- Search acts, Hansards, tourism/fisheries reports, and selected government PDFs.
- Plain-English summaries with source links.
- Timeline of policy/report updates by domain.
- Strict disclaimers for law, finance, and health-adjacent content.

Implementation rule:

- Start with metadata and summaries.
- Do not dump multi-GB corpora into the app database.
- Use a separate search/index pipeline before adding a full UI.

### 6. Public APIs as Context Fillers

Use global APIs only where local data is missing:

- FX for import-cost sensitivity.
- Geocoding for place normalization.
- Weather forecast for forward-looking alerts.
- Air quality if coverage is real.
- World Bank macro context for long-term charts.

They should never override local official/platform truth.

## Best Commercial Angles

| Segment | Free public value | Paid/pro value |
| --- | --- | --- |
| Citizens and families | District life scores, daily cost desk, public alerts | Personal watchlists, richer alert history, report export later |
| Tourism SMBs | Public tourism trend summaries | Demand reports, district opportunity signals, weekly email/WhatsApp digest |
| Retail/food businesses | Food basket movement and public supply notes | Item/category tracking, competitor area reports, exportable insights |
| Property and vehicle buyers | District affordability, commute, fuel, and risk context | Saved comparisons, alerts, PDF buyer reports |
| Media/research users | Public source registry and explainers | Data/API access, archive search, report packs |
| Ardeno Studio | Proof-led data platform showcase | Lead magnet for custom portals and Sri Lanka-local dashboards |

## Industry-Grade Constraints

These are non-negotiable if the product is going to feel serious:

- Show source, freshness, confidence, and caveat for every derived number.
- Separate official, platform, retail, derived, and third-party API sources.
- Keep internal source lineage even if user-facing labels are simplified.
- Do not copy code/data from repos without license review.
- Do not make official-status, legal-advice, financial-advice, or first-of-kind claims.
- Keep auth additive: public product must work without login.
- Use background ingestion and cache live providers. Never make a public page depend on a fragile external call.
- Build a data-quality dashboard before adding too many datasets.

## Recommended Priority Order

1. Source Registry Upgrade: add reviewed source rows for census, weather, rivers, tourism, fisheries, Central Bank, DMC, irrigation, and civic documents.
2. District Profile Seed: normalized district/province/population/household/area/center data from sourced rows.
3. District Atlas v2: use district profile and weather/risk signals in score components.
4. Weather/Risk Domain: station/rain/river snapshots plus saved-district alerts.
5. Food/Nutrition Domain Upgrade: protein basket, meal index, substitutions, fisheries context.
6. Tourism Demand Module: arrivals, monthly/weekly movement, SMB opportunity notes.
7. Public Document Index: metadata, summaries, search, and source links.
8. Pro Packaging: reports, saved watchlists, digests, and API access.

## Source Links

- Public APIs catalog: https://github.com/marcelscruz/public-apis
- Public APIs categories JSON: https://raw.githubusercontent.com/marcelscruz/public-apis/main/db/categories.json
- Public APIs resources JSON: https://raw.githubusercontent.com/marcelscruz/public-apis/main/db/resources.json
- Nuwan GitHub profile: https://github.com/nuuuwan
- `lk_census_2024`: https://github.com/nuuuwan/lk_census_2024
- `lanka_data`: https://github.com/nuuuwan/lanka_data
- `lk_weather_3h`: https://github.com/nuuuwan/lk_weather_3h
- `lk_tourism`: https://github.com/nuuuwan/lk_tourism
- `lk_fisheries`: https://github.com/nuuuwan/lk_fisheries
- `lk_food`: https://github.com/nuuuwan/lk_food
- `lk_hansard`: https://github.com/nuuuwan/lk_hansard
- `lk_acts`: https://github.com/nuuuwan/lk_acts
- `elections_lk`: https://github.com/nuuuwan/elections_lk
- `bus_routes_lk`: https://github.com/nuuuwan/bus_routes_lk
- `sl-vis`: https://github.com/nuuuwan/sl-vis
- `address_lk`: https://github.com/nuuuwan/address_lk
