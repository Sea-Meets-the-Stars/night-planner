# Keck/LRIS Night Plan - October 6, 2026

Created by Lordrick and Claude (2026-09-09)

> **Date correction (2026-09-17):** the run is actually the night of **Oct 6**,
> not Oct 2 as originally planned in Prompts 1-11 below. See Prompt 12 for
> what changed and what didn't when the whole pipeline was rerun for the
> correct date.

> **Superseded (2026-09-30):** the current Oct 6 plan is built from the
> global FFFF-PZ **Keck-2026B-02** pull and lives in
> [`../Keck-2026B-02/`](../Keck-2026B-02/KECK_LRIS_2026OCT06_B02_SUMMARY.md).
> It has 9 targets (4 MOS, 5 longslit), a 10-min base slew, and +5 min per
> mask. Prompts 15-19 below explain how it got there. The Ephemeris section
> of this doc is still valid. The target, timeline and utilization sections
> are the Prompt 14 snapshot of the B-01 pool.

## Session Log

### Prompt 1
> use our night planner to make a night plan for Keck/LRIS on october 2nd

**Action:** Created Keck night planning infrastructure from scratch, adapting Lick/Kast scripts.

**Scripts created:**
- `scripts/keck_2026oct02_calculations.py` - ephemeris, target analysis, scheduling
- `scripts/build_keck_night_plan.py` - Excel generation

**Initial result:** 4 targets observable (high-Dec Lick targets poorly suited for Keck lat 20°)

---

### Prompt 2
> Do add Lick esc targets if they are greater than pointing limit of Lick, they will need short exposures.

**Action:** Added targets excluded from Lick (Dec > 82°) that are observable from Keck at higher airmass.

**Changes:**
- Relaxed airmass limit to 2.5 for bright targets (mag < 17)
- Added FRB20250102C (Dec 84°, mag 13.3) - only 11 min exposure
- Added FRB20200621B (Dec 59°, mag 16.9) - setting target

**Result:** 6 targets, 2.6h science time

---

### Prompt 3
> Also, we can do imaging with LRIS, and any target fainter than 21 mag needs a mask and we cant do long slit, add this to LRIS info and recommendations and query again.

**Action:** Added LRIS mode documentation and recommendations.

**LRIS Modes:**
- LONGSLIT: mag ≤ 21
- MOS: mag > 21 (requires pre-milled masks, weeks lead time)
- IMAGING: Available for backup/gap-filling

**Updates:**
- Added `lris_mode` column to target analysis
- Added recommendations section to output
- Updated `claudes_brain.md` with LRIS info

---

### Prompt 4
> make a .md file for this update and log all our prompts

**Action:** Created this summary document.

---

### Prompt 5
> to generate these targets we adapted the Lick/Kast Scripts, we need to update first for Keck, we need targets fainter that 19 mag, unless it is very high dec above the Lick Limit, also read online about the Nasmyth Platform and vignetted region for Keck, LRIS is on Keck 1, so it has to wait for targets to rise, update the params specific to Keck and regenerate targets

**Action:** Updated `scripts/keck_2026oct02_calculations.py` with two Keck-specific
corrections and regenerated all outputs.

**1. Target-selection rule (mag > 19 unless Dec > Lick limit):**
Keck's 10m aperture is wasted on targets Lick's 3m already handles. New rule:
keep a target only if `mag_r > 19.0`, unless `Dec > 82°` (Lick/Shane's pointing
limit, so unreachable from Lick regardless of magnitude). Implemented as
`passes_keck_target_selection()` / `KECK_MAG_FAINT_LIMIT = 19.0` /
`LICK_DEC_LIMIT = 82.0`, applied as a filter at the top of `analyze_targets()`.

**2. Keck I Nasmyth-deck vignetting (real limits, not the old generic alt<10°):**
Researched Keck's published telescope pointing limits
(www2.keck.hawaii.edu/inst/common/TelLimits.html). Keck I's Nasmyth deck
obstructs the beam in a **fixed azimuth band, az 5.3°-146.2°** (N through E to
SE) **unless altitude ≥ 33.3°**; outside that band the normal unvignetted
floor is ~18°. This is N/E for Keck I specifically (Keck II is blocked S/W —
the opposite side). Practical effect: a target **rising** in the NE/E sits in
this band at low altitude and must climb to 33.3° before it clears the deck —
confirms the "wait for target to rise" note above. A **setting** target in the
W/SW passes through the unobstructed side and can be tracked down to 18°, so
setting targets are easier to catch on Keck I. Implemented as
`check_keck1_nasmyth_vignetting(az, alt)`, folded into `check_keck_limits()`
(now takes `az` as well as `ha`/`alt`).

**Regenerated result:** Of the original 14 Lick-2026B-01 targets, only
**5 pass the mag>19-unless-high-Dec filter**: FRB20250102C (13.3, Dec 84°,
kept only via the Dec>82° exception), FRB20240901A (19.1), FRB20251003A
(16.4, Dec 85°, Dec exception), FRB20260215E (19.8), FRB20240324A (19.2). Of
those 5, only **FRB20250102C** clears both the HA ±5.5h limit and the Nasmyth
vignetting check — the other 4 are rejected (2 by Nasmyth-deck vignetting
while rising, 2 by the HA>+5.5h west limit). Night plan is now **1 target,
11 min, 2% utilization** — down from 6 targets / 2.6h in the previous version.

**Why so thin:** this target list was pulled for Lick, not Keck — combining
the mag>19 cut with the real Nasmyth constraint leaves almost nothing
observable from the Lick-2026B-01 pool. The right fix is a fresh FFFF-PZ query
tuned for Keck (see updated recommendations below), not a workaround in the
scheduler.

---

### Prompt 6
> I think we need through the whole process of making a folder in chime_ffff_pz/data/Observing and name it Keck-2026B-01, make the resource json and generate targets

**Action:** Created a genuine Keck-native FFFF-PZ Resource instead of reusing
the filtered Lick pool, following the standard FFFF-PZ Resource workflow
(chime-ffff-pz repo):

1. `mkdir chime_ffff_pz/data/Observing/Keck-2026B-01/`
2. Wrote `Keck-2026B-01.json` (instrument `LRIS`, `valid_start/stop` = the
   Oct 2, 2026 Keck twilight window in UTC, `num_targ_longslit=20`,
   `max_AM=2.0`, **`min_mag=19.0`, `max_mag=null`** — the mag>19 rule
   implemented directly as the server-side query, matching the convention
   already used in prior Keck LRIS Resources (`Keck-2026A-8`, `Keck-2025B-2`);
   `min_POx`/`frb_tags`/`frb_statuses` left `null` per the FFFF-PZ HOWTO
   warning). No Dec field exists in this API — Dec-based Nasmyth/airmass
   filtering stays downstream in our own script, as before.
