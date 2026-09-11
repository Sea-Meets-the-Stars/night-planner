# Claude's Brain — night-planner

This file is Claude's persistent memory for the **night-planner** project. As I
learn about night planning, the telescope, the author's preferences, and how this
repository is organized, I record the durable, reusable knowledge here — the
things a fresh session would want to know. A dated **Version History** at the
bottom tracks every update.

## Project purpose

- Teach Claude to generate a **night plan for a modern, professional telescope**,
  learning from two professional astronomers (J. Xavier Prochaska, `jxp@ucsc.edu`,
  and a colleague).
- Longer-term goal: a **GitHub-hosted webpage dashboard** monitoring all of the
  author's Claude-assisted projects.

## Working conventions (from CLAUDE.md)

- **Git:** the author runs all git commands; I use only read-only git.
- **Calculations:** always write them as a Python script to disk (reproducible),
  never inline-only.
- **Logging:** same approach as the ClimateIntelligence repo — a daily narrative
  log I write at `Logs/YYYY/MM/YYYY-MM-DD.md`, plus `Logs/log_summary.csv` written
  automatically by the `Stop` hook (`.claude/hooks/log_usage.py`). CO2 ≈ 0.076 g
  per 1,000 tokens. See [`../Logs/logging.md`](../Logs/logging.md).
- **Coding:** Python; methods not classes; imports at top; docstrings with
  inputs/outputs; matplotlib/seaborn/Bokeh for plots; `"Created by JXP and Claude"`
  header on every file and docstring.

## Repository layout (as of 2026-07-11)

