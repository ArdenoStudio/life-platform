# Ariva District Life Pulse Revival — Implementation Plan

> **For agentic workers:** Implement phase-by-phase; check boxes as you go. Do not skip verification commands at phase boundaries.

**Goal:** Ship the 60-day MVP defined in [`docs/superpowers/specs/2026-07-13-ariva-revival-design.md`](../specs/2026-07-13-ariva-revival-design.md) — district-first Today briefing, three sister signals, one Cost of Life score, visible trust chrome, and platform deep links.

**Architecture:** Federated adapters (`backend/app/adapters/{food,fuel,property}.py`) → `LifeService.overview` (`backend/app/services/life_service.py`) → `/api/v1/life/overview` → `HomePage` (→ `TodayPage`) in the React shell. No mega-merge; MVP narrows aggregation and UI to food / fuel / shelter only.

**Tech stack:** FastAPI + SQLAlchemy (backend), React + TanStack Query + Vite (frontend), Playwright (E2E).

**Spec:** [`2026-07-13-ariva-revival-design.md`](../specs/2026-07-13-ariva-revival-design.md)

---

## Phase 1: MVP Today

**Target:** District Life Pulse as the primary Today surface — sticky district, three sisters, Cost of Life hero, trust strip, shell IA.

### Done / partial (as of 2026-07-13)

- [x] **Six-tab shell IA** — Today · Cost · Places · Move · Decide · Trust labels in [`frontend/src/components/Shell.tsx`](../../frontend/src/components/Shell.tsx) (`navItems`, i18n keys `today`, `cost`, `places`, …).
- [x] **Sticky home district (anonymous)** — URL `?district=` + `localStorage` via [`frontend/src/lib/format.ts`](../../frontend/src/lib/format.ts) (`HOME_DISTRICT_KEY`, `readStoredHomeDistrict`); district `<select>` in shell chrome [`Shell.tsx`](../../frontend/src/components/Shell.tsx).
- [x] **Overview API** — `GET /api/v1/life/overview` in [`backend/app/api/v1/endpoints/life.py`](../../backend/app/api/v1/endpoints/life.py), logic in [`backend/app/services/life_service.py`](../../backend/app/services/life_service.py) (`overview`).
- [x] **Three sister domains on Today** — food / fuel / property cards in [`frontend/src/pages/HomePage.tsx`](../../frontend/src/pages/HomePage.tsx) (`sisterDomainKeys`, links via `domain.homepage_url`).
- [x] **Cost of Life label (API)** — `survival_index.label == "Cost of Life"` in [`backend/app/schemas.py`](../../backend/app/schemas.py); asserted in [`backend/tests/test_life_api.py`](../../backend/tests/test_life_api.py).
- [x] **Source release on Today** — release badge in [`HomePage.tsx`](../../frontend/src/pages/HomePage.tsx); public endpoint consumed via [`frontend/src/lib/api.ts`](../../frontend/src/lib/api.ts) → `getSourceRelease`.
- [x] **Trust tab (MVP subset exists)** — [`frontend/src/pages/SourcesPage.tsx`](../../frontend/src/pages/SourcesPage.tsx): registry, validation, release card, source-class glossary.
- [x] **Move surface** — [`frontend/src/pages/MovePage.tsx`](../../frontend/src/pages/MovePage.tsx): transport fares, fuel/cost teaser.
- [x] **Decide surface (baseline)** — [`frontend/src/pages/ComparePage.tsx`](../../frontend/src/pages/ComparePage.tsx): district affordability compare.
- [x] **Auth district save** — `PUT /me/profile` + save CTA on Today via [`frontend/src/App.tsx`](../../frontend/src/App.tsx) (`saveProfileMutation`, `updateMeProfile`).
- [x] **Life pulse aggregate** — `GET /me/life-pulse` ([`backend/app/api/v1/endpoints/me.py`](../../backend/app/api/v1/endpoints/me.py)); rendered on Today when signed in.
- [x] **Federated adapters** — [`backend/app/adapters/food.py`](../../backend/app/adapters/food.py), [`fuel.py`](../../backend/app/adapters/fuel.py), [`property.py`](../../backend/app/adapters/property.py).