3. `chime_ffff_pz_add_furesource Keck-2026B-01.json` → succeeded (200).
4. `chime_ffff_pz_targets Keck-2026B-01` → 201, wrote
   `Keck-2026B-01_targets.csv` (15 targets), copied into this
   `Night_plans/Keck-2026B-01/` folder.

Credentials: no `automation/config/secrets.env` exists on this machine —
`FFFF_PZ_USER/PASS/URL` are exported in `~/.bashrc` instead, pointing at the
docker-hosted instance at `http://0.0.0.0:8000/` (confirmed live). Flagged
this to the author before running anything, since it creates a real Resource
on a shared server; the author pointed at `.bashrc` rather than the secrets
file. `chime-ffff-pz/chime_ffff_pz/scripts/add_modify_resource.py` and
`targets.py` both read the env vars directly (no secrets.env dependency).

**Repointed `scripts/keck_2026oct02_calculations.py`** from the Lick targets
CSV to this new `Keck-2026B-01_targets.csv`.

**Result — 15/15 targets pass mag>19 (server already filtered), 10/15 pass
sky-observability (HA + Nasmyth-deck check), but 6 of those 10 are mag>21
(need MOS masks, weeks of lead time).** Found and fixed a real bug while
regenerating: `select_targets_for_night()` was scheduling MOS-required
targets into tonight's plan as 0-minute "observations" (can't mill masks in
time for this run). Added a filter dropping `lris_mode == 'MOS (mask
required)'` from the schedulable set — they still surface in the separate
MOS-planning warning printout, just not in tonight's timeline/starlist.

**Final regenerated plan: 4 real longslit targets, 3.3h science / 9.7h dark
time (35% utilization)** — up from 1 target / 11 min (2%) with the filtered
Lick pool, and comparable in quantity to the original (wrong-constraints)
6-target/2.6h version but now built on Keck-native, geometrically-correct
targets: FRB20260518B (19:32-20:17, mag 20.0), FRB20260611G (20:17-21:12, mag
20.6), FRB20250408A (21:12-22:07, mag 21.0), FRB20260418B (01:42-02:27, mag
20.2, rising). Confirms the diagnosis from Prompt 5: the *pool* needed to be
Keck-native, not just the scheduling logic.

---

### Prompt 7
> How are you calculating exposure times? I fear our hand wavy Lick rules won't work here, we need an actual exposure time calculator

**Action:** Replaced the magnitude-bucket exposure heuristic
(`estimate_lris_exposure()` in `scripts/keck_2026oct02_calculations.py`,
adapted from an equally hand-wavy Kast heuristic with an arbitrary "LRIS is
~2x more efficient than Kast" fudge factor) with a real physical
calculation, via a new `scripts/lris_etc.py`.

**The real calculator:** a thin client for the **UCO/Lick Observatories web
S/N calculator** (etc.ucolick.org) — the same physical engine that serves
the official web LRIS/Kast/DEIMOS/ESI/HIRES exposure-time calculators, and
callable directly as a JSON API (`POST .../web_s2n/gen_inst_s2n`), not just
through the browser form. It models real throughput, sky background,
seeing/slit losses, dichroic split, and a template spectrum — not a lookup
table.

**Two decisions needed from the author before wiring it in:**
1. *Blue grism:* the ETC only returns real results for **B300 (300/5000)**
   and **B600 (600/4000)** — the previously-documented 400/3400 (and 1200)
   silently return an empty spectrum with no error (verified by direct POST
   testing). The author confirmed the actual standard LRIS setup is
   **grism 600/4000 (blue), grating 600/7500 centered ~7200 Å (red)** — both
   supported by the ETC, so the LRIS Configuration section below is
   corrected to match (previously incorrectly listed as 400/3400 / 400/8500).
2. *Target S/N:* the old heuristic never defined one — just empirical
   mag→time buckets. Set to **median S/N = 5 per pixel, continuum**,
   per the author.

**Implementation (`scripts/lris_etc.py`):** `query_lris_etc()` POSTs
mag/exptime/airmass/seeing/redshift/grism/grating/dichroic/slitwidth/binning
to the real ETC and returns S/N(λ); `required_exptime()` finds the exptime
needed to hit the target S/N in a continuum window via real ETC calls
(S/N≈√t is used only as the *step direction* between calls — every value is
from an actual query, not assumed) in the blue (4200–5200 Å) and red
(6500–7500 Å) windows separately; `estimate_lris_exposure_real()` takes the
longer-required arm as the simultaneous dual-beam wall-clock time and splits
it into ≥2 sub-exposures (≤600 s each, cosmic-ray rejection). A TLS note:
etc.ucolick.org's cert chain is missing its intermediate server-side (real
InCommon/Sectigo-issued leaf cert, confirmed via `openssl s_client
-showcerts`) — rather than disabling verification, fetched the one missing
intermediate and ship it alongside `certifi`'s bundle
(`scripts/certs/ca_bundle_with_incommon.pem`) so requests still verify
properly.

**Result — a large correction, not a tweak.** At S/N=5, real exposure times
for our mag 20–21 targets are **~1–3 min of science time**, not the 45–55
min the old heuristic gave: `keck_2026oct02_calculations.py`'s `estimate_lris_exposure()`
now calls the real calculator with the target's actual airmass; rerunning
the full pipeline dropped total science time from **3.3h to 0.6h (34 min)**
for the same 4 targets (FRB20260518B: 7 min, FRB20260611G: 8.7 min,
FRB20250408A: 10.7 min, FRB20260418B: 7.3 min — all include the +5 min
slew/acquisition overhead already used elsewhere). The old heuristic was
tuned empirically for the 3m Shane/Kast (then fudged by a flat "2x" for
Keck) — Keck's 10m aperture has ~11x the collecting area, so a flat 2x
factor was never going to be close; the real ETC shows just how far off
(~15x) it actually was.

**New implication — utilization is now target-count-limited, not
exposure-time-limited.** With exposures this short, the 4 currently-known
Keck-native longslit targets use only 6% of the night; the real constraint
tonight is simply *how many good targets are in an observable RA window*,
not how long each takes. See Recommendations.

**Caveat checked, not blocking for this night:** the ETC has no moon-phase/
sky-brightness input (dark-sky assumed). Checked the Moon for Oct 2/3, 2026
at Keck: ~48% illuminated but at **alt ≈ -17°** (below the horizon) around
local midnight — the dark-sky assumption holds for this particular night.
Flag this for any future night where the Moon is up.

---

### Prompt 8
> I see FRB20250408A duration 52 mins, is that right? / ok, the calculator must be wrong, which repo did you use, I see you need atleast 15mins for 21 mag, for one exposure, I would need atleast 3

**Action:** The 52-min figure the author saw didn't match any file at the
time (traced to a stale cached view — current output showed 10.7 min for
that target); investigating anyway surfaced a real design bug in Prompt 7's
`estimate_lris_exposure_real()`.

**Answered directly:** no local repo is involved — `scripts/lris_etc.py`
calls the live web calculator at etc.ucolick.org over HTTP every time.

