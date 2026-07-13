# Ariva District Life Pulse Revival — Design Spec

**Status:** Approved — implementation in progress (2026-07-13)  
**Date:** 2026-07-13  
**Owner:** Ariva product  
**Supersedes:** [2026-07-11 park decision](#chronicle-supersession-of-2026-07-11-park-decision)

---

## Summary

Ariva District Life Pulse is a **district-first daily briefing** for Sri Lanka living costs. The revival narrows scope to one sticky home district, three sister domain signals (food, fuel, shelter/property), a single Cost of Life score, visible trust chrome, and deep links into source platforms. It does not merge upstream systems into a mega-dataset; it federates adapters over FoodLK, Octane, and PropertyLK public APIs.

The product promise: *“What changed in my district today, and can I trust it?”*

---

## Problem

Users need a fast, honest read on daily living pressure in **their** district—not a national dashboard that buries locality under breadth. Prior Ariva work spread signal across many domains (vehicles, utilities, retail, weather, transport) before proving a tight daily habit loop. District Life Pulse revival tests whether a **minimal sister-signal desk** with explicit provenance earns repeat visits.

---

## Goals

| Goal | Success signal |
|------|----------------|
| District stickiness | ≥60% of returning sessions use the same home district within 7 days |
| Signal clarity | Users can name food, fuel, and shelter status without opening sub-pages |
| Trust visibility | Every headline metric shows source class, freshness, and degradation state |
| Federation integrity | No raw listing merge; deep links resolve to FoodLK / Octane / PropertyLK |
| Decision speed | Cost of Life score loads in one overview call with sister signals |

## Non-goals (MVP)

See [Out of scope](#out-of-scope).

---

## MVP Definition

### 1. Sticky home district

- User selects or confirms a **home district** (25 Sri Lanka districts + “Sri Lanka” national fallback).
- District persists in:
  - **Anonymous:** URL query `?district=…` and `localStorage` key `ariva.homeDistrict`.
  - **Authenticated:** `user_profiles.district` overrides local storage on sign-in; write-back on change.
- **Today** page always opens on home district; other IA tabs inherit district context unless explicitly overridden.
- District chip is persistent in shell chrome (not buried in filters).

### 2. Three sister signals

Each sister signal is a normalized `DomainSignal` from an existing federated adapter. MVP surfaces exactly three:

| Sister | Adapter upstream | Primary headline | Secondary line |
|--------|------------------|------------------|----------------|
| **Food** | FoodLK | Basket pressure / staple move | Freshness + confidence pill |
| **Fuel** | Octane | Pump reference move (petrol/diesel) | Last official check time |
| **Shelter** | PropertyLK | Rent / listing pressure index | Market breadth note |

**Rules:**

- Sister cards show **status** (`live`, `degraded`, `offline`) with no silent substitution.
- Degraded/offline states use fixture-backed structure already in adapters; UI must label fallback.
- No fourth sister card on Today in MVP (vehicles, utilities, weather, transport stay deep-link only).

### 3. One Cost of Life score

- Single composite score for the active district + household profile (`single` | `family` | `commuter`).
- Derived from weighted food, fuel, and shelter inputs only in MVP—utilities, transport, health, and vehicle components are **excluded from the headline score** but may appear in Cost tab detail.
- Score carries:
  - Numeric index (district-relative baseline = 100)
  - Direction chip (↑ / ↓ / → vs prior snapshot)
  - `derived` source class with expandable weight breakdown
- Served from existing affordability pipeline narrowed to MVP basket weights (see [Data model](#data-model)).

### 4. Trust chrome

Trust chrome is **always visible** on Today and on any surface showing a sister signal or Cost of Life score.

**Required elements per metric:**

1. **Source class** — `official` | `platform` | `retail` | `derived`
2. **Freshness** — observed timestamp + human note (“checked 2h ago”, “scheduled refresh”)
3. **Confidence** — `high` | `medium` | `low`
4. **Degradation banner** — when any sister is non-`live`, show district-level strip: *“Some signals are degraded; labels preserved.”*

**Trust entry point:**

- Shell nav includes **Trust** tab → source registry subset for the three sisters + Cost derivation manifest.
- Link to `/life/source-release` public metadata (release key, source keys, seed-fallback flag) without exposing operator artifacts.

### 5. Deep links

Every sister card and Cost breakdown row includes **“View on {platform}”** deep links:

| Sister | Deep link target |
|--------|------------------|
| Food | FoodLK search / category URL with district query params |
| Fuel | Octane station / price board URL |
| Shelter | PropertyLK district listings URL |

**Rules:**

- Deep links open in new tab; UTM params identify `ariva_life_pulse` campaign.
- Ariva does not iframe upstream UIs in MVP.
- Search results and saved items store platform URL + external id, not copied listing bodies.

---

## Information Architecture

Primary nav (6 tabs):

```
Today · Cost · Places · Move · Decide · Trust
```

### Today

**Purpose:** Daily district briefing—the Life Pulse surface.

**Contents:**

- Home district selector (sticky)
- Cost of Life score hero
- Three sister signal cards (food, fuel, shelter)
- Trust strip (release key, degradation state)
- Optional authenticated block: saved profile, unread notifications count, “Save this district” CTA

**Maps from current:** `home` page, narrowed.

### Cost

**Purpose:** Inspect the Cost of Life score and monthly basket mechanics.

**Contents:**

- Score history sparkline (district + profile)
- Weight breakdown (food / fuel / shelter only in MVP)
- Link to full affordability methodology in Trust

**Maps from current:** `cost` / CostOS page, trimmed.

### Places

**Purpose:** District context for shelter and neighborhood pressure.

**Contents:**

- District atlas panel (scores, highlights)
- Shelter sister expanded
- Deep link to PropertyLK district explorer

**Maps from current:** `atlas` page, shelter-forward.

### Move

**Purpose:** Mobility and relocation **signals**, not a trip planner.

**Contents:**

- District pair fare hints (public transport + fuel-only private estimate)
- “Compare district” teaser → Decide
- Deep links to Octane / transport sources
- **Not** a sister card in MVP; secondary surface only

**Maps from current:** partial `intelligence` + transport endpoints.

### Decide

**Purpose:** Lightweight choice support—stay vs move, profile toggle.

**Contents:**

- Side-by-side district comparison (max 2 districts)
- Cost of Life delta
- Sister signal deltas
- Export/share deep link `?page=decide&district=A&compare=B&profile=family`

**Maps from current:** `compare` / affordability compare patterns.

### Trust

**Purpose:** Source governance and user-facing provenance.

**Contents:**

- Source registry filtered to MVP domains
- Active release card (`/life/source-release`)
- Confidence / freshness glossary
- Operator-only content remains unlisted at `/?page=operator`

**Maps from current:** `sources` page, focused.

### URL contract

```
/?page=today&district=Colombo&profile=family&locale=en
/?page=cost&district=Kandy&profile=single
/?page=places&district=Galle
/?page=move&district=Colombo
/?page=decide&district=Colombo&compare=Kandy&profile=family
/?page=trust
```

`today` remains alias for `home` during transition.

---

## User Flows

### Anonymous daily check

1. Land on Today with Colombo default (or last `localStorage` district).
2. See Cost of Life score + three sisters + trust chrome.
3. Tap Fuel sister → deep link to Octane.
4. Change district → URL and storage update; overview refetch.

### Authenticated save district

1. Sign in (Firebase).
2. Confirm district → `PUT /me/profile` with `district`.
3. Life Pulse (`GET /me/life-pulse`) merges profile district, overview, notifications.
4. Alert rules optional post-MVP; MVP shows notifications list only.

### Degraded upstream

1. Octane timeout → fuel sister `degraded`, fixture structure, visible banner.
2. Cost of Life recalculates with labelled degraded inputs; derived confidence drops.
3. Trust tab explains which source failed and last successful snapshot.

---

## Architecture

### Principle: federated adapters, no mega-merge

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   FoodLK    │     │   Octane    │     │  PropertyLK  │
│  (source)   │     │  (source)   │     │   (source)   │
└──────┬──────┘     └──────┬──────┘     └──────┬───────┘
       │                   │                    │
       ▼                   ▼                    ▼
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│ food adapter│     │ fuel adapter│     │shelter adapter│
└──────┬──────┘     └──────┬──────┘     └──────┬───────┘
       │                   │                    │
       └───────────────────┼────────────────────┘
                           ▼
                  ┌─────────────────┐
                  │   LifeService   │
                  │  overview merge │
                  └────────┬────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
     ┌────────────┐ ┌────────────┐ ┌───────────────┐
     │  domain_   │ │ life_index_│ │ integration_  │
     │ snapshots  │ │ snapshots  │ │    runs       │
     └────────────┘ └────────────┘ └───────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Ariva API      │
                  │  /life/overview │
                  │  /me/life-pulse │
                  └────────┬────────┘
                           ▼
                  ┌─────────────────┐
                  │  District Life  │
                  │  Pulse UI       │
                  └─────────────────┘
```

**Hard rules:**

1. **No mega-merge table** of raw listings, offers, or quotes across platforms.
2. Adapters fetch upstream public APIs with timeout; fallback fixtures are per-domain, not cross-domain.
3. Normalized snapshots store **summaries** (metrics, highlights, timestamps)—not full catalog mirrors.
4. Cost of Life is a **derived snapshot** (`life_index_snapshots`) with explicit input pointers to sister snapshots.
5. Vehicle (AutoLens), utilities, weather, retail remain in codebase but **out of MVP overview aggregation**.

### API surface (MVP)

| Endpoint | Role |
|----------|------|
| `GET /life/overview?district&profile` | Today briefing: sisters + Cost of Life |
| `GET /life/affordability?district&profile` | Cost tab detail |
| `GET /life/source-release` | Trust release card |
| `GET /life/domains` | Sister metadata + platform URLs |
| `GET /me/life-pulse` | Authenticated Today enrichment |
| `GET /me/profile` / `PUT /me/profile` | Sticky district |

Internal operator endpoints unchanged; not user-facing in MVP.

### Caching and freshness

| Domain | Cache TTL | Language |
|--------|-----------|----------|
| Food | 6h | “Scheduled refresh” |
| Fuel | 1h | “Checked recently” |
| Shelter | 6h | “Market snapshot” |
| Cost of Life | On sister refresh | “Derived from labelled inputs” |

### Frontend composition

- Shell nav refactored to 6 IA labels; route keys versioned.
- `HomePage` → `TodayPage`: hero score + three sisters + trust strip.
- Shared `SisterSignalCard` component enforces trust chrome contract.
- `DeepLinkButton` component standardizes platform exits.

---

## Data Model

### MVP Cost of Life weights

| Input | Weight | Source |
|-------|--------|--------|
| Food sister metric | 45% | FoodLK adapter normalized basket pressure |
| Fuel sister metric | 20% | Octane adapter pump reference |
| Shelter sister metric | 35% | PropertyLK adapter rent pressure index |

Weights are **planning defaults**, labelled derived, not official statistics. Trust tab documents methodology and links to full HIES-informed weights as post-MVP roadmap.

### Sister signal schema (normalized)

Uses existing `DomainSignal` with MVP-required fields populated:

- `key`: `food` | `fuel` | `property` (shelter label in UI maps to `property` key)
- `status`: `live` | `degraded` | `offline`
- `headline`, `summary`, `metrics[]`, `freshness_note`, `confidence`, `source_class`
- `platform_url`: deep link target
- `observed_at`

### Sticky district precedence

```
authenticated profile.district
  → localStorage ariva.homeDistrict
    → URL ?district=
      → default "Colombo"
```

---

## Trust & Governance

- Personal account data **never** overrides source labels, confidence, or freshness notes.
- Degraded domains remain visible with status badges—no hiding failed sisters.
- `/life/source-validation` gates release promotion; MVP UI reads public release metadata only.
- Deep links must not pass PII in query strings.

---

## Chronicle: Supersession of 2026-07-11 Park Decision

### What was decided on 2026-07-11

On **2026-07-11**, the team **parked** District Life Pulse as a standalone daily product surface. Rationale recorded at that time:

1. **Breadth-first bet** — Ship the full Living Atlas (multi-domain overview, utilities, transport, weather, retail, vehicles) before proving a narrower daily loop.
2. **Engineering load** — Avoid parallel IA work while adapter coverage expanded across six+ domains.
3. **Risk reduction** — Defer sticky-district UX until district profile promotion pipeline (`source_data_releases`) reached production confidence.

That decision placed District Life Pulse in **maintenance-only** mode: `/me/life-pulse` remained as an authenticated aggregate of full overview, but there was no dedicated Today briefing, no three-sister constraint, and no Cost-of-Life-only score contract.

### Why this revival supersedes the park decision

Evidence shifted between 2026-07-11 and 2026-07-13:

| Factor | Jul 11 state | Jul 13 state |
|--------|--------------|--------------|
| Adapter maturity | Partial degradation across domains | Food, fuel, property adapters stable with labelled fallbacks |
| Release promotion | Operator-dependent | `source_data_releases` + public `/life/source-release` live |
| User feedback | “Too much dashboard” | Request for district daily pulse |
| Strategic fit | Atlas-first | Public-first **signal desk** aligns with federation model |

**Supersession ruling (2026-07-13):**

- **Resume** District Life Pulse as the **primary Today surface** with MVP scope defined in this spec.
- **Demote** full multi-domain hero on Today; other domains move to secondary tabs (Move, Cost detail) or post-MVP.
- **Retain** federated architecture—park decision’s implied “wait for mega-merge” path is **explicitly rejected**.
- **Time-box** revival to 60 days; failure triggers re-park or kill (see kill criteria).

### Document lineage

| Document | Disposition |
|----------|-------------|
| 2026-07-11 park decision (chat/decision log) | Superseded by this spec |
| `docs/architecture.md` | Still authoritative for runtime; MVP is a product subset |
| `docs/industry-standard-execution-plan.md` | Continues; MVP maps to Phase 1 signal-desk proof |

---

## 60-Day Kill Criteria

**Evaluation date:** 2026-09-11 (60 days from spec approval)

Revival **fails** and triggers **re-park or shutdown** if **any** of the following are true at evaluation:

### Adoption

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Weekly active district users | < 500 WAU | Analytics: unique clients with `overview` fetch + district != national |
| D7 return rate | < 15% | Users who hit Today on day 0 and return within 7 days |
| Sticky district rate | < 40% | Sessions using same district as first session in week |

### Reliability

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Sister live rate | < 85% uptime each | `integration_runs` success / total per adapter over 14-day window |
| Overview p95 latency | > 2.5s | API telemetry for `/life/overview` |
| Silent fallback incidents | > 0 | Any production incident where degraded data rendered without banner |

### Trust

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Trust chrome completeness | < 100% on sisters | UI audit + contract tests |
| Deep link rot | > 10% broken | Weekly link check to platform URLs |
| Source-release transparency | Missing on Today | Manual QA gate |

### Product

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Cost score comprehension | < 50% survey “understand score” | In-app micro-survey (n ≥ 100) |
| Deep link CTR | < 5% | Click-through to FoodLK/Octane/PropertyLK |

### Kill actions

1. **Re-park** — Today reverts to Atlas-wide hero; Life Pulse features hidden behind flag.
2. **Kill** — Remove MVP IA tabs; archive `TodayPage` sister layout; retain API adapters for other products.
3. **Post-mortem** — Required within 5 business days; publish learnings to `docs/superpowers/specs/`.

**Continuation rule:** If **≥ 4 of 5** category groups (Adoption, Reliability, Trust, Product, and at least one adoption metric) pass, revival continues to next phase.

---

## Out of Scope

The following are **explicitly excluded** from the 60-day MVP. They are not deferred bugs—they are intentional boundaries.

### Product

- Email, WhatsApp, push, or SMS notifications
- User-defined alert rules UI (backend may exist; no MVP surface)
- Vehicle / AutoLens as a sister signal
- Utilities, LPG, water, electricity as sister signals
- Weather and disaster risk on Today
- Retail offers and coupon surfaces
- National “Sri Lanka” as recommended home district (fallback only)
- In-app listing search across merged catalogs
- Iframed upstream platform experiences
- Sinhala/Tamil copy complete audit (locale keys exist; content parity not gated)
- Native mobile apps
- SEO/marketing landing pages beyond current shell

### Data & engineering

- Mega-merge of FoodLK + Octane + PropertyLK raw data into one table
- Scraping or copying upstream HTML parsers into Ariva
- New upstream sources beyond existing three sister adapters for MVP score
- Real-time WebSocket streaming (short-cache HTTP remains)
- HIES-grade statistical certification of Cost of Life score
- Automated DMC / emergency alert ingestion
- Public write APIs or crowdsourced price submission
- Multi-country expansion

### Operations

- Self-serve operator release console for non-operators
- SLA-backed uptime commitments
- Paid tiers, billing, or subscriptions

---

## Milestones (60 days)

| Week | Deliverable |
|------|-------------|
| 1 | IA shell (6 tabs), sticky district, URL contract |
| 2 | Today page: three sisters + trust chrome components |
| 3 | MVP Cost of Life weights + overview API contract frozen |
| 4 | Deep links + Trust tab release card |
| 5 | Decide compare flow + Move teaser |
| 6 | Auth profile district sync, life-pulse integration |
| 7 | QA: degradation banners, link rot checks, analytics events |
| 8 | Kill-criteria dashboard + evaluation prep |

---

## Analytics Events (MVP)

| Event | Properties |
|-------|------------|
| `pulse.today_view` | `district`, `profile`, `locale` |
| `pulse.district_change` | `from`, `to`, `auth` |
| `pulse.sister_expand` | `sister`, `status` |
| `pulse.deep_link_click` | `sister`, `platform` |
| `pulse.cost_detail_view` | `district`, `profile` |
| `pulse.trust_view` | `release_key` |
| `pulse.compare_run` | `district_a`, `district_b` |

---

## Open Questions

1. **Default district for first-time users** — IP geo is unreliable; keep Colombo or prompt district modal on first visit?
2. **Shelter label** — UI says “Shelter”; API key remains `property` for adapter compatibility. Document in i18n.
3. **Compare cap** — Two districts max in MVP; expand in Decide phase 2?
4. **Score baseline** — District baseline 100 vs national baseline 100 for index display.

---

## Appendix: Component Checklist

- [ ] `DistrictChip` — sticky shell control
- [ ] `CostOfLifeHero` — score + direction + derived badge
- [ ] `SisterSignalCard` × 3 — food, fuel, shelter
- [ ] `TrustStrip` — degradation + release key
- [ ] `DeepLinkButton` — platform exit
- [ ] `SourceClassPill` — official / platform / retail / derived
- [ ] `FreshnessLabel` — timestamp + note
- [ ] `TodayPage` — composes above
- [ ] Shell nav labels: Today · Cost · Places · Move · Decide · Trust

---

## References

- `docs/architecture.md` — federated adapter runtime
- `docs/source-roadmap.md` — affordability methodology context
- `docs/verification.md` — life-pulse and API smoke tests
- `GET /api/v1/life/overview` — current overview contract
- `GET /api/v1/me/life-pulse` — authenticated pulse aggregate
