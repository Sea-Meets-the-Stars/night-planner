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