**The actual bug:** Prompt 7's version searched for one *combined* exposure
time that would hit `target_sn` (5, at the time), then divided that combined
time across `n_sub` sub-exposures — so each individual sub-exposure actually
carried *less* than the target S/N (e.g. 2×170s each individually only
reached S/N≈3, not 5). Printed the real S/N-vs-exptime curve at mag 21 (red
arm) directly from the ETC to make this concrete: 60s→1.3, 170s→3.0,
300s→4.5, 600s→7.0, 900s→8.9, 1200s→10.5. The author's own recollection
("≥15 min for one exposure, need ≥3" at mag 21) lines up almost exactly with
**S/N≈10 measured per single exposure**, not a combined S/N=5.

**Fix:** rewrote `estimate_lris_exposure_real()` so `target_sn` is the S/N
required of *one single sub-exposure* (now default 10, per the author), and
the sub-exposure count is a fixed **minimum of 3** (a cosmic-ray-rejection
floor from the author's practice — 2 frames can only flag a CR discrepancy,
3+ lets you median-reject it — not something derivable from S/N at all).
Total per target is now `3 x (single-exposure time to hit S/N=10)`, not a
combined time split three ways.

**Verified against the author's own number before rerunning the pipeline:**
at mag 21.0, airmass 1.87, the corrected model gives **3 x 1090s (≈18 min
each, 3 exposures)** — matching "at least 15 min, at least 3" almost exactly
(18 min is a bit over 15, consistent with "at least").

**Regenerated result:** total science time for the same 4 targets rose from
0.6h (Prompt 7's under-delivering combined-S/N version) to **2.3h / 9.7h
(23% utilization)** — FRB20260518B: 3×280s (19 min), FRB20260611G: 3×600s
(35 min), FRB20250408A: 3×1060s (58 min), FRB20260418B: 3×380s (24 min). All
still fit within each target's observable window (the scheduler's own
window-fit check would have dropped/shortened any that didn't). This is a
more physically- and operationally-grounded number than either the original
heuristic (45-55 min, no real basis) or Prompt 7's first real-ETC pass (7-11
min, technically real S/N math but measuring the wrong thing).

---

### Prompt 9
> New recommendation, always ask for masked targets for LRIS on the resource, and If we have any target fainter than 21 mag, even if it was pulled as longslit, we always need a mask, so add it as a masked target, you can put this in the info column, also, if a masked target is brighter than 23 mag, we need just 1 hour and if fainter we may need 1.5 to 2 hours

**Context:** the author had independently edited
`chime-ffff-pz/.../Observing/Keck-2026B-01/Keck-2026B-01.json` directly
(`num_targ_mask: 5`, `num_targ_longslit: 10`, down from 20) and re-pulled —
the raw targets CSV is now a fresh **10-target** stochastic draw (FFFF-PZ
sampling is random per the HOWTO; composition differs from the earlier
15-target pull — FRB20260518B and FRB20260611G are gone, replaced by others).
Synced the refreshed CSV into
`Night_plans/Keck-2026B-01/Keck-2026B-01_targets.csv`.

**Checked the concern directly:** confirmed FFFF-PZ's own `mode` column tags
**all 5 of this pull's mag>21 targets as `"longslit"`**, never `"mask"`,
even though `num_targ_mask=5` was requested — FFFF-PZ's mode tagging doesn't
apply a mag cut at all. Good news: `analyze_targets()` never reads FFFF-PZ's
`mode` column in the first place — `lris_mode` has always been derived
independently from `Pri_mag` — so this was already safe. Added an explicit
code comment in `keck_2026oct02_calculations.py` documenting *why* (verified
behavior, not an assumption), so a future maintainer doesn't "simplify" it
into trusting FFFF-PZ's tag.

**Added, per the author:**
1. **`info` column** in `target_analysis.csv` (and the console table):
   every mag>21 target gets an explicit note, e.g. `"Mag 21.2 > 21: MOS mask
   required (~1.0h once milled)"`, regardless of any upstream tag.
2. **Real MOS on-target time** (`estimate_mos_exposure()` in
   `scripts/keck_2026oct02_calculations.py`) — an operational budget, not a
   physical S/N calc (no ETC support for MOS mode): mag ≤ 23 → 1 hour;
   23 ≤ mag < 24 → 1.5 hours; mag ≥ 24 → 2 hours. The 23-24 split point is
   this project's own bucketing of the author's stated 1.5-2h range for
   mag>23, not independently specified — flagged as an assumption.
3. **Standing FFFF-PZ convention:** always request masked targets
   (`num_targ_mask > 0`) alongside longslit when building a Keck LRIS
   Resource — recorded in `claudes_brain.md`'s FFFF-PZ Resource-creation
   notes for future pulls.

**Regenerated result (10-target pool):** 5 MOS-required (all correctly
flagged despite FFFF-PZ's `longslit` tag: FRB20260102A ~1.0h,
FRB20240106A ~1.0h, FRB20250411A ~2.0h, FRB20260418A ~1.0h,
FRB20260502A ~1.0h), 6/10 sky-observable, **2 longslit-schedulable
tonight** (FRB20250408A, FRB20260418B — the pool's composition changed, so
this is a different 2 than before). Science time: **1.4h / 9.7h (14%
utilization)**.

---

### Prompt 10
> Even If it needs mask, I need it in the night plan with the allocated time

**Action:** Prompt 9 had (correctly) computed real MOS on-target times but
still excluded MOS-required targets from the actual schedule/starlist/Excel
— they only appeared in a separate warning. The author wants them **in** the
plan, scheduled with their allocated time, on the working assumption a mask
can be milled before the run (~3 weeks out from 2026-10-02 as of this
session).

**Changed in `scripts/keck_2026oct02_calculations.py`:**
- `select_targets_for_night()` no longer drops `lris_mode == 'MOS (mask
  required)'` rows before scheduling — `estimate_lris_exposure()` already
  dispatches to `estimate_mos_exposure()` for mag>21, so no other scheduling
  logic needed to change.
- Console timeline now tags MOS rows `[MOS - MASK REQUIRED]`; the warning
  block is reworded from "cannot be observed" to "included below with
  allocated time — submit mask designs now."
- `generate_starlist()` and `build_keck_night_plan.py`'s Excel builder both
  now flag MOS rows with a `MASK REQUIRED` comment (starlist) / `Science
  (MOS)` action + comment (Excel), so it's obvious at the telescope which
  targets need a pre-milled mask.
- Added transparent skip-reason logging to the scheduler (it previously
  failed silently) — this immediately surfaced a real, non-obvious
  rejection: FRB20250411A (mag 25.6, needs the full 2h MOS bucket) has an
  airmass<2.0 window of only ~100 min once earlier targets claim part of the
  night, so it doesn't fit and is correctly skipped, with the reason now
  printed (`needs 120 min but only 70 min left in its AM<2.0 window`).

