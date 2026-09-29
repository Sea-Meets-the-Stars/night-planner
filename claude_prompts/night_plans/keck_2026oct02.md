# Keck/LRIS Night Plan Prompts - October 2, 2026

Created by Lordrick and Claude

Prompts extracted from daily logs: 2026-09-09, 2026-09-10, 2026-09-11

---

## Session 1: 2026-09-09

### Prompt 1 — Initial Request
> use our night planner to make a night plan for Keck/LRIS on october 2nd

**Result:** First Keck plan, adapted from Lick/Kast scripts. Created `scripts/keck_2026oct02_calculations.py` and `scripts/build_keck_night_plan.py`. 4 targets from Lick pool observable.

### Prompt 2 — LRIS Modes + High-Dec Targets
> Also, we can do imaging with LRIS, and any target fainter than 21 mag needs a mask and we cant do long slit, add this to LRIS info and recommendations and query again. [Also add Lick-excluded high-Dec targets]

**Result:** Added LRIS mode documentation (longslit ≤21 mag, MOS >21 mag). Added FRB20250102C (Dec 84.1°, excluded from Lick). 6 targets, 2.6h science.

### Prompt 3 — Summary Document
> make a .md file for this update and log all our prompts

**Result:** Created `Night_plans/Keck-2026B-01/KECK_LRIS_2026OCT02_SUMMARY.md`

---

## Session 2: 2026-09-10

### Prompt 4 — Real Keck Constraints
> ok, I see here to generate these targets we adapted the Lick/Kast Scripts, we need to update first for Keck, we need targets fainter that 19 mag, unless it is very high dec above the Lick Limit, also read online about the Nasmyth Platform and vignetted region for Keck, LRIS is on Keck 1, so it has to wait for targets to rise, update the params specific to Keck and regenerate targets

**Result:**
- Implemented mag>19 filter (unless Dec>82°)
- Researched Keck I Nasmyth deck vignetting: az 5.3°-146.2° blocked below alt 33.3°
- Only 1 target survived real constraints (down from 6)

### Prompt 5 — Fresh FFFF-PZ Resource
> I think we need through the whole process of making a folder in chime_ffff_pz/data/Observing and name it Keck-2026B-01, make the resource json and generate targets

**Result:** Created Keck-specific FFFF-PZ resource with `min_mag=19.0`. Fresh 15-target pull. 4 longslit targets, 3.3h science.

### Prompt 6 — Regenerate Plan
> can you make a new night plan now
>
> [follow-up] I see 16 targets, why only four? also update all docs

**Result:** Documented full 15→4 target funnel (5 fail sky-observability, 6 need MOS masks).

### Prompt 7 — Real ETC
> How are you calculating exposure times? I fear our hand wavy Lick rules wont work here, we need an actual exposure time calculator

**Result:**
- Built `scripts/lris_etc.py` calling live etc.ucolick.org API
- Confirmed grism 600/4000 blue, grating 600/7500 red
- Target S/N=5 per pixel continuum
- Total science dropped from 3.3h to 0.6h (real LRIS is much faster than hand-wavy estimate)

### Prompt 8 — ETC Calibration
> I see FRB20250408A duration 52 mins, is that right?
>
> [follow-up] ok, the calculator must be wrong, which repo did you use, I see you need atleast 15mins for 21 mag, for one exposure, I would need atleast 3

**Result:**
- Bug: was computing combined S/N, not per-exposure S/N
- Fixed to S/N=10 per single exposure, minimum 3 exposures
- Science time rose from 0.6h to 2.3h (correct)

---

## Session 3: 2026-09-11

### Prompt 9 — MOS Exposure Rules
> New recommendation, always ask for masked targets for LRIS on the resource, and If we have any target fainter than 21 mag, even if it was pulled as longslit, we always need a mask, so add it as a masked target, you can put this in the info column, also, if a masked target is brigheter than 23 mag, we need just 1 hour and if fainter we may need 1.5 to 2 hours

**Result:**
- Added `info` column flagging mag>21 targets
- MOS exposure estimate: ≤23 mag → 1h, 23-24 mag → 1.5h, ≥24 mag → 2h
- Updated FFFF-PZ convention: always request masked targets

### Prompt 10 — Include MOS in Schedule
> why only 2, have you recorded the reason for rejecting other candidates?
>
> [follow-up] Even If it needs mask, I need it in the night plan with the allocated time
>
> [follow-up] yesm abd yodate our night time

**Result:**
- Changed scheduler to include MOS targets (flagged `[MASK REQUIRED]`)
- 5 targets now scheduled (2 longslit + 3 MOS)
- 4.4h/9.7h (45% utilization)

### Prompt 11 — Coordinate Verification
> Are you using proper coordinates and elevation for Keck?

**Result:**
- Verified against `astropy.coordinates.EarthLocation.of_site('keck')`
- Fixed latitude: 19.8263° → 19.828333° (was ~7 arcsec off)
- Lon/elevation were correct

---

## Key Lessons Learned

1. **Don't reuse another site's target pool** — Lick targets are biased toward high Dec; Keck needs its own FFFF-PZ query
2. **Research real telescope constraints** — Keck I Nasmyth deck vignetting is critical
3. **Use real ETCs** — Hand-wavy scaling from smaller telescopes is wrong by factors of 5-10x
4. **S/N per exposure, not combined** — Each sub-exposure needs full S/N for cosmic-ray rejection
5. **Minimum 3 exposures** — For cosmic-ray rejection regardless of S/N math
6. **Never trust upstream mode tags** — FFFF-PZ `mode` column doesn't match mag-based requirements
7. **Verify hardcoded constants** — Check site coordinates against canonical sources

---

## Final Configuration

- **Telescope:** Keck I
- **Instrument:** LRIS
- **Blue:** Grism 600/4000
- **Red:** Grating 600/7500, centered ~7200Å
- **Target S/N:** 10 per pixel continuum, per single exposure
- **Min exposures:** 3
- **MOS times:** mag ≤23 → 1h, 23-24 → 1.5h, ≥24 → 2h
