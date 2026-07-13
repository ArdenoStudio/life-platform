# District Life Pulse — UI Redesign Spec

**Status:** Approved — implementation in progress  
**Date:** 2026-07-13  
**Branch:** `cursor/pulse-ui-redesign-ddb9`

## Problem

The MVP functional shell ships with a **marketing landing hero** (Aceternity motion, duplicate district controls, light cards on dark chrome). Users need an **operational signal desk** — calm, scannable, district-first.

## Design direction

| Principle | Implementation |
|-----------|----------------|
| Pulse-first | Cost of Life + 3 sisters above the fold |
| Context once | District / profile / locale only in `Shell` |
| Unified surfaces | `PulsePanel` glass on dark; `paper` tone for dense data |
| Status = color | Green/amber/red for health; gold for derived score |
| Motion minimal | No ambient beams on data panels; respect `prefers-reduced-motion` |
| Mobile desk | Compact header; sister row scroll; compare cards not wide tables |

## Typography

- **Manrope** — UI and metrics (`font-sans`)
- **Fraunces** — display wordmark only (`font-display`)
- Tabular nums for LKR values

## Page contracts

### Today (`page=today`)

1. Compact header: district · profile · freshness
2. `CostOfLifeHero` primary block
3. Food / Fuel / Shelter sister cards (equal grid)
4. `TrustStrip` (degradation + release)
5. Optional account bento when signed in (secondary)

### Cost / Places / Move / Decide / Trust

- Shared `PulsePanel` + `PulseKicker` headers
- No duplicate district/profile pickers (read-only context line + link to shell)

## Accessibility

- `min-h-11` touch targets on primary controls
- `aria-current="page"` on nav
- Shell search combobox pattern (phase 2)
- `lang` sync with locale

## Out of scope

- Full shadcn migration
- Light mode toggle
- Native apps

## Kill criteria alignment

Operational UI supports 60-day review: trust visible, sisters scannable, no misleading marketing copy on Today.