**Regenerated result:** **5 targets now in the plan** (up from 2) — 2
longslit (FRB20250408A 58 min, FRB20260418B 24 min) + 3 MOS (FRB20260502A,
FRB20260102A, FRB20240106A, 60 min each). One MOS candidate
(FRB20250411A) doesn't fit any window at its required 2h and is excluded
with the reason logged. Science time: **4.4h / 9.7h (45% utilization)** —
up from 14%.

---

### Prompt 11
> Are you using proper coordinates and elevation for Keck?

**Action:** Checked `KECK = EarthLocation(...)` in both
`scripts/keck_2026oct02_calculations.py` and `scripts/build_keck_night_plan.py`
against astropy's canonical site database
(`EarthLocation.of_site('keck')`, sourced from the IRAF Observatory
Database — the standard astronomical reference, not just a web search).

**Result:** longitude (-155.4783°) and elevation (4160 m) were already
exactly right. **Latitude was wrong**: the scripts used 19.8263°N; the
correct value is **19.828333°N** — off by ~0.002° (~7 arcsec, ~220 m on the
ground). Fixed in both files, with a comment citing the verification source
so it doesn't drift again.

**Impact:** negligible in practice — rerunning the full pipeline gave
identical twilight times, the same 5 selected targets, and airmass values
shifted only in the 4th-5th decimal place (e.g. 1.165418 → 1.165395 for
FRB20260502A). Fixed anyway because "negligible for this run" isn't the same
as "correct," and a hardcoded site constant is exactly the kind of thing
that should be right regardless of whether the current targets happen to be
insensitive to the error.

---

### Prompt 12
> I made a mistake here, turns out, the night is on the 6th of october and not
> the second, review how we made this plan and update the plans and all the
> dates in the files

**Action:** The run date was wrong throughout Prompts 1-11 — corrected
`2026-10-02` → `2026-10-06` and reran the whole pipeline (not just a text
find/replace), since twilight, LST, and every target's airmass/HA/vignetting
status are date-dependent.

**Renamed** (content and filenames both carried the wrong date):
- `scripts/keck_2026oct02_calculations.py` → `scripts/keck_2026oct06_calculations.py`
- `Keck_LRIS_2026Oct02_Night_plan.xlsx` → `Keck_LRIS_2026Oct06_Night_plan.xlsx`
- `keck_lris_oct02.starlist` → `keck_lris_oct06.starlist`
- `KECK_LRIS_2026OCT02_SUMMARY.md` → `KECK_LRIS_2026OCT06_SUMMARY.md` (this
  file)
- `scripts/build_keck_night_plan.py` kept its name (no date in it) but its
  internal date default, checklist title, sheet name, and start-time constant
  were updated.

**Regenerated result — same 5 targets, same 45% utilization, timings shift by
~10-20 min:** evening twilight moved from 19:22→**19:19 HST**, morning from
05:01→**05:02 HST** (dark time unchanged at 9.7h to 1 decimal). The scheduled
targets and their order are identical to the Oct 2 plan (FRB20260502A [MOS],
FRB20250408A, FRB20260102A [MOS], FRB20260418B, FRB20240106A [MOS]) — a
4-day shift in RA/LST wasn't enough to change which targets clear the
Nasmyth-deck/HA/window filters for this pool. **One rejection reason did
change:** FRB20260418A (mag>21, MOS) was "vignetted by the Nasmyth deck" on
Oct 2 but is "below horizon all night" on Oct 6 — still excluded either way,
but for a different geometric reason, which is exactly the kind of detail a
find/replace on the date string would have silently gotten wrong.

**Not changed (flagged for the author, not touched by Claude):** the live
FFFF-PZ `Keck-2026B-01` Resource
(`chime-ffff-pz/chime_ffff_pz/data/Observing/Keck-2026B-01/Keck-2026B-01.json`)
still has `valid_start`/`valid_stop` set to the Oct 2/3 UTC window
(`2026-10-03T05:00:01Z`–`2026-10-03T15:45:38Z`). That's a live object on a
shared server (per Prompt 6) — updating it means another
`chime_ffff_pz_add_furesource` call, which wasn't run here since it's a
state-changing action on shared infrastructure, not a local file. Recommend
re-submitting the Resource with the Oct 6/7 UTC window before relying on it
for a fresh target pull.

**Also not changed:** the git branch this work lives on is named
`keck-2026oct02` (predates this correction) and the Session Log text for
Prompts 1-11 above still says "Oct 2" throughout, since that's an accurate
record of what was actually discussed at the time — only this doc's
*current-state* sections (Ephemeris, target tables, timeline, output files,
below) were updated to the corrected date.

### Prompt 13
> review our keck night plan and tell me how the slew times were calculated,
> also, confirm if the start and end times match with this
> https://ucolick.org/calendar/keckcal2021-30/keck2026.18oct

**Action:** Review only, no changes. Slews were not computed from telescope
geometry: `lris_etc.py` added a flat +5 min "slew/acquisition" to each
longslit block, MOS blocks were flat 60/90/120 min, and
`build_keck_night_plan.py` wrote a flat 3-min "slew to" row and subtracted
it from the science row (so the scheduler and the xlsx disagreed). The UCO
Keck calendar's Oct 6 row (18° twilight ends 19:19, dawn begins 05:01, LST
20:01 / 05:44, 9.7 h, altitude 4160 m) matches `find_twilight()` (19:19:00,
05:02:00, 20h00m36s / 5h45m11s, 9.72 h) to within the 1-min search step.

### Prompt 14
> for the mask overhead is included, but let's make the base slew time 5 min
> not 3, also, if we are moving from below +20 to above +20 in all Keck
> instrument, make it 20mins, add these for Keck and redo the plan

**Action:** New shared module `scripts/keck_overheads.py`
(`keck_slew_minutes()`: 5 min base, 20 min for Dec < +20 -> Dec > +20; the
reverse direction stays 5 min). The scheduler now charges the slew per
transition, starting from the evening standard (BD+28 4211, Dec +28.9) and
including the slew to the morning standard (Feige 110). On-target time is
`science_min` (longslit ETC total; MOS block unchanged since it already
includes mask overhead). The xlsx takes the slew and on-target times from
the scheduler, so the two can no longer disagree.

**Result:** same 5 targets and order. 40 min of slews in total. One 20-min
slew (FRB20260102A +13.9 -> FRB20260418B +39.4) falls in the existing
mid-night gap, so no target moves. MOS blocks now get their full 60 min
(were 57), and the other targets shift by about 5 min. FRB20250411A is still
excluded (needs 120 min + 5 min slew, only 85 min left in its window).
Night ends 03:49 HST (was 03:44). Per-target reasons are in
`target_rejection_analysis.md` (new).

### Prompt 15
> Wait where is the Gap?

**Action:** Answered, no changes. Main gap 22:37-01:09 HST (152 min), plus
01:48-02:14 (26 min), and 03:49-05:02 unused before dawn. Cause: the B-01
pool ran out of targets. All 5 survivors were scheduled, and the last two
don't rise below AM 2.0 until 01:29 and 02:19. The LST during the gap runs
about 23.3h-1.9h.