### Remaining Phase 1 tasks

- [ ] **Align `localStorage` key with spec** — Rename `ariva-home-district` → `ariva.homeDistrict` in [`frontend/src/lib/format.ts`](../../frontend/src/lib/format.ts); migrate read path for one release.
- [ ] **URL alias `page=today`** — Map `today` → `home` in [`frontend/src/App.tsx`](../../frontend/src/App.tsx) `readInitialParams` / `validPages`; emit `today` in URL when on Today (spec URL contract).
- [ ] **Auth district precedence** — On sign-in, override local district from `lifePulse.profile.district` in [`frontend/src/App.tsx`](../../frontend/src/App.tsx); write-back on profile save (spec precedence chain).
- [ ] **Extract trust chrome components** (spec appendix):
  - [ ] `frontend/src/components/DistrictChip.tsx` — thin wrapper around shell district control (or delegate from `Shell.tsx`).
  - [ ] `frontend/src/components/SourceClassPill.tsx` — extend [`SourcePill.tsx`](../../frontend/src/components/SourcePill.tsx) pattern.
  - [ ] `frontend/src/components/FreshnessLabel.tsx` — `observed_at` + `freshness_note`.
  - [ ] `frontend/src/components/SisterSignalCard.tsx` — status, headline, metrics, trust pills, deep link.
  - [ ] `frontend/src/components/DeepLinkButton.tsx` — platform exit + `utm_campaign=ariva_life_pulse`.
  - [ ] `frontend/src/components/TrustStrip.tsx` — release key + district degradation banner.
  - [ ] `frontend/src/components/CostOfLifeHero.tsx` — index, direction chip, derived badge, weight teaser.
- [ ] **Rename / narrow Today page** — Refactor [`HomePage.tsx`](../../frontend/src/pages/HomePage.tsx) → `TodayPage.tsx`; demote multi-domain hero (vehicles, utilities, weather, retail, top movers grid) to secondary tabs or remove from Today.
- [ ] **MVP overview contract (backend)** — In [`life_service.py`](../../backend/app/services/life_service.py) `overview`:
  - [ ] Headline mentions food / fuel / shelter only (not vehicles).
  - [ ] Add optional `sister_domains` filter or document that clients slice `domains` to `food|fuel|property`.
  - [ ] Expose direction vs prior snapshot on `survival_index` (field + migration if persisted in `life_index_snapshots`).
- [ ] **Degradation banner** — When any sister `status !== 'healthy'`, show district strip on Today (spec: *"Some signals are degraded; labels preserved."*); wire from `overview.source_health` or per-domain status in [`TodayPage`](../../frontend/src/pages/HomePage.tsx).
- [ ] **Deep links with UTM** — Build platform URLs in adapters or a small `frontend/src/lib/deepLinks.ts`; replace raw `homepage_url` anchors in sister cards.
- [ ] **i18n shelter label** — UI “Shelter” / API `property` keys in [`frontend/src/i18n.ts`](../../frontend/src/i18n.ts) (`sisterShelter` exists; audit copy).
- [ ] **Frontend tests** — Update [`frontend/src/App.test.tsx`](../../frontend/src/App.test.tsx) for Today-only sister layout and trust chrome presence.

### Phase 1 verification

```bash
# Backend unit tests
cd backend && python -m pytest tests/test_life_api.py -q

# Smoke: overview returns Cost of Life + sisters
cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8090 &
curl -s "http://127.0.0.1:8090/api/v1/life/overview?district=Colombo&profile=family" | python -m json.tool | head -80

# Frontend unit tests + lint
cd frontend && npm run lint && npm run test

# Manual: Today shows 3 sisters, district persists across reload, Trust tab loads release card
cd frontend && npm run dev
# Open http://127.0.0.1:5173/?page=today&district=Kandy&profile=family
```

