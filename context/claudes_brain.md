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
- **Observing spreadsheet ("possible targs"):** each Lick/Kast run folder in
  obs_docs carries a `possible_targs.xlsx` (sheet `possible_targs`; columns
  TNS, RA_HMS, DEC_DMS, Epoch, Pri_mag, Sec_mag) — primary-host coords in
  sexagesimal, Epoch 2000.0, sorted by RA. Build it from the targets CSV with
  `night_planner/make_lick_possible_targs.py`, which also applies the
  **Shane pointing limit: no targets at Dec > +82°** (author, Q7.1 of the
  2026-08-13 plan). Note the server may return fewer targets than
  `num_targ_longslit` requests (e.g. 14 of 15 for Lick-2026B-01).

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