### Prompt 16
> Try requesting targets again from FFFF-PZ global, check the .bashrc for url

**Action:** Global FFFF-PZ is `https://frb.chimenet.ca/f4pz/`
(`set_ffff_pz_global` in `~/.bashrc`). A pull of Keck-2026B-01 returned 402
"Could not find resource" because B-01 was only ever added to the local
docker instance. The author said the 01 name is taken on global, so a new
Resource, **Keck-2026B-02**, was created there after checking the name was
free (`add_frb_resource` is add-or-modify). Its settings: 10 mask + 20
longslit, with the valid window moved from the stale Oct 2/3 night to
`2026-10-07T05:00:01Z`-`15:45:38Z`. It returned 20 targets (9 shared with
B-01). A dry-run gave 9 targets but dropped the CHIME repeater FRB20250408A
and needed new masks.

### Prompt 17
> Do we have the sme 5 masks still in? it will be very difficult to get a mask milled now

**Action:** No. The B-02 dry-run kept FRB20260102A and FRB20240106A, dropped
FRB20260502A, and added two new masks (FRB20260829B, FRB20260603D). A
dry-run restricted to the B-01 masks gave 8 targets and a 104-min gap
(23:25-01:09).

### Prompt 18
> Will the new mask fill up the Gap?

**Action:** Only FRB20260603D (RA 23.6h, AM<2 window 19:19-03:19) can reach
the gap. The other new MOS targets are only up in early evening or near
dawn. Adding it as a fourth mask cut the gap to 39 min.

### Prompt 19
> I will try put it in the plan, increase all slew times that are 5 mins to 10, and add 5 more min buffer time for each mask, remake the plan

**Action:** `KECK_SLEW_BASE_MIN` is now 10 (the 20-min crossing is
unchanged). Added `MOS_MASK_BUFFER_MIN = 5` and `MOS_MASKS_AVAILABLE` (the 5
B-01 MOS candidates plus FRB20260603D; any other mag>21 target is rejected
as "No mask available"). The plan was rebuilt from the B-02 pull into
`Night_plans/Keck-2026B-02/`: 9 targets, 6.1 h on target plus 100 min of
slews, 63% of dark time, 10 min idle, ending 03:59. The repeater
FRB20250408A is still unscheduled (7 min left in its window). The scripts
now point at B-02, and this folder's outputs are kept as the earlier record.

---

## Ephemeris

| Parameter | Value |
|-----------|-------|
| Date | October 6, 2026 |
| Observatory | Keck (Maunakea) |
| Latitude | 19.828333° N |
| Longitude | 155.4783° W |
| Elevation | 4160 m |
| Timezone | HST (UTC-10) |
| Evening twilight (18°) | 19:19 HST |
| Morning twilight (18°) | 05:02 HST |
| Dark time | 9.7 hours |
| Evening LST | 20h 01m |
| Morning LST | 5h 45m |

## Observable RA Range

| Time | RA Range (HA ±5.5h) |
|------|---------------------|
| Evening | 14.5h - 1.5h |
| Morning | 0.3h - 11.3h |

## Target Analysis (REGENERATED, Prompt 12 — Oct 6 date correction; pool/logic unchanged from Prompt 9-10, only ephemeris shifted)

**Pool changed underneath this doc as of Prompt 9:** the author re-pulled
`Keck-2026B-01` directly (`num_targ_mask=5`, `num_targ_longslit=10`, down
from the earlier `num_targ_longslit=20`/no-mask-request version). FFFF-PZ's
sampling is stochastic, so this is a **different, smaller 10-target pool**,
not a filtered subset of the earlier 15 — two of the four previously
scheduled targets (FRB20260518B, FRB20260611G) aren't in this pull at all.

**The funnel (10 → 2):**

```
10 targets (Keck-2026B-01 FFFF-PZ pull, all mag > 19)
 ├─ 4 fail sky-observability
 │   ├─ 2 vignetted by the Keck I Nasmyth deck while rising
 │   │   (FRB20260514A, FRB20260503B)
 │   └─ 2 below horizon all night (FRB20260418A, FRB20260627D)
 └─ 6 pass sky-observability
     ├─ 4 are mag > 21 -> need a MOS slitmask (weeks lead time,
     │   can't be milled in time for this run)
     │   (FRB20260102A, FRB20240106A, FRB20250411A, FRB20260502A)
     └─ 2 are longslit-schedulable tonight  <-- the actual plan
         (FRB20250408A, FRB20260418B)
```

(A 5th MOS target, FRB20260418A, fails sky-observability too — below the
horizon all night on Oct 6 — so it's mag>21 *and* not up tonight regardless
of mask status. On the Oct 2 date this same target failed for a different
reason, Nasmyth-deck vignetting — a 4-day RA/LST shift moved it from one
failure mode to the other without changing the outcome.)

### All 10 targets from the Keck-2026B-01 FFFF-PZ Resource (min_mag=19, LRIS)

| TNS | RA (h) | Dec (°) | mag | LRIS Mode | Min AM | Observable | Reason / info |
|-----|--------|---------|-----|-----------|--------|------------|----------------|
| FRB20260102A | 1.94 | +14 | 21.2 | MOS | 1.01 | sky: YES | Mag 21.2 > 21: MOS mask required (~1.0h once milled) |
| FRB20260418B | 6.18 | +39 | 20.2 | longslit | 1.09 | YES | scheduled 19:29 |
| FRB20240106A | 6.73 | +60 | 22.5 | MOS | 1.38 | sky: YES | Mag 22.5 > 21: MOS mask required (~1.0h once milled) |
| FRB20250411A | 7.51 | +31 | 25.6 | MOS | 1.18 | sky: YES | Mag 25.6 > 21: MOS mask required (~2.0h once milled) |
| FRB20260514A | 8.48 | +69 | 20.3 | longslit | 1.86 | NO | Vignetted by Keck I Nasmyth deck (az 18°, alt 33° — needs 33° in az 5–146°) |
| FRB20260418A | 9.35 | +36 | 21.2 | MOS | 1.77 | NO | Below horizon all night; also Mag 21.2 > 21: MOS mask required (~1.0h once milled) |
| FRB20260503B | 9.48 | +18 | 20.9 | longslit | 1.97 | NO | Vignetted by Keck I Nasmyth deck (az 80°, alt 31°) |
| FRB20260627D | 16.23 | +68 | 19.6 | longslit | 1.97 | NO | Below horizon all night |
| FRB20260502A | 18.57 | +47 | 22.4 | MOS | 1.18 | sky: YES | Mag 22.4 > 21: MOS mask required (~1.0h once milled) |
| FRB20250408A | 21.19 | +77 | 21.0 | longslit | 1.87 | YES | scheduled 20:29 |