**Phase 1 exit criteria:** Today page composes extracted components; only food / fuel / shelter are sister cards; degradation banner visible when mocked degraded; `page=today` works; profile district overrides storage on auth.

---

## Phase 2: Cost / Trust refinement

**Target:** MVP Cost of Life weights (45% / 20% / 35%), derived confidence, Cost tab trim, Trust governance surfaced to users.

### Tasks

- [ ] **MVP affordability weights** — In [`life_service.py`](../../backend/app/services/life_service.py) `affordability_from_signals` / new `mvp_cost_of_life`:
  - Food 45%, fuel 20%, shelter 35% only; exclude utilities, transport, vehicle, health from **headline** `survival_index` total.
  - Document weights in response (`breakdown` + `derived` source class).
- [ ] **Persist derived snapshot** — Write `life_index_snapshots` with input pointers to sister `domain_snapshots` (see [`backend/app/db/models.py`](../../backend/app/db/models.py)); link in Trust manifest.
- [ ] **Cost tab trim** — [`frontend/src/pages/CostOSPage.tsx`](../../frontend/src/pages/CostOSPage.tsx): sparkline/history for district + profile; weight breakdown (3 inputs); link to Trust methodology; hide non-MVP line items from hero (detail section OK).
- [ ] **Places tab shelter-forward** — [`frontend/src/pages/AtlasPage.tsx`](../../frontend/src/pages/AtlasPage.tsx): elevate shelter sister; PropertyLK deep link per spec.
- [ ] **Decide flow (MVP)** — [`ComparePage.tsx`](../../frontend/src/pages/ComparePage.tsx): max 2 districts; Cost of Life delta + sister signal deltas (not generic domain metric pickers); share URL `?page=decide&district=A&compare=B&profile=…`.
- [ ] **Trust tab filter** — [`SourcesPage.tsx`](../../frontend/src/pages/SourcesPage.tsx): filter registry to food / fuel / property + derived Cost manifest; Cost derivation expandable section.
- [ ] **Adapter platform URLs** — Ensure [`food.py`](../../backend/app/adapters/food.py), [`fuel.py`](../../backend/app/adapters/fuel.py), [`property.py`](../../backend/app/adapters/property.py) expose district-scoped `platform_url` / `homepage_url` for deep links.
- [ ] **Derived confidence** — When any sister degraded/offline, lower `survival_index.confidence` and surface in `CostOfLifeHero`.
- [ ] **Backend contract tests** — Extend [`backend/tests/test_life_api.py`](../../backend/tests/test_life_api.py):
  - MVP breakdown keys ⊆ `{food, fuel, property}` for headline score.
  - Weights sum to 100%.
  - Degraded fuel → `confidence` drops + status preserved in `domains`.

### Phase 2 verification

```bash
cd backend && python -m pytest tests/test_life_api.py -k "overview or affordability or survival" -q

# Affordability detail
curl -s "http://127.0.0.1:8090/api/v1/life/affordability?district=Colombo&profile=family" | python -m json.tool

# Cost command still serves Cost tab
curl -s "http://127.0.0.1:8090/api/v1/life/cost-command?district=Colombo&profile=family&locale=en" | python -m json.tool | head -40

# Source release for Trust
curl -s "http://127.0.0.1:8090/api/v1/life/source-release" | python -m json.tool

cd frontend && npm run test -- --run src/App.test.tsx
```

**Phase 2 exit criteria:** Headline Cost of Life uses 3-input weights; Cost and Trust pages document derivation; Decide compares two districts with sister deltas; degraded-input behaviour covered by tests.

---

## Phase 3: E2E and ops

**Target:** Automated smoke for Life Pulse IA, analytics hooks, kill-criteria observability, runbooks.

### Tasks

- [ ] **Playwright Life Pulse suite** — Extend [`frontend/tests/e2e/life-dashboard.spec.ts`](../../frontend/tests/e2e/life-dashboard.spec.ts):
  - Today: three sister labels (Food / Fuel / Shelter), Cost of Life hero, trust strip.
  - District change updates URL and refetches overview.
  - Deep link click opens new tab (mock or `page.context().waitForEvent('popup')`).
  - Decide two-district compare; Move teaser link.
  - Degraded state: banner visible (use test mock or fixture API).
