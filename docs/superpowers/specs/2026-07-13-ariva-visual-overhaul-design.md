# Ariva Visual Overhaul — Ardeno Command Desk

**Status:** Implemented (Phase 1)  
**Date:** 2026-07-13  
**Branch:** `cursor/ariva-visual-overhaul-ddb9`

## Problem

The July 13 pulse desk work reorganized information architecture but preserved the original warm paper/gold glass aesthetic. Users and stakeholders expected a **visually distinct** federation product matching Octane, PropertyLK, Vehicle, and FoodLK quality — not rearranged dark glass.

Production at `life-platform.vercel.app` was also serving stale bundles, compounding the perception that nothing changed.

## Design direction: Ardeno Command Desk

A **true-black editorial terminal** that unifies sister platforms without cloning any single sister dialect:

| Token | Value | Rationale |
|-------|-------|-----------|
| Canvas | `#000000` + dot grid | PropertyLK-level contrast; removes warm gradient washes |
| Surface | `#0a0a0a` / `#111111` | Flat panels, no glass morphism |
| Foreground | `#fafafa` | High readability |
| Primary accent | Teal `#2dd4bf` | Ariva life identity; distinct from Octane amber / PropertyLK teal-dark |
| Domain accents | Food orange, Fuel amber, Shelter teal, Vehicle blue | Federation color bleed on sister rows |
| UI font | Inter | Matches modern sister stacks (Vehicle, PropertyLK) |
| Display font | Fraunces | Wordmark only |
| Metrics font | JetBrains Mono | Tabular nums on all scores |

## Key UI changes

1. **Shell** — Single slim sticky bar; pill navigation with teal active fill; "by Ardeno Studio" co-brand; no nested `floating-surface` glass header.
2. **Cost of Life hero** — Dominant mono score (`76/100` pattern from FoodLK); daily/monthly in flat elevated tiles.
3. **Sister signals** — Horizontal desk rows with left accent stripe (not 3-up glass cards).
4. **Mobile** — Sticky bottom metric bar (Octane pattern).
5. **Removed** — Ambient tri-color gradients, gold gradient brand mark, `backdrop-blur` glass panels, nested `pulseInnerCard` glass nesting.

## Sister platform references

- **Octane** — Light marketing hero, pill nav, price cards → adopted pill nav + mobile sticky bar
- **PropertyLK** — True black, teal, morphing nav → adopted black canvas + editorial contrast
- **Vehicle** — Geist/shadcn flat surfaces → adopted flat elevated panels
- **FoodLK** — Edition score hero, mono metrics → adopted dominant score display

## Out of scope (Phase 2)

- Per-page layout rewrites beyond token migration (Operator light panels remain)
- Backend Fly deploy / Vercel production redeploy (requires credentials)
- Full e2e Playwright pass on CI

## Success criteria

- [x] New CSS/JS bundle hashes in build (`index-DuVEBSpm.css`)
- [x] Today page visually distinct at a glance (black, teal, mono hero)
- [x] Frontend unit tests pass
- [ ] Production deploy reflects new assets
- [ ] User sign-off on visual direction

## Verification

```bash
cd frontend && npm run lint && npm run test && npm run build
```