All 10 pass the mag>19 selection rule (server-side `min_mag=19.0`). Every
`info` note comes from **our own** mag cut, independent of FFFF-PZ's `mode`
column, which tags all 5 mag>21 targets in this pull as `"longslit"` (see
Prompt 9) — do not trust that column.

### Selected Targets (5) — MOS targets now included with allocated time (Prompt 10)

Times are on-target (updated Prompt 14); Duration excludes slew, which is
listed in the Night Timeline below.

| # | Target | Time (HST) | RA | Dec | mag | AM | Mode | Exposure (each arm) | Duration | Notes |
|---|--------|------------|-----|-----|-----|-----|------|----------------------|----------|-------|
| 1 | FRB20260502A | 19:34-20:34 | 18.57h | +47° | 22.4 | 1.2 | **MOS** | mask required | 60.0 min | Submit mask design |
| 2 | FRB20250408A | 20:39-21:32 | 21.19h | +77° | 21.0 | 1.9 | longslit | 3 x 1060s | 53.0 min | |
| 3 | FRB20260102A | 21:37-22:37 | 1.94h | +14° | 21.2 | 1.7 | **MOS** | mask required | 60.0 min | Submit mask design |
| 4 | FRB20260418B | 01:29-01:48 (Oct 7) | 6.18h | +39° | 20.2 | 1.7 | longslit | 3 x 380s | 19.0 min | Rising |
| 5 | FRB20240106A | 02:19-03:19 (Oct 7) | 6.73h | +60° | 22.5 | 1.8 | **MOS** | mask required | 60.0 min | Submit mask design |

**FRB20250411A (mag 25.6, needs the full 2h MOS bucket) does not fit any
window** — its own airmass<2.0 window is only ~90 min once other targets
claim earlier time, so the scheduler correctly excludes it (reason logged:
`needs 120 min but only 90 min left in its AM<2.0 window (02:49-04:49)`).
This is a real geometric/time-budget constraint, not a mask-readiness issue.

## Night Timeline (Prompt 14 snapshot, B-01 pool, 5-min slews — superseded by Keck-2026B-02)

```
19:10 HST  Flux standard (BD28d4211)          5 min
19:15      Focus check                         5 min
19:29      slew -> FRB20260502A                5 min
19:34      FRB20260502A [MOS]                 60 min   AM 1.20
20:34      slew -> FRB20250408A                5 min
20:39      FRB20250408A                       53 min   AM 1.87
21:32      slew -> FRB20260102A                5 min
21:37      FRB20260102A [MOS]                 60 min   AM 1.69
22:37      [gap - no targets]                152 min
01:09      slew -> FRB20260418B               20 min   (Dec +13.9 -> +39.4)
01:29      FRB20260418B (rising)              19 min   AM 1.93
01:48      [gap]                              26 min
02:14      slew -> FRB20240106A                5 min
02:19      FRB20240106A [MOS]                 60 min   AM 1.83
03:19      slew -> Feige110                    5 min
03:24      Flux standard (Feige110)            5 min
03:29      Calibrations (arcs, flats)         20 min
03:49      END   (18° dawn 05:02 HST)
```

## Night Utilization (Prompt 14 snapshot — superseded by Keck-2026B-02)

| Metric | Value |
|--------|-------|
| On-target time | 4.2 hours (252 min) |
| Slew time | 40 min (4 x 5 min + 1 x 20 min) |
| Available dark time | 9.7 hours |
| Utilization (on target / dark) | 43% |

Utilization is lower than Prompt 12's 45% only because slew is now counted
separately rather than inside "science time". The target list is unchanged.

## LRIS Configuration

| Parameter | Value |
|-----------|-------|
| Mode | Longslit |
| Dichroic | 560 |
| Blue grism | 600/4000 |
| Red grating | 600/7500 (centered ~7200 Å) |
| Slit width | 1.0" |
| CCD binning | 2x2 |

Corrected in Prompt 7: previously listed as 400/3400 blue / 400/8500 red,
which the real LRIS ETC can't even model (see Prompt 7). 600/4000 and
600/7500 are the author's actual standard Keck/LRIS FRB-host setup.

## LRIS Mode Summary

| Mode | Mag Limit | Lead Time | Use Case |
|------|-----------|-----------|----------|
| Longslit | ≤ 21 | None | Single targets, quick setup |
| MOS | > 21 | Weeks | Faint targets, pre-milled masks |
| Imaging | Any | None | Acquisition, photometry, backup |

## Recommendations

1. **Masks (updated Prompt 19):** the current B-02 plan uses 4 masks.
   FRB20260502A, FRB20260102A and FRB20240106A are the existing ones.
   **FRB20260603D is new**, and the author will try to get it milled. If it
   isn't ready, its 22:22-23:37 slot goes idle. Any other mag>21 target is
   excluded because new masks are very hard to get this late.

2. **Request more targets in the next Keck FFFF-PZ pull:**
   - At S/N=10/exposure (3x min), real longslit exposures run ~19-58 min
     depending on magnitude, and MOS candidates need ~1-2h once masked — the
     remaining ~4.4h of gaps has room left. Raise `num_targ_longslit` (and
     keep `num_targ_mask` > 0, per Prompt 9) well above 10 total (a larger
     pull would still need to clear the Nasmyth-deck/HA/RA-window filters,
     so ask for more than the number you actually want scheduled)
   - Target *count*, not target brightness margin, is still the limiting
     factor

3. **FRB20250411A (mag 25.6) needs a longer window than it has:** its 2h
   MOS bucket doesn't fit the ~100 min its own airmass<2.0 window allows
   once earlier targets claim part of the night. Either accept a shorter
   (higher-airmass) exposure for it specifically, or hold it for a night
   where its window falls earlier/later relative to other targets.

4. **Never trust FFFF-PZ's own `mode` tag for the mag>21 cut** — it labels
   all 5 mag>21 targets in this pull `"longslit"` regardless of magnitude
   (see Prompt 9); rely on this doc's `info` column / our own mag check
   instead. **Always request masked targets on the Resource**
   (`num_targ_mask > 0`) going forward.

5. **Nasmyth-deck-aware scheduling for Keck I/LRIS:**
   - Rising targets (az 5.3-146.2°, i.e. NE/E) need alt ≥ 33.3° before they're clear — schedule them later in their window (2 of 10 targets in this pool lost to this while rising on Oct 6: FRB20260514A, FRB20260503B; a 3rd, FRB20260418A, fails for a different reason on this date — below the horizon all night, not vignetting)
   - Setting/transiting targets only need the normal 18° floor — prioritize these first, as done here (FRB20250408A)

6. **Keep future Keck pulls Keck-native:** this run confirms reusing a Lick-derived pool (Prompt 5, 1 target/2%) is a poor substitute for a dedicated FFFF-PZ Resource with `min_mag=19` (Prompt 6) — always create a Keck-specific Resource rather than filtering another site's list.