- [ ] **Analytics events** — Implement spec events in a thin [`frontend/src/lib/analytics.ts`](../../frontend/src/lib/analytics.ts) (stub to `window.gtag` or console in dev):
  - `pulse.today_view`, `pulse.district_change`, `pulse.sister_expand`, `pulse.deep_link_click`, `pulse.cost_detail_view`, `pulse.trust_view`, `pulse.compare_run`.
  - Fire from `TodayPage`, `Shell`, `SisterSignalCard`, `DeepLinkButton`, `CostOSPage`, `SourcesPage`, `ComparePage`.
- [ ] **Link rot check script** — Add `scripts/check-deep-links.mjs` (Node stdlib): HEAD request sister `platform_url` samples; fail CI if >10% broken (align with kill criteria).
- [ ] **Kill-criteria telemetry doc** — Section in [`docs/verification.md`](../../docs/verification.md) mapping spec thresholds to queries (`integration_runs`, overview p95, UI audit checklist).
- [ ] **CI wiring** — Ensure [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) runs updated E2E against live backend (pattern already uses `npm run test:e2e`).
- [ ] **Operator path unchanged** — Confirm `/?page=operator` still gated ([`frontend/src/pages/OperatorPage.tsx`](../../frontend/src/pages/OperatorPage.tsx)); no MVP leakage.

### Phase 3 verification

```bash
# Full backend suite
cd backend && python -m pytest -q

# E2E (backend on 8090, frontend on 3001 per docs/verification.md)
cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8090 &
cd frontend && npm run build && npm run preview -- --host 127.0.0.1 --port 3001 &
LIFE_E2E_BASE_URL=http://127.0.0.1:3001 npm run test:e2e

# Deep link rot (after script exists)
node scripts/check-deep-links.mjs

# Production smoke checklist — see docs/verification.md
curl -s "$DEPLOYED_API/api/v1/life/overview?district=Colombo" | python -m json.tool | head -20
curl -s "$DEPLOYED_API/api/v1/life/source-release" | python -m json.tool
```

**Phase 3 exit criteria:** E2E covers Today + Trust + Decide; analytics events fire in dev console; deep-link script runs in CI; verification doc updated for 60-day kill review (2026-09-11).

---

## File map (quick reference)

| Area | Primary files |
|------|----------------|
| Spec | `docs/superpowers/specs/2026-07-13-ariva-revival-design.md` |
| Overview API | `backend/app/services/life_service.py`, `backend/app/api/v1/endpoints/life.py` |
| Schemas | `backend/app/schemas.py` |
| Adapters | `backend/app/adapters/{food,fuel,property}.py` |
| Shell / routing | `frontend/src/App.tsx`, `frontend/src/components/Shell.tsx` |
| Today UI | `frontend/src/pages/HomePage.tsx` → `TodayPage.tsx` |
| Cost / Trust / Decide | `CostOSPage.tsx`, `SourcesPage.tsx`, `ComparePage.tsx`, `AtlasPage.tsx`, `MovePage.tsx` |
| API client | `frontend/src/lib/api.ts` |
| Tests | `backend/tests/test_life_api.py`, `frontend/src/App.test.tsx`, `frontend/tests/e2e/life-dashboard.spec.ts` |
| Verification | `docs/verification.md` |

---

## Out of scope (do not implement in this plan)

Per spec: push/email alerts, fourth sister cards, mega-merge, HIES certification, native apps, operator self-serve console. See [Out of scope](../specs/2026-07-13-ariva-revival-design.md#out-of-scope) in the design doc.

---

## 60-day checkpoint

**Evaluation date:** 2026-09-11 — use kill criteria in the design spec (Adoption, Reliability, Trust, Product). Continuation requires ≥4 of 5 category groups passing.