- `CLAUDE.md` — guidance for Claude (this project's rules).
- `claude_prompts/start_up.md` — ordered start-up prompts driving initial setup.
- `context/` — durable context; `claudes_brain.md` (this file).
- `Logs/` — daily narrative logs, `log_summary.csv`, `logging.md`.
- `.claude/` — `settings.json` (Stop hook wiring), `hooks/log_usage.py`,
  `skills/` (`grill-me`, `critical-partner`; copied from ClimateIntelligence).
- `setup.py` / `setup.cfg` / `pyproject.toml` — packaging. Author's convention
  (from `python/linetools` and `Projects/XAI`): metadata + deps in **setup.cfg**,
  `pyproject.toml` limited to `[build-system]`, `setup.py` a minimal `setup()` shim.
- `requirements.txt` — mirror of `setup.cfg` install_requires.
- `night_planner/` — the Python package (`__init__.py`, `__version__`).
- `tests/` — pytest suite (`test_import.py` smoke test passes).

## Author's Python-repo conventions (learned from linetools & XAI)

- Package layout: `<pkg>/` for source, `tests/` for `test_*.py`, metadata in
  `setup.cfg` under `[metadata]`/`[options]`, `pyproject.toml` build-system only.
- BSD-3 license; author `J. Xavier Prochaska`. Plotting via matplotlib.
- **Reference project:** `Projects/XAI` is the closest sibling — a Claude-driven
  *webpage dashboard to monitor all Claude-based projects* (matches night-planner's
  stated dashboard goal). Its `.claude/settings.json` (WebSearch/WebFetch allow +
  the `log_usage.py` Stop hook) is identical to ClimateIntelligence's and is the
  one to copy here (already in place from start-up prompt 1).
- Note: the prompt referenced `Oceanography/python`, which does not exist on disk;
  `papers/Oceanography/*` holds paper *analysis* dirs, not packaged repos. Used the
  author's actual Python repos (linetools, XAI, ClimateIntelligence) instead.

## Astronomy / night-planning knowledge

- _(To be filled in as I learn the telescope, instruments, targets, and the
  astronomers' night-planning workflow.)_
- **UCO/Lick observing calendars** (`ucolick.org/calendar/`, readme at
  `readme.html`; details in [`claudes_context.md`](claudes_context.md)):
  pre-computed nightly almanacs for **Lick (Mt. Hamilton, PST)** and **Keck
  (Maunakea, HST)**, one row per evening-date-plus-following-morning, in
  12° (nautical) and 18° (astronomical) twilight variants — sunset/sunrise,
  twilight/dawn times, moon rise/set, sidereal times (twilight/midnight/dawn),
  night & dark length, moon RA/Dec/distance at midnight. Authoritative
  site-specific reference for cross-checking our astroplan/thorsky-computed
  night events for any Lick/Keck night, 2011–2030 (adjacent decades also
  posted).
- **Instrument taxonomy & the facility instrument set** (full per-instrument
  summaries with URLs in [`claudes_context.md`](claudes_context.md), section
  "Instrument manuals"): the types that matter for planning are **imager /
  longslit / multi-object (MOS, slitmask) / echelle-echellette / IFU** — type
  drives the constraints (blue-UV coverage → dark time; NIR → moon-tolerant;
  MOS → masks fixed before the night; single slit → parallactic-angle/ADC
  choices; Nasmyth mounts → rotator/PA handling).

  | Instrument | Telescope (focus) | Type | Coverage | Planning hook |
  |---|---|---|---|---|
  | Kast | Shane 3m (Cass) | dual-arm longslit | blue+red via dichroic (4600/5700 Å splits) | slit PA; simultaneous arms |
  | HIRES | Keck I (Nasmyth) | echelle | 0.3–1.0 µm, R 25k–85k | HIRESb vs HIRESr fixed for the night; image rotator for PA/parallactic |
  | LRIS | Keck I (Cass) | imager+longslit+**MOS** | 3200–10,000 Å, R 300–5000 | masks milled on-site → pre-run lead time |
  | MOSFIRE | Keck I (Cass) | NIR **MOS**+imager | 0.97–2.41 µm (Y/J/H/K, one band), R≈3500 | CSU reconfigures in <5 min — no milled masks |
  | DEIMOS | Keck II (Nasmyth) | imager+longslit+**MOS** | optical, ≤5000 Å/exposure, R≤6000 | milled masks → pre-run lead time; 16.6′ slit length |
  | ESI | Keck II (Cass) | echellette+imager | 0.39–1.1 µm in one shot, R≤13k | fixed format, minimal setup choices |
  | KCWI | Keck II (Nasmyth) | **IFU** | blue 3500–5600 Å + red 5400–10,800 Å, R≈900–4500+ | slicer (8.4/16.5/33″×20.4″) sets R & FOV; dark time for blue |
  | NGPS | P200 (Cass) | 4-channel slit spectrograph | 3050–10,400 Å simultaneous, R>4000 | ships an ETC + Observation Timeline Modeler (prior art) |
  | GMOS | Gemini N & S | imager+longslit+**MOS**+IFU | 0.36–1.03 µm, R≤10k | queue/OB-based; masks + 3 mounted gratings decided in advance |

  Mask-lead-time (MOS) instruments: **LRIS, DEIMOS, GMOS** (physical milled
  masks) and **MOSFIRE** (software mask designs, but reconfigurable at night);
  single-slit/echelle: **Kast, HIRES, ESI, NGPS**; IFU: **KCWI** (and GMOS-IFU,
  NGPS slicer).
- **Kast FRB-host setup & exposure heuristic (2026B-01; from the authors'
  prior Lick/Kast plans):** standard setup is the **d57 dichroic** (split
  ~5700 Å), **600/7500** grating on the red arm, **600/4310** grism on the
  blue arm, **2" slit**. Kast is dual-beam — both arms expose
  *simultaneously*, so per-target wall clock = one arm's total, not the sum.
  Total integration T per arm scales with primary-host r-mag:
  <15.5 → 1800 s; 15.5–17.5 → 2400 s; 17.5–19.3 → 3600 s; ≥19.3 → 5400 s.
  Red splits into 600 s subframes (300 s if mag < 13); blue (less efficient)
  into 900 s (T ≤ 1800), 1200 s (T = 2400–3600), or 1800 s (T ≥ 5400)
  subframes, ≥2 per arm, keeping red_total ≈ blue_total. Cell strings are
  "N x 600" / "N x 1200"; Duration (hh:mm) = max arm total; slew rows stay
  at 5 min. Implemented in `night_planner/estimate_kast_exposures.py`.

### Skills & tools for telescope night planning (researched 2026-07-11)

**Installable agent/Claude skills**
- **Astropy Claude Code Skill** (mcpmarket) — coordinate transforms (ICRS/Galactic/
  **AltAz**), time-scale conversions (UTC/TAI/TDB), units, FITS I/O. The primitives
  for computing where/when a target is observable.
- **K-Dense-AI `claude-scientific-skills`** — 140+ agent skills (open Agent Skills
  standard, works in Claude Code). Includes an **Astropy** skill and a **SIMBAD**
  astronomical-database skill; astronomy DBs: NASA, SDSS, SIMBAD, Exoplanet Archive.

**Python packages (the computational core — wrap these, don't reinvent)**
- **astroplan** (Astropy-affiliated) — THE observation-planning package: `Observer`,
  `FixedTarget`, observability under constraints (`AirmassConstraint`,
  `AtNightConstraint`, `MoonSeparationConstraint`, `MoonIlluminationConstraint`),
  airmass/parallactic-angle plots, sky charts, and a **Scheduler** (priority /
  sequential). Already a project dependency (prompt 2). This is our engine.
- **Visplot** — web tool: hardware-aware visibility + heuristic scheduling
  (altitude & hour-angle limits, twilight, moon distance); good for ToO triggers.
- **AstroSA** — framework to benchmark/assess schedulers.

**Professional Phase-2 systems (the structure a "night plan" should emulate)**
- **ESO p2** — Observation Blocks (OBs), containers, README, finding charts, ObsPrep.
- **Gemini Observing Tool (OT)** — Phase-II observation definition; same sequences
  run at the telescope. Takeaway: a professional plan = ordered OBs + per-target
  constraints + finding charts + a run README, not just a target list.

**Best-practice knowledge to encode**
- Order targets by meridian transit / optimal airmass; plan around twilight windows,
  Moon phase & separation; check seeing/transparency forecasts (Clear Outside,
  Astrospheric). (Amateur equipment/thermal/night-vision tips are mostly N/A for a
  professional facility.)

**Recommendation:** build a project `night-plan` skill whose engine is **astroplan**,
optionally vendoring the **Astropy** skill for coord/time primitives, and whose
output structure mirrors ESO p2 / Gemini OT (ordered OBs + constraints + finding
charts + README). Awaiting the astronomers' specific telescope/site/instrument
before authoring. See references in Logs/2026/07/2026-07-11.md, Entry 4.

### The astronomers' real night-planning practice (/mnt/scratch/xavier/Observing, read 2026-07-12)

Full detail in [`claudes_context.md`](claudes_context.md), section "Observing
archive". The durable, reusable facts:

- **Run-folder template** (`Observing/<Instrument>/<Run>/`, Run = `2022Oct`,
  `2023A`, `2025A/Feb26`; per-night subfolders for multi-night runs): night-plan
  `.docx` + Keck starlist `.txt` + `inst_config.txt` (SIAS submission) +
  `Targets.docx`/target `.xlsx` + finder-chart docs + (MOS) mask files
  (`.lst`/`.obj`/`.reg`) + `Obs_logs*.xlsx` + backup-target docs + README/
  strategy notes. Instruments in the archive: DEIMOS, HIRES, KCWI, LRIS,
  MOSFIRE, NIRC2, ToO — Keck-centric.
- **Keck starlist format** (spec, verified across DEIMOS/HIRES/LRIS/KCWI
  starlists):
  `name  HH MM SS.ss  ±DD MM SS.s  equinox  [keyword=value …]  [# comment]`
  e.g. `J073802.33+274948.81  07 38 02.33 +27 49 48.81 2000.00 rotdest=128.30
  rotmode=PA vmag=22.0`. Observed keywords only: `rotdest=` (PA deg),
  `rotmode=PA|pa`, `raoffset=`/`decoffset=` (arcsec, star→target),
  `vmag=`, `pmra=`/`pmdec=`, `lgs=`, `pa=`. Conventions: offset stars as
  companion entries `<name>_OFF` / `_o` / `_S1..S3` sharing the target's
  `rotdest`; slitmasks listed by mask ID with mask PA in `rotdest`; imaging
  mosaic pointings `_p1..p4`; `#` comment lines as section headers
  (# Longslit / # FRBs / # Standards) and per-line notes (z, mag, "Beginning
  of night standard").
- **Night-plan doc skeleton** (recurring across DEIMOS 2022Oct, LRIS 2023A,
  HIRES 2026A, KCWI 2018Oct): (1) title + Useful-links (instrument page,
  ucolick ephemeris, weather, starlist, finders); (2) ranked science
  priorities; (3) per-program setup tables (grating/filter/λc, dichroic,
  slicer, decker/XDANGLE, binning, focus); (4) twilight block — open at
  sunset, focus, standard star, align first mask, and a second standard at
  morning twilight; (5) **LST-keyed timeline** bounded by the 18°-twilight
  LST range ("Night 1 (Oct 26: LST = 21:06-7:09 [18deg])"), blocks of
  target/mask + setup + exposures×repeats + contingency notes, mid-night
  MIRA (focus) for DEIMOS; (6) afternoon calibration checklist (biases,
  ThAr arcs, flats, 11× counts); (7) Backup Plans; (8) SA questions (+ phone
  number); (9) appended troubleshooting/lessons (living document); (10)
  pre-run TODO list. HIRES formats the timeline as a table
  (UTStart-End | Target | RA | Dec | Setup | Exp | # | z | mag | Comments).
- **Offset-star acquisition procedure** (DEIMOS 2022Oct README): center the
  `_OFF` star, TO applies the starlist raoffset/decoffset holding the PA →
  faint target in slit with star on-slit as reference; 600–900 s exposures
  with on-the-fly reduction deciding continue/abort/coadd.
- **inst_config.txt** = Keck SIAS form: PI, run_date, n_nights, mode
  checkboxes, and numbered slots for slitmasks/gratings/filters (LRIS also
  grisms/dichroics/blue+red filters, per night) + `slitmask_deadline` —
  hardware is locked weeks ahead; the plan must fit the declared slots.
- **ToO plan** (MOSFIRE FRB 190614D, 2020-12-07): single compact doc —
  trigger/date/instrument, paper, ephemeris, Goals, Setup, Targets(+offset
  star), acquisition rules (offset star J_AB 16–18.5 within 1′, relaxable to
  2′/J=19.5; avoid bright stars — persistence; rotate slit to catch both
  candidates). No LST timeline.
- **Pre-run target tracking table** (DEIMOS 2023Dec `target_info.xlsx`):
  Target | mag | Filter | Survey Image | Exp time per mask | Grating combo |
  Redshift | mask status (Submitted for milling / Milled) | tentative obs
  time (HST) | Comments.
- **Facilities breadth** (`Observations/`): AAO, ALMA, Gemini-N/S, HST, JWST,
  Keck, Lick_Kast, Magellan, MeerTRAP_HighDM, MMT, NOT, Pepsi, SOAR, VLT.
- **Starlist equinox is not always 2000.0**: the blackbody-standard grid
  `DEIMOS/2022July/starlist_blackbody_0hr.txt` uses **equinox 2016.0**
  (Gaia epoch) coordinates with `pmra=/pmdec=` on every line — a starlist
  writer must carry (epoch, pm) per target, not hard-code J2000.

### Lessons from FFFF_PZ, JSkyCalc/thorsky & astropy docs (2026-07-11)

Full survey in [`claudes_context.md`](claudes_context.md); durable takeaways:

- **Definitions to adopt (JSkyCalc/thorsky):** rise/set at sun/moon altitude
  **−0.833°** (zd 90°50′); astronomical twilight at sun alt **−18°**; hour angle
  = LST − RA wrapped to ±12 h; near the horizon use a *true airmass* (Snell &
  Heiser 1968 polynomial) rather than plain sec z; moonlight via the
  **Krisciunas & Schaefer (1991)** V mag/arcsec² sky-brightness model, not just
  a separation cut; report parallactic angle (slit orientation) and barycentric
  time/velocity corrections.
- **Two-layer design (thorsky `Observation` class):** separate *instantaneous
  circumstances* (LST/HA/alt/az/airmass/parallactic/moon/sun) from *per-night
  events* (sunset, −18° twilights, night center, moon rise/set). The single best
  ranking scalar is `hrs_up` — hours tonight above the critical altitude,
  clipped to the twilights.
- **Run/plan data model (FFFF_PZ `FRBFollowUpResource`):** an observing run =
  instrument + UT validity window + N targets per mode (imaging/longslit/mask)
  + selection criteria (survey, status, tags, P_Ox, mag limits) + **max_AM**.
  The plan is a flat pandas table (`TNS, Resource, mode`); the observing log
  returns as a table (`..., Conditions, texp, date, success`) and is ingested
  back to advance per-target statuses (NeedImage → NeedSpectrum → done).
- **Feasibility-filter idiom (FFFF_PZ `frb_targeting.calc_airmasses`):** build
  `Observer` from `EarthLocation.from_geodetic(lon, lat, elev)`; loop nights
  bounded by `twilight_evening/morning_astronomical` (use `which='previous'` to
  step nights safely); sample every 30 min; one vectorized `SkyCoord` array for
  all targets; keep targets whose *minimum airmass over the run* ≤ max_AM.
- **Core astropy recipe:** `target.transform_to(AltAz(obstime=times,
  location=loc))` → `.alt`/`.az`/`.secz`; `get_sun(t)` / `get_body('moon', t,
  loc)` for dark time and moon separation; `Time.sidereal_time('apparent',
  lon)`; `Time.light_travel_time(coord, kind='barycentric')` for BJD. Caveats:
  `.secz` is plane-parallel; AltAz refracts only if `pressure` is supplied.
- **The gap night-planner fills:** FFFF_PZ stops at *which* targets are
  observable in a run; JSkyCalc is a calculator, not a scheduler. Sequencing
  targets *within* the twilight-bounded night is our job (start from
  astroplan's Scheduler).

### FFFF-PZ Resource creation for CHIME FRB runs (HOWTO + chime-ffff-pz, 2026-08-13 prep)

Sources: `context/HOWTOs/FFFF-PZ-HOWTO.pdf` (pp. 6–8) and
`/home/xavier/Projects/FRBs/chime-ffff-pz` (docs/, scripts/, data/Observing/).

- **Naming:** `<Site>-<Semester>-<run#>` (e.g. `Lick-2025B-3`); one Resource
  per observing *run* (1–3 nights), run # unpadded by convention and
  incrementing within the semester. The name keys everything downstream
  (targets/obsplan/logobs/finder commands, git branch, CANFAR folder).
- **Workflow:** (1) hand-write JSON at
  `chime_ffff_pz/data/Observing/<name>/<name>.json`; (2)
  `chime_ffff_pz_add_furesource <json>` (PUT `add_frb_resource/`, HTTP 200;
  often prints a benign "error"); (3) confirm on the web dashboard; (4)
  `chime_ffff_pz_targets <name>` (PUT `targets_from_frb_followup_resource/`,
  HTTP 201) → `<name>_targets.csv` in the same folder (columns: TNS, FRB
  RA/Dec/DM/survey/tags, Pri_*/Sec_* host name/RA/Dec/POx/mag/filter, mode,
  Resource). Selection is stochastic — rerun if too few. Later:
  `<name>_pending.csv` + `chime_ffff_pz_obsplan`, finders, starlist
  (`chime_ffff_pz_starlist <observatory>`), `chime_ffff_pz_logobs`.
- **JSON fields** (Lick/Kast practice, from Lick-2025B-*/2026A-2):
  `instrument="KAST"`, UT `valid_start/valid_stop` (loose window OK — server
  clips to astronomical twilight and applies the min-airmass filter),
  `num_targ_img/mask = 0`, `num_targ_longslit` = 20–30 requested (only ~4–6
  observed per Kast night), `max_AM = 2.0`, `frb_surveys = "all"`,
  `frb_tags/frb_statuses = null` (server default → NeedSpectrum for
  longslit), `max_mag` 19.5–20.5 (PATH primary host r); **omit `min_POx`** —
  setting it overrides the status logic (HOWTO warning).
- **Auth:** `FFFF_PZ_USER/PASS/URL` (`https://frb.chimenet.ca/f4pz/`) from
  `chime-ffff-pz/automation/config/secrets.env`; run in the `astro` conda
  env. Git: branch named after the resource, JSON PR'd to main (author runs
  git). CANFAR registration (`fu_resources.csv` + `canfar_upload -f`) only
  matters for post-run data upload.
- **Keck/LRIS Resource convention (differs from Lick/Kast, added 2026-09-10
  per the author):** always request masked targets too —
  **`num_targ_mask > 0`**, not `0` — alongside `num_targ_longslit`, since
  LRIS (unlike Kast) has a real MOS mode for mag>21 targets. **Never trust
  FFFF-PZ's own `mode` column for the longslit/mask split** — it tags every
  target pulled via `num_targ_longslit` as `"longslit"` regardless of
  magnitude (verified empirically, Keck-2026B-01 Prompt 9: 5/5 mag>21
  targets tagged `"longslit"`). Apply your own mag>21 cut downstream
  instead (see `estimate_mos_exposure()` /
  `LRIS_LONGSLIT_MAG_LIMIT` in `night-planner/scripts/keck_2026oct02_calculations.py`).
- **FFFF-PZ sampling is stochastic per-pull, not just per-Resource:**
  re-running `chime_ffff_pz_targets` on an unchanged Resource, or one with
  only `num_targ_mask`/`num_targ_longslit` tweaked, can return a smaller or
  differently-composed set each time — always re-sync any local copy of a
  `<name>_targets.csv` before trusting downstream numbers.
- **Observing spreadsheet ("possible targs"):** each Lick/Kast run folder in
  obs_docs carries a `possible_targs.xlsx` (sheet `possible_targs`; columns
  TNS, RA_HMS, DEC_DMS, Epoch, Pri_mag, Sec_mag) — primary-host coords in
  sexagesimal, Epoch 2000.0, sorted by RA. Build it from the targets CSV with
  `night_planner/make_lick_possible_targs.py`, which also applies the
  **Shane pointing limit: no targets at Dec > +82°** (author, Q7.1 of the
  2026-08-13 plan). Note the server may return fewer targets than
  `num_targ_longslit` requests (e.g. 14 of 15 for Lick-2026B-01).

### Keck/LRIS Mode Summary (2026-09-09)

**LRIS Observing Modes:**
- **LONGSLIT:** mag ≤ 21 (practical limit for reasonable S/N in ~1h)
- **MOS (slitmask):** mag > 21 requires pre-milled masks (weeks lead time)
- **IMAGING:** Available for acquisition, photometry, or gap-filling

**LRIS Exposure Estimates (longslit):**
| mag_r | Red arm | Blue arm | Total |
|-------|---------|----------|-------|
| ≤14 | 2×180s | 2×180s | 11 min |
| 14-17 | 2×600s | 2×600s | 25 min |
| 17-19 | 3×600s | 3×600s | 35 min |
| 19-20.5 | 4×600s | 4×600s | 45 min |
| 20.5-21 | 5×600s | 5×600s | 55 min |

**Keck Pointing Limits:**
- Dec ≥ -37° (horizon limit)
- HA: -5.5h to +5.5h
- Zenith blind spot negligible

**Keck vs Lick Target Compatibility:**
- Lick (lat 37°) can observe Dec up to +82°
- Keck (lat 20°) struggles with Dec > 70° (high airmass)
- Targets at Dec > 82° excluded from Lick are observable from Keck at AM ~2.4
- For Keck runs, query FFFF-PZ with Dec < 60° for optimal coverage

### Keck Observatory coordinates (verified 2026-09-11)

`EarthLocation`: **lat 19.828333°N, lon -155.478333°W, height 4160 m**
(matches `astropy.coordinates.EarthLocation.of_site('keck')`, sourced from
the IRAF Observatory Database — the canonical reference, not a web search).
An earlier hardcoded value used lat 19.8263° (wrong by ~7 arcsec); fixed in
both Keck scripts. If a coordinate for Keck ever needs re-deriving, check
`EarthLocation.of_site('keck')` first rather than searching the web.

### Keck-specific corrections to the Lick-derived scripts (2026-09-10)

The Keck scripts (`scripts/keck_2026oct02_calculations.py`,
`build_keck_night_plan.py`) started as adaptations of the Lick/Kast scripts
and initially carried over Lick-shaped assumptions. Two Keck-specific facts
now implemented:

- **Target-selection rule:** Keck's 10m aperture shouldn't re-observe what
  Lick's 3m already reaches. Rule: keep a target only if `mag_r > 19.0`,
  unless `Dec > 82°` (Lick/Shane's pointing limit — unreachable from Lick at
  any magnitude). `KECK_MAG_FAINT_LIMIT = 19.0`, `LICK_DEC_LIMIT = 82.0`,
  `passes_keck_target_selection()`.
- **Keck I Nasmyth-deck vignetting (real limits, not a generic alt floor):**
  source, Keck Telescope Pointing Limits
  (www2.keck.hawaii.edu/inst/common/TelLimits.html). Keck I's Nasmyth deck
  blocks the beam in a **fixed azimuth band, az 5.3°-146.2°** (N through E to
  SE) unless altitude ≥ 33.3°; elsewhere the floor is ~18°. This band is N/E
  for Keck I specifically — **Keck II is blocked S/W instead** (opposite
  side). LRIS is on Keck I, so a target **rising** through the NE/E sits in
  the blocked band at low altitude and must climb to 33.3° before it clears
  the deck ("wait for the target to rise"); a target **setting** in the W/SW
  clears at the normal 18° floor, so setting targets are the easier catch on
  Keck I. Implemented as `check_keck1_nasmyth_vignetting(az, alt)`, folded
  into `check_keck_limits()` (now takes `az` too).
- **Effect on the Oct 2, 2026 plan:** applying both to the (Lick-sourced)
  Lick-2026B-01 target pool dropped it from 6 targets/2.6h to **1 target/11
  min (2% utilization)** — most of the pool is either too bright (mag≤19,
  Dec≤82°) or fails the real Nasmyth check while rising. This exposed that
  the target *pool* itself needs a Keck-specific FFFF-PZ query (mag>19,
  Dec<60°), not just Keck-corrected scheduling logic. Full detail:
  `Night_plans/Keck-2026B-01/KECK_LRIS_2026OCT02_SUMMARY.md`, Prompt 5.

### Created a real Keck-2026B-01 FFFF-PZ Resource (2026-09-10, Prompt 6)

Followed the standard FFFF-PZ Resource workflow (see "FFFF-PZ Resource
creation" above) to replace the filtered-Lick-pool workaround with a genuine
Keck-native target list:
`chime-ffff-pz/chime_ffff_pz/data/Observing/Keck-2026B-01/Keck-2026B-01.json`
— `instrument="LRIS"`, `min_mag=19.0`/`max_mag=null` (the mag>19 rule
implemented server-side, matching the convention already used by
`Keck-2026A-8`/`Keck-2025B-2`), `num_targ_longslit=20`, `max_AM=2.0`. Ran
`chime_ffff_pz_add_furesource` then `chime_ffff_pz_targets Keck-2026B-01`
(both succeeded); copied the resulting `_targets.csv` (15 targets) into
`night-planner/Night_plans/Keck-2026B-01/` and repointed
`scripts/keck_2026oct02_calculations.py` at it.

- **Credentials note:** no `automation/config/secrets.env` exists on this
  machine (only the template + a `secrets_test.env`). `FFFF_PZ_USER/PASS/URL`
  are instead exported directly in `~/.bashrc`, pointing at a docker-hosted
  instance (`http://0.0.0.0:8000/`) — confirmed live and already holding real
  runs (e.g. `Lick-2026B-01`). `add_modify_resource.py`/`targets.py` read
  those env vars directly, no secrets file required. Asked the author before
  writing anything since it's a real write to a shared server; the author
  pointed at `.bashrc` as the credential source.
- **Bug found and fixed:** `select_targets_for_night()` was scheduling
  mag>21 (MOS-mask-required) targets into the night's timeline as 0-minute
  "observations" — masks take weeks to mill, so they can't be used this run.
  Now filtered out of the schedulable set (`lris_mode == 'MOS (mask
  required)'`); they still appear in the separate MOS-planning warning for
  tracking toward a future run.
- **Result:** of 15 Keck-native targets, 10 pass sky-observability
  (HA + Nasmyth-deck), but 6 of those are MOS-only (mag>21) — leaving 4
  real longslit targets, **3.3h science / 9.7h dark (35% utilization)**, up
  from 1 target/2% on the filtered Lick pool. Confirms: a dedicated
  Keck-specific FFFF-PZ Resource beats filtering another site's list. Full
  detail in `KECK_LRIS_2026OCT02_SUMMARY.md`, Prompt 6.
- **Gotcha:** `Keck-2026B-01_targets.csv` has 16 *lines* but only 15
  *targets* (1 header row) — easy to miscount by eye. The 15→4 funnel (5 fail
  sky-observability, 6 of the remaining 10 are MOS-only/mag>21) is spelled
  out as an explicit diagram at the top of the Target Analysis section in
  `KECK_LRIS_2026OCT02_SUMMARY.md` — point there first if this comes up again
  instead of recounting from the CSV.

### Real LRIS exposure-time calculator (2026-09-10, Prompt 7)

The `estimate_lris_exposure()` magnitude-bucket table (adapted from an
equally hand-wavy Kast heuristic via an arbitrary "LRIS is ~2x more efficient
than Kast" fudge factor) had no basis in throughput/sky/read-noise physics.
Replaced it with `scripts/lris_etc.py`, a client for the **real UCO/Lick web
S/N calculator** at etc.ucolick.org — the same engine behind the official
web LRIS/Kast/DEIMOS/ESI/HIRES ETCs, and callable directly as JSON
(`POST https://etc.ucolick.org/web_s2n/gen_inst_s2n`, no auth), not just
through the browser form.

- **Setup used:** grism 600/4000 (blue), grating 600/7500 centered ~7200 Å
  (red), dichroic D560, slit 1.0", binning 2x2 — the author's actual standard
  Keck/LRIS FRB-host config. Correcting a stale assumption: this repo
  previously documented 400/3400 blue / 400/8500 red, which the real ETC
  can't even model (see next point).
- **ETC coverage gotcha:** the ETC's blue-grism dropdown only *works* for
  B300 (300/5000) and B600 (600/4000) — B400 (400/3400) and B1200 return an
  **empty result with no error message** (`errormsg=""`, zero-length `s2n`
  array). Always check the array is non-empty, not just the error field,
  when validating this API. Red-grating options (600/7500, 600/10000,
  1200/9000, 400/8500, 831/8200) all work; only D560 dichroic is modeled.
- **Target S/N convention (per the author):** median S/N = 5 per pixel,
  continuum, measured in a blue window (4200-5200 Å) and a red window
  (6500-7500 Å) separately; the longer-required arm sets the simultaneous
  dual-beam wall-clock time (both arms expose together). Split into ≥2
  sub-exposures of ≤600s each for cosmic-ray rejection.
- **Method:** `required_exptime()` uses real ETC calls at each step (S/N≈√t
  only picks the *next exptime to try*, never assumed as the final answer),
  iterating to within 5% of the target S/N.
- **TLS note:** etc.ucolick.org's cert is genuinely CA-issued
  (InCommon/Sectigo) but the server doesn't send its intermediate — confirmed
  via `openssl s_client -showcerts` before reaching for `verify=False`.
  Fetched the one missing intermediate from the leaf cert's `Authority
  Information Access` CA-issuers URL and ship it alongside `certifi`'s bundle
  (`scripts/certs/ca_bundle_with_incommon.pem`) so verification still works
  properly.
- **Result:** at S/N=5, real LRIS exposures for mag 20-21 targets are ~1-3
  min of science time (7-11 min incl. overhead), not the 45-55 min the old
  heuristic gave — roughly a 15x overcorrection, consistent with Keck's 10m
  vs. Lick's 3m being ~11x the collecting area (the old heuristic's flat "2x"
  fudge factor was never close). Rerunning the Oct 2, 2026 plan dropped total
  science time from 3.3h to 0.6h for the same 4 targets.
- **New implication:** with real (short) exposure times, utilization is now
  limited by *target count*, not exposure time — the plan uses only 6% of
  the night with just 4 targets in hand. Future Keck FFFF-PZ pulls should
  request many more targets (`num_targ_longslit` well above 20), since each
  one is now cheap in telescope time. Full detail in
  `KECK_LRIS_2026OCT02_SUMMARY.md`, Prompt 7.

### Correction: target S/N must be per single sub-exposure, not combined (2026-09-10, Prompt 8)

The author caught a real bug in the Prompt 7 model, not just a disagreement
of taste. `estimate_lris_exposure_real()` had searched for one *combined*
exposure time hitting `target_sn` (5), then divided that combined time across
sub-exposures — so each individual frame actually carried *less* than the
target S/N (e.g. "2×170s" each only reached S/N≈3, not 5). The author's own
recalled minimum for mag 21 ("≥15 min per exposure, ≥3 exposures") lines up
almost exactly with **S/N≈10 measured per single exposure** — confirmed
directly against the ETC's real S/N-vs-exptime curve (60s→1.3, 170s→3.0,
300s→4.5, 600s→7.0, 900s→8.9, 1200s→10.5 at mag 21, red arm).

**Fixed model:** `target_sn` (now default **10**) is the S/N required of one
single sub-exposure; the sub-exposure count is a separate fixed **minimum of
3** (cosmic-ray rejection — 2 frames can only flag a CR discrepancy, 3+ lets
you median-reject it; not derivable from S/N). Total time per target is now
`3 x (single-exposure time to hit S/N=10)`, not a combined time split three
ways.

**Result:** total science time for the Oct 2, 2026 plan's same 4 targets rose
from 0.6h (Prompt 7's under-delivering version) to **2.3h / 9.7h (23%
utilization)** — e.g. mag 21 (FRB20250408A): 3×1060s (58 min), vs. 2×170s
(10.7 min) under the buggy version and 45-55 min under the original
heuristic. 23% is the number that should stand. Full detail in
`KECK_LRIS_2026OCT02_SUMMARY.md`, Prompt 8.

**General lesson:** "combined S/N across N frames" and "S/N per single
frame, N times" are different targets — a real ETC call can still be wired
into the wrong quantity. When a domain expert's gut-check number disagrees
with a calculator's output by a large, consistent factor, reverse-engineer
what quantity their number is actually describing before assuming either
side is simply wrong — it pinned down the missing parameter here almost
exactly.

### MOS-required targets are scheduled directly, not just flagged (2026-09-11, Prompt 10)

Per the author: a mag>21 target isn't excluded from the night plan just
because it needs a mask -- it goes into the schedule with its real
allocated time (`estimate_mos_exposure()`, ~1-2h), on the working
assumption a mask can be milled before the run. `select_targets_for_night()`
in `scripts/keck_2026oct02_calculations.py` no longer drops
`lris_mode == 'MOS (mask required)'` rows before scheduling. MOS rows are
tagged `[MOS - MASK REQUIRED]` / `MASK REQUIRED` in the console timeline,
starlist, and Excel so it's unambiguous at the telescope which targets are
contingent on a mask actually existing by run night.

Added while doing this: skip-reason logging in the scheduler (it silently
`continue`d before). This immediately surfaced a real geometric constraint
that had been invisible: a target whose required exposure time exceeds what
fits in its own airmass<2.0 window gets correctly dropped, and now says why
(e.g. "needs 120 min but only 70 min left in its AM<2.0 window"). Lesson:
a silent `continue` in a scheduler hides genuine constraints, not just
uninteresting ones -- log the reason at every skip point.

## Version History

- **v0.1 — 2026-07-11:** Created during start-up prompt 1. Seeded project purpose,
  working conventions, and repository layout. Astronomy/night-planning knowledge
  section is a placeholder pending the astronomers' input.
- **v0.2 — 2026-07-11:** Start-up prompt 2 ("Basic start up"). Added Python
  packaging scaffolding (setup.py/setup.cfg/pyproject.toml, requirements.txt,
  `night_planner/` package, `tests/`) following the author's linetools/XAI
  convention. Recorded those conventions and the settings.json recommendation
  (copy XAI's — already in place). Chose astronomy deps: numpy, astropy,
  **astroplan** (observability/scheduling), matplotlib, pyyaml.
- **v0.3 — 2026-07-11:** Start-up prompt 3 (1st task under "Skills"). Copied the
  `grill-me` and `critical-partner` skills verbatim from ClimateIntelligence into
  `.claude/skills/` (both single-file SKILL.md, project-agnostic, no edits needed).
- **v0.4 — 2026-07-11:** Start-up prompt 4 (2nd task under "Skills"). Web-searched
  for skills/tools to help Claude learn telescope night planning; recorded findings
  in the "Skills & tools" subsection above (astroplan core; Astropy & SIMBAD agent
  skills; ESO p2 / Gemini OT as structural models). No skills installed yet —
  presented recommendations to the author for a decision.
- **v0.5 — 2026-07-11:** Executed context_prompts.md Code prompt 1 on the Fable 5
  model. Examined FFFF_PZ and JSkyCalc repos + astropy docs; wrote
  context/claudes_context.md and recorded new night-planning concepts here.
- **v0.6 — 2026-07-11:** Executed context_prompts.md Websites/Ephemeris prompt 1
  on the Fable 5 model. Documented the UCO/Lick & Keck calendar ephemeris sites
  in context/claudes_context.md.
- **v0.7 — 2026-07-11:** Executed context_prompts.md Websites/Instrument-manuals
  prompt 1 on the Fable 5 model. Summarized Lick/Keck/Palomar/Gemini instruments
  in context/claudes_context.md.
- **v0.8 — 2026-07-12:** Executed context_prompts.md Night-plans prompt 1 on the
  Fable 5 model. Summarized the /mnt/scratch/xavier/Observing archive (run-folder
  convention, Keck starlist format, night-plan doc anatomy) into
  context/claudes_context.md.
- **v0.9 — 2026-07-13:** Executed context_prompts.md Night-plans prompt 2 on the
  Fable 5 model — synthesized targets & observing strategies into the Responses
  subsection of claude_prompts/context_prompts.md, with pointers into the context
  and brain files. Added the Gaia-epoch (equinox 2016.0 + proper motions)
  starlist fact noted while re-verifying archive files.
- **v0.10 — 2026-08-13:** Lick 2026-08-13 plan prep (Fable 5). Read the
  FFFF-PZ HOWTO PDF and the chime-ffff-pz repo; added the "FFFF-PZ Resource
  creation" subsection (naming convention, JSON fields, add_furesource →
  targets workflow, auth, per-night Kast capacity). Posed Q&A in
  claude_prompts/night_plans/lick_2026aug13.md; no Resource generated yet.
- **v0.11 — 2026-08-10:** Generated the Lick-2026B-01 Resource (Fable 5):
  wrote/uploaded the JSON (clean success), pulled 14 targets, and built the
  observing spreadsheet via the new `night_planner/make_lick_possible_targs.py`
  (Dec ≤ +82° Shane cut dropped 2 targets → 12 in
  Night_plans/Lick-2026B-01/). Added the possible-targs spreadsheet
  convention and the Dec +82° pointing limit above.
- **v0.12 — 2026-08-10:** Built the Lick-2026B-01 Night plan (Fable 5) via the
  new `night_planner/make_lick_night_plan.py` →
  `Night_plans/Lick-2026B-01/Lick_2026B-01_Night_plan.xlsx`. Departure from
  the archive template (per the author's explicit prompt): science sheets are
  named per target TNS (12 sheets, RA order) instead of per night. Checklist
  copied from `Lick_2026A-4_Night_plan.xlsx` with Done flags reset; exposure
  times and Kast red/blue setup left blank (deferred to the observer); watch
  out that the archive template stores some sexagesimal DEC values as Excel
  time cells (negative decs silently lose their sign) — always write RA/DEC
  as text.
- **v0.13 — 2026-08-10:** Added Kast exposure estimates to the Lick-2026B-01
  Night plan (Fable 5) via the new `night_planner/estimate_kast_exposures.py`:
  d57 / red 600/7500 / blue 600/4310 / 2" slit, with the r-mag → total-
  integration heuristic calibrated to 9 prior Lick/Kast plans (recorded above
  under Astronomy knowledge). Filled red side / blue side / Duration on each
  target's "Science + overhead" row, set slew rows to 0:05, and stamped the
  Kast setup note in cell Q1 of every target sheet; Redshift left blank
  (unknown pre-obs).
- **v0.14 — 2026-08-10:** Wrote the Lick-2026B-01 target-selection report
  (Fable 5) into the prompt file's Reports section. Durable fact: CHIME FRB
  tag definitions (CHIME-Blind/-Repeater/-Unbiased/-Lowz/-GBO/-Bright/-KKO,
  etc.), including their stochastic-draw weights and per-sample cuts, live in
  `chime-ffff-pz` at `chime_ffff_pz/data/Criteria/*.json`.
- **v0.15 — 2026-08-11:** REGENERATED Lick-2026B-01 Night plan (Sonnet 4.5
  via lordrick). Corrected sheet structure: date-named sheets ("August 13th")
  not target-named, matching the Lick-2026A-4 template. ~~Added full Lick/Shane
  pointing constraints: **Dec ≤ +82°**, **RA ≥ 5h** (no targets west of 5h),
  **HA ≥ -3:45h** (cannot observe west of 3h45m HA).~~ **[WRONG - see v0.16]**
  Created automated calculation scripts: `scripts/lick_2026b01_calculations.py`
  (LST/twilight/airmass/target-selection) and `scripts/build_night_plan.py`
  (Excel generation from selected targets). For Aug 13, 2026: **18° astronomical
  twilight** 21:38 PDT / 20:38 PST (LST 18h02m) to 04:46 PDT / 03:46 PST
  (LST 1h11m), timeline starts 21:30 PDT. **Lick calendar timezone
  convention:** tables use "PST" label year-round (actual UTC-8), even in
  summer when local time is PDT (UTC-7); verified against
  ucolick.org/calendar (2-3 min agreement). ~~Of 12 viable targets (after Dec
  cut), 8 pass all pointing limits; selected 6 for night 1 (FRB20230729A,
  FRB20200621B, FRB20240324A, FRB20260215E, FRB20201128D, FRB20250202A)
  totaling ~520 min for 7.1h night.~~ **[4 of 6 targets WRONG - see v0.16]**
  Night plan → `Night_plans/Lick-2026B-01/Lick_2026B-01_Night_plan.xlsx`.
- **v0.16 — 2026-08-12:** CORRECTED Lick-2026B-01 Night plan (Sonnet 4.5
  via lordrick). **CRITICAL FIX:** v0.15 had wrong Shane pointing limits.
  **CORRECT constraints:** (1) **Dec ≤ +82°**, (2) **HA: -5h ≤ HA ≤ +3.75h**
  (symmetric - cannot point >5h east OR >3.75h west of meridian), (3) **NO
  RA limits** - observable RAs depend on LST and time of year. **Hour angle
  convention:** HA = LST - RA (±12h); negative HA = east of meridian (before
  transit), positive HA = west (after transit). Of 12 viable targets (after
  Dec cut), **only 6 pass HA limits during the night**: 2 evening (RA 15-16h:
  FRB20230729A, FRB20200621B), 4 morning (RA 0-5h: FRB20200702C, FRB20250902A,
  FRB20230805A, FRB20231223B), totaling **420 min** (7.0h). **Rejected:** 6
  targets at RA 9-13h (always HA > +3.75h, too far west). v0.15 incorrectly
  selected 4 of these rejected targets! Created
  `scripts/observable_ra_calculator.py` showing time-dependent RA windows.
  Full corrections in `Night_plans/Lick-2026B-01/CORRECTIONS_SUMMARY.md` and
  `HOWTO_night_plan_creation.md`. **KEY LESSON:** Always verify telescope
  mechanical limits with observer - HA constraints create LST-dependent RA
  windows, not static forbidden zones.
- **v0.17 — 2026-09-09:** Created Keck/LRIS night plan for Oct 2, 2026 (Opus 4.5
  via lordrick). New scripts: `scripts/keck_2026oct02_calculations.py` and
  `scripts/build_keck_night_plan.py`. Added LRIS mode summary (longslit mag ≤21,
  MOS for fainter, imaging available). Discovered Lick targets (high Dec) poorly
  suited for Keck (lat 20°) - only 6/14 observable. Added Lick-excluded target
  FRB20250102C (Dec 84°, mag 13.3) observable from Keck at AM ~2.5. Output in
  `Night_plans/Keck-2026B-01/`. Recommendation: query FFFF-PZ with Dec < 60° for
  proper Keck coverage.
- **v0.18 — 2026-09-10:** Corrected Keck-specific params in
  `scripts/keck_2026oct02_calculations.py` (Sonnet 5). Added the
  mag>19-unless-Dec>82° target-selection rule and the real Keck I Nasmyth-deck
  vignetting check (researched at www2.keck.hawaii.edu/inst/common/TelLimits.html
  — az 5.3-146.2° needs alt≥33.3°, N/E for Keck I, opposite for Keck II),
  replacing the old generic alt<10° floor. Regenerated all outputs; result
  dropped from 6 targets/2.6h to 1 target/11 min (2% utilization), exposing
  that the Lick-2026B-01 pool itself is unsuited for Keck and a fresh
  Keck-specific FFFF-PZ query is the real fix. Full detail recorded above
  under "Keck-specific corrections to the Lick-derived scripts".
- **v0.19 — 2026-09-10:** Created a genuine `Keck-2026B-01` FFFF-PZ Resource
  (Sonnet 5) per the standard workflow — folder + JSON
  (`instrument=LRIS`, `min_mag=19.0`) in `chime-ffff-pz/.../Observing/`,
  `chime_ffff_pz_add_furesource` + `chime_ffff_pz_targets`, copied the
  15-target pull into night-planner and repointed
  `keck_2026oct02_calculations.py` at it. Also fixed a real scheduling bug
  (MOS-mask/mag>21 targets were being scheduled as 0-min "observations").
  Result: 4 real longslit targets, 3.3h/9.7h (35% utilization) — confirms a
  Keck-native pull beats filtering the Lick list. Full detail above under
  "Created a real Keck-2026B-01 FFFF-PZ Resource".
- **v0.20 — 2026-09-10:** Replaced the magnitude-bucket LRIS exposure
  heuristic with a real physical calculator (Sonnet 5). New
  `scripts/lris_etc.py` calls the real UCO/Lick web S/N calculator
  (etc.ucolick.org, JSON API) targeting S/N=5/pixel continuum per the
  author, using the author-confirmed real setup (grism 600/4000, grating
  600/7500 ~7200Å — corrected from a stale 400/3400/400/8500 assumption).
  Result: exposure times for mag 20-21 targets dropped from a 45-55 min
  heuristic to 7-11 min real (~15x), consistent with Keck's ~11x collecting
  area over Lick that the old flat "2x" fudge factor never captured. Total
  science time for the Oct 2, 2026 plan: 3.3h → 0.6h (same 4 targets) —
  utilization is now target-count-limited, not exposure-time-limited. Full
  detail above under "Real LRIS exposure-time calculator".
- **v0.21 — 2026-09-10:** Fixed a real bug the author caught in v0.20's
  model (Sonnet 5): target S/N was being hit *combined* across sub-exposures,
  so each individual frame under-delivered. Reverse-engineered the author's
  recalled "≥15 min/exposure, ≥3 exposures" at mag 21 against the ETC's real
  S/N-vs-exptime curve → confirmed S/N≈10 per *single* exposure was the
  actual intended target. Fixed `estimate_lris_exposure_real()`: target_sn=10
  per single sub-exposure, fixed minimum of 3 sub-exposures (CR-rejection,
  not S/N-derived). Science time for the same 4 targets: 0.6h → 2.3h (23%
  utilization) — the number that should stand. Full detail above under
  "Correction: target S/N must be per single sub-exposure, not combined".
- **v0.22 — 2026-09-10:** Added real MOS-mask handling and an explicit
  `info` column (Sonnet 5), per the author. New
  `estimate_mos_exposure()`: mag≤23→1h, 23-24→1.5h, ≥24→2h on-target time
  once a mask is milled (an operational bucket, not physics; 23-24 split
  point is this project's own interpolation of the author's "1.5-2h fainter"
  range). `target_analysis.csv` now carries an `info` column flagging every
  mag>21 target regardless of FFFF-PZ's own tag. Confirmed empirically that
  FFFF-PZ's `mode` column is untrustworthy for the longslit/mask split (see
  new "Keck/LRIS Resource convention" note above) — always request
  `num_targ_mask>0` going forward and apply our own mag cut regardless. Also
  synced a fresh, smaller (10-target) FFFF-PZ pull the author had made
  directly by editing the Resource JSON — re-ran the full pipeline: 2
  targets schedulable tonight (FRB20250408A, FRB20260418B), 1.4h/9.7h (14%
  utilization), 4 real MOS candidates with real time estimates attached.
  Full detail in `KECK_LRIS_2026OCT02_SUMMARY.md`, Prompt 9.
- **v0.23 — 2026-09-11:** Per the author, MOS-required targets now go
  *into* the actual schedule with their allocated time (Sonnet 5), not just
  a separate warning — v0.22 had computed real MOS timing but still excluded
  them from `select_targets_for_night()`'s output. Removed that exclusion
  (`estimate_lris_exposure()` already dispatches correctly); tagged MOS rows
  `[MOS - MASK REQUIRED]` / `MASK REQUIRED` in the console timeline,
  starlist, and Excel so it's unambiguous at the telescope which targets
  still need a milled mask. Also added skip-reason logging to the scheduler
  (previously silent), which immediately surfaced a real constraint:
  FRB20250411A (mag 25.6, needs the full 2h MOS bucket) doesn't fit its own
  ~100-min airmass<2.0 window once other targets claim earlier time, so it's
  correctly excluded — not a bug, a genuine geometric conflict. Result: 5
  targets in the plan (2 longslit + 3 MOS), 4.4h/9.7h (45% utilization), up
  from 2 targets/14%. Full detail in `KECK_LRIS_2026OCT02_SUMMARY.md`,
  Prompt 10.
- **v0.24 — 2026-09-11:** Fixed a real Keck site-coordinate error (Sonnet
  5), per the author's question. `KECK = EarthLocation(...)` in both Keck
  scripts had latitude 19.8263°N; checked against
  `astropy.coordinates.EarthLocation.of_site('keck')` (IRAF Observatory
  Database, the canonical source) and found the correct value is
  19.828333°N — off by ~7 arcsec (~220 m). Longitude (-155.4783°) and
  elevation (4160 m) were already exactly right. Fixed both files with a
  comment citing the verification source. Impact on this run: negligible
  (same twilight times, same 5 targets, airmass shifted only in the
  4th-5th decimal) — fixed anyway since a hardcoded site constant should be
  correct regardless of whether current targets are sensitive to the error.
  Full detail in `KECK_LRIS_2026OCT02_SUMMARY.md`, Prompt 11.