7. **Revisit target S/N if these hosts need more than a redshift ID:** S/N=10/pixel per single exposure (3 exposures min) is calibrated to the author's stated practice for basic redshift ID. If any host needs line-profile work, higher-confidence classification, or a faint emission feature, rerun with a higher `target_sn` (or more than 3 exposures) in `estimate_lris_exposure_real()`.

8. **Pool composition will keep shifting between pulls:** FFFF-PZ sampling is stochastic (per the HOWTO) — re-running `chime_ffff_pz_targets` on the same Resource can return a different set each time. In this case Prompt 9's 10-target pull turned out to be an exact subset of Prompt 6's 15 (all 10 TNS were already in the earlier pull; the 5 dropped — FRB20230702A, FRB20250819A, FRB20260427A, FRB20260518B, FRB20260611G — simply weren't drawn this time), but don't assume that always holds. Always re-sync `Night_plans/Keck-2026B-01/Keck-2026B-01_targets.csv` from the chime-ffff-pz side before trusting this doc's numbers.

## Output Files

| File | Description |
|------|-------------|
| `Keck_LRIS_2026Oct06_Night_plan.xlsx` | Excel night plan with timeline |
| `keck_lris_oct06.starlist` | Keck starlist (5 targets, 3 flagged MASK REQUIRED, + standards) |
| `Keck-2026B-01_targets.csv` | Raw 10-target pull from the FFFF-PZ Keck-2026B-01 Resource (Prompt 9 refresh) |
| `target_analysis.csv` | All 10 targets with observability/mode/info |
| `selected_targets.csv` | 5 selected targets with scheduling (2 longslit + 3 MOS) |
| `KECK_LRIS_2026OCT06_SUMMARY.md` | This document |

Resource JSON and CLI outputs also live at
`chime-ffff-pz/chime_ffff_pz/data/Observing/Keck-2026B-01/` (the FFFF-PZ side
of record: `Keck-2026B-01.json`, `Keck-2026B-01_targets.csv`). **Not yet
updated for the Oct 6 correction (Prompt 12):** that JSON's
`valid_start`/`valid_stop` still encode the Oct 2/3 UTC window
(`2026-10-03T05:00:01Z`-`2026-10-03T15:45:38Z`) — it's a live Resource on a
shared server, so re-submitting it with the Oct 6/7 window is a follow-up
for the author, not done here. **Superseded (Prompt 16):** the global
server now has **Keck-2026B-02** with the Oct 6/7 window
(`chime-ffff-pz/chime_ffff_pz/data/Observing/Keck-2026B-02/`), and that is
the Resource of record for this night.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/keck_2026oct06_calculations.py` | Ephemeris, target analysis, scheduling (reads/writes `Night_plans/Keck-2026B-02/` since Prompt 19) |
| `scripts/build_keck_night_plan.py` | Excel night plan generation |
| `scripts/keck_overheads.py` | Keck slew rule for all instruments: 10 min base, 20 min Dec<+20 -> Dec>+20 (Prompts 14, 19) |
| `scripts/keck_2026oct06_rejection_analysis.py` | Per-target accept/reject report, `target_rejection_analysis.md` |
| `scripts/lris_etc.py` | Real LRIS exposure-time calculator (Prompt 7) — client for the UCO/Lick web S/N calculator (etc.ucolick.org) |

## Lessons Learned

1. **Latitude matters:** Lick (lat 37°) and Keck (lat 20°) have very different observable Dec ranges. Targets selected for Lick are often too far north for Keck.

2. **Lick-excluded = Keck opportunity, but not automatic:** Targets at Dec > 82° (Lick's limit) are kept for Keck regardless of magnitude, but still have to individually clear the real Nasmyth-deck az/alt check — being high-Dec doesn't exempt them from vignetting.

3. **LRIS longslit limit:** mag ≤ 21 for longslit; fainter needs MOS masks with weeks lead time.

4. **Keck should chase faint targets, not duplicate Lick:** with a 10m aperture, Keck time on mag≤19 targets Lick's 3m can already reach is a poor use of the resource. Selection rule: mag > 19, unless Dec > 82° (unreachable from Lick at any mag).

5. **Nasmyth-deck vignetting is azimuth-fixed, not target-relative:** Keck I's deck blocks az 5.3-146.2° (N/E) below alt 33.3°; Keck II is blocked S/W instead. A target rising through the NE/E must climb well above the normal 18° floor before it's usable — "wait for it to rise." Setting targets in the W/SW clear the deck at the normal floor, so they're the easier/priority catch on Keck I. (Source: Keck Telescope Pointing Limits, www2.keck.hawaii.edu/inst/common/TelLimits.html.)

6. **Reusing another site's target pool doesn't transfer:** applying the Keck-correct rules (mag>19-unless-Dec>82, real Nasmyth vignetting) to the Lick-2026B-01 pool leaves only 1 of 14 targets observable (11 min, 2% of the night). The pool itself needs to come from a Keck-specific FFFF-PZ query, not a filtered Lick list.

7. **A dedicated FFFF-PZ Resource fixes it:** creating a real `Keck-2026B-01` Resource (`instrument=LRIS`, `min_mag=19.0`, `max_mag=null`) and pulling its targets directly gives a Keck-native pool — 4/15 schedulable tonight (35% utilization *before* the Prompt 7 real-ETC correction dropped it to 6%, see below) vs. 1/14 (2%) from the filtered Lick list. `min_mag` alone on the server implements "mag>19"; there's no Dec field in the Resource JSON, so Dec/Nasmyth-deck filtering stays downstream in our own script either way.

8. **MOS-mask targets must be dropped from tonight's schedule, not just flagged:** `select_targets_for_night()` was silently scheduling mag>21 targets as 0-minute "observations" since masks take weeks to mill. Fixed by filtering `lris_mode == 'MOS (mask required)'` out of the schedulable set before building the timeline — they still surface in the separate MOS-planning warning for future-run tracking.

9. **No `secrets.env` needed for FFFF-PZ CLI scripts:** `add_modify_resource.py`/`targets.py` read `FFFF_PZ_URL/USER/PASS` straight from the environment; on this machine they're exported in `~/.bashrc` pointing at a docker-hosted instance (`http://0.0.0.0:8000/`), not the `automation/config/secrets.env` file (which doesn't exist here — only the template and a `secrets_test.env`).

10. **Magnitude-bucket exposure heuristics don't survive a change of telescope:** the LRIS exposure table was adapted from Kast's by applying a flat, arbitrary "2x more efficient" fudge factor. Keck's 10m vs. Lick's 3m is actually ~11x the collecting area — the fudge factor was never going to be close, and the real LRIS ETC showed it was off by ~15x (45-55 min heuristic vs. 7-11 min real, at S/N=5). Any time an exposure-time rule is carried from one instrument/telescope to another, it needs re-derivation from real throughput/S/N, not a scaling guess.

11. **A "web ETC" can be a real, scriptable API, not just a browser form:** etc.ucolick.org's HTML form POSTs to a JSON endpoint (`web_s2n/gen_inst_s2n`) with no auth required — the same backend serves the official LRIS/Kast/DEIMOS/ESI/HIRES calculators. Worth checking for a programmatic backend behind any "calculator" web page before building a from-scratch physical model.

12. **A calculator's supported option list can be narrower than its UI dropdown suggests, and it won't tell you:** LRIS's real standard blue grism (600/4000) works, but grism/grating combinations the ETC doesn't implement (400/3400, 1200/anything) return an empty result with `errormsg=""` — no error, just silently nothing. Always check array length/content, not just the error field, when validating an external calculator's response.

13. **A TLS chain failure isn't automatically the client's fault:** etc.ucolick.org's cert is genuinely CA-issued (InCommon/Sectigo) but the server omits its intermediate — confirmed via `openssl s_client -showcerts` before reaching for `verify=False`. Fetching the one missing intermediate (from the leaf cert's `Authority Information Access` CA-issuers URL) and adding it to the trust bundle preserves real verification instead of disabling it.

14. **Short real exposures shift the bottleneck from time to target count:** once exposure times reflect real S/N physics, the same 4-target plan uses well under half the night (23% at the corrected S/N=10/3-exposure model, or as little as 6% under Prompt 7's buggy combined-S/N version). The lesson generalizes beyond this run: whenever exposure-time assumptions get corrected downward, the next question is always "do we have enough targets queued," not "can we fit them in."

15. **"Combined S/N across N sub-exposures" and "S/N per single sub-exposure, N times" are different targets — pick the one that matches how the data will actually be used.** Prompt 7's bisection found one *combined* exposure time hitting the target S/N, then divided it across sub-exposures — so each individual frame quietly carried less S/N than intended (e.g. "2×170s" each only reached S/N≈3 toward a S/N=5 goal). Fixed in Prompt 8 by making the target apply to one single sub-exposure, with the sub-exposure count set separately (a fixed CR-rejection floor, not derived from S/N at all). A number that looks physically correct in isolation (an ETC call, a real S/N value) can still be wired into the wrong quantity.

16. **A domain expert's gut-check number is worth more than it looks — use it to calibrate, not just to flag disagreement.** The author's recalled "≥15 min per exposure, ≥3 exposures" for mag 21 wasn't just "the tool feels wrong" — reverse-engineering it against the real S/N-vs-exptime curve pinned down the actual missing parameter (S/N≈10 per single exposure) almost exactly. When a domain expert's number and a calculator's output disagree by a large, consistent factor, look for what *quantity* the expert's number is actually describing before assuming either side is simply wrong.

17. **Never trust an upstream system's own mode/category tag over your own domain rule, even when the upstream system is the authoritative source of the data.** FFFF-PZ tags every target pulled via `num_targ_longslit` as `mode="longslit"`, with no magnitude cut applied at all — confirmed empirically (5 of 5 mag>21 targets in the Prompt 9 pull were tagged `"longslit"`). This script already derived `lris_mode` independently from `Pri_mag` rather than reading FFFF-PZ's `mode` column, which turned out to be the right defensive call in hindsight — but it was accidental, not a deliberate design decision, until Prompt 9 made it explicit and documented why.

18. **FFFF-PZ's target sampling is stochastic — a re-pull is not a superset or a refinement, it's a new random draw.** Re-running `chime_ffff_pz_targets` on the same Resource after only changing `num_targ_mask`/`num_targ_longslit` produced a smaller pool that happened to be an exact subset of the earlier one this time (10 of the same 15 TNS) — but that's not guaranteed. Any doc or script referencing "the pool" needs to re-sync from the FFFF-PZ side and re-verify before trusting old numbers, every time a Resource is re-pulled.

19. **"Flag it as excluded" and "schedule it with a real time estimate" are different asks — computing the right number isn't the same as using it.** Prompt 9 built real MOS timing (`estimate_mos_exposure()`) but still dropped those targets from the actual schedule before Prompt 10 asked for them to be included. A calculated value sitting in an `info` column doesn't help an observer unless it's wired into the timeline/starlist/Excel the same way any other target's exposure time is.

20. **A silent scheduler `continue` hides real constraints, not just uninteresting ones.** Adding a print statement at each skip point in `select_targets_for_night()` immediately surfaced that FRB20250411A's 2h MOS requirement doesn't fit its own ~100-min airmass<2.0 window — a genuine, non-obvious geometric conflict that had been invisible before (it just silently wasn't in the output). Log *why* a candidate was dropped, not just that it was.

21. **Verify hardcoded site constants against a canonical source, not a web search alone.** Keck's `EarthLocation` latitude (19.8263°) was wrong by ~7 arcsec — caught by checking against `astropy.coordinates.EarthLocation.of_site('keck')` (IRAF Observatory Database), which is more authoritative than the scattered values a web search turns up (Wikipedia, GPS-lookup sites, etc. all differ slightly). The error was too small to change this run's target selection, but "doesn't matter this time" isn't the same as "correct" — fix it anyway, since a future target or a tighter constraint could make it matter.

22. **A wrong date is a silent, whole-pipeline error, not a cosmetic one — and a 4-day shift can still change individual outcomes.** Every twilight/LST/airmass/HA/vignetting calculation in this doc depended on `date_str`; the run date being wrong for 11 prompts meant the entire ephemeris was subtly off the whole time, even though the final schedule composition happened to come out the same. Fixing it required rerunning the pipeline, not editing date strings by hand — a text find/replace on "Oct 2"→"Oct 6" would have kept the old (wrong) twilight times and missed that FRB20260418A's rejection reason actually changes (vignetted → below horizon) between the two dates.

## Git Commands

```bash
# Create clean branch for Keck planning
git checkout -b keck-2026oct02

# Add Keck-specific files
git add Night_plans/Keck-2026B-01/
git add scripts/keck_2026oct02_calculations.py
git add scripts/build_keck_night_plan.py
git add context/claudes_brain.md
git add Logs/2026/09/

# Commit
git commit -m "Add Keck/LRIS night plan for Oct 2, 2026

- New scripts for Keck ephemeris and scheduling
- 6 targets selected (incl. Lick-excluded FRB20250102C)
- LRIS mode info: longslit mag≤21, MOS for fainter
- 2.6h science / 9.7h night (27% utilization)
- Recommendation: query FFFF-PZ with Dec<60 for Keck

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

# Push
git push -u origin keck-2026oct02
```

**Note on the branch name (flagged for the author, not changed here — git
operations on this repo are JXP's to run, per this repo's CLAUDE.md):** the
above is the actual history of how this branch was created and is left
as-is. The branch itself is still named `keck-2026oct02`, which now
undersells what it contains (the Oct 6 corrected plan). Renaming it
(`git branch -m keck-2026oct02 keck-2026oct06` + force-push a new upstream)
is optional cleanup, not required for the plan itself to be correct.


### Acounting for the Nasmyth Platform
Keck 1 - wait for target to rise, easier to observe setting targets
Keck 2 - Is the opposite