# Claude's Context — night-planner

Product context for the **night-planner** project: a survey of two external code
bases relevant to telescope night planning, plus the astropy primitives they (and
we) build on. Written 2026-07-11 by executing `claude_prompts/context_prompts.md`
(Code section, prompt 1). Everything below was read directly from the repos/docs
cited; where I did not verify a detail I say so.

---

## 1. FFFF_PZ — FRB follow-up target & observation management

**Repo:** <https://github.com/FRBs/FFFF_PZ> — a fork of **YSE_PZ** (Coulter et
al. 2023, arXiv:2303.02154), the Young Supernova Experiment's Django-based
transient survey management platform, adapted for **FRB follow-up by "F4"**
(the FRB follow-up collaboration). It is a full web application (Django + MySQL,
Docker-deployed) whose job is *human-in-the-loop* target management: ingest
transient alerts, associate host galaxies, and drive follow-up decisions.

### Architecture (night-planning-relevant slice)

All application code lives in the Django app `YSE_App/`. FRB-specific logic is
in top-level `YSE_App/frb_*.py` modules; the ORM data model is in
`YSE_App/models/`.

**Facility data model** (a chain of Django models):

- `models/observatory_models.py` — `Observatory`: name, `utc_offset`,
  `tz_name`, plus daylight-savings fields (`DLS_utc_offset`, `DLS_start/end`).
- `models/telescope_models.py` — `Telescope`: FK to Observatory + `latitude`,
  `longitude`, `elevation` (the geodetic inputs for airmass computations).
- `models/instrument_models.py` — `Instrument` (FK to Telescope) →
  `InstrumentConfig` → `ConfigElement` (many-to-many): instrument setups as
  composable named elements.
- `models/telescope_resource_models.py` — `TelescopeResource` (telescope + PI +
  groups + `begin_date_valid`/`end_date_valid`, i.e. a semester allocation) with
  subclasses **`ToOResource`** (awarded/used ToO hours *and* triggers),
  **`QueuedResource`** (awarded/used hours), **`ClassicalResource`** with
  `ClassicalObservingDate` (specific scheduled nights, each with a
  `ClassicalNightType`). This captures the three professional observing modes:
  classical / queue / ToO.

**The observing-run model** — `models/frbfollowup_models.py`:

- `FRBFollowUpResource` ≈ *one observing run*: `name`, `instrument` (FK),
  `valid_start`/`valid_stop` (UT datetimes), **per-mode target counts**
  (`num_targ_img`, `num_targ_longslit`, `num_targ_mask`), **`max_AM`** (maximum
  acceptable airmass), and target-selection criteria: `frb_surveys`,
  `frb_tags`, `frb_statuses`, `min_POx` (minimum PATH host-association
  probability P(O|x)), `min_mag`/`max_mag` host-magnitude cuts. Optional
  `obs_type` (Classical/ToO/Queue), `PI`, `Program`, `Period` (e.g. "2024A").
- Key methods: `get_frbs_by_mode()` (filter candidates, apply the airmass
  feasibility cut, split by mode) and `generate_target_table()` → a **pandas
  DataFrame** of observable targets for the run.

### Target selection & the airmass filter — `YSE_App/frb_targeting.py`

- `calc_airmasses(frb_fu, gd_frbs)` — the core visibility computation, built
  directly on **astroplan + astropy**:
  1. `EarthLocation.from_geodetic(telescope.longitude*u.deg, telescope.latitude*u.deg, telescope.elevation*u.m)`
     → `astroplan.Observer(location=..., timezone="UTC")`.
  2. Loop over the nights between `valid_start` and `valid_stop`, bounding each
     night with `Observer.twilight_evening_astronomical()` /
     `twilight_morning_astronomical()` (note the `which='previous'` idiom to
     step night-by-night without an infinite loop).
  3. Sample every **30 minutes**; `altaz = tel.altaz(time, frb_coords)`
     (vectorized over all targets at once via a single `SkyCoord` array);
     airmass computed as plain **sec z** = `1/cos(zenith)`, set to 1e9 below
     the horizon.
  4. Return the **minimum airmass each target reaches during the run**; the
     caller keeps targets with `min_AM <= resource.max_AM`.
- `targetfrbs_for_fu(frb_fu)` — Django QuerySet filtering by survey, transient
  status (default: `NeedImage` / `NeedSpectrum` / `NeedSecondary`), and tags.
- `grab_targets_by_mode(...)` — mode logic: **imaging** targets are those with
  status `NeedImage` (no host identified yet); **longslit** targets need status
  `NeedSpectrum` plus host `P_Ox > min_POx` and magnitude cuts; **mask** not
  implemented.
- `select_with_priority(...)` / `assign_probs(...)` — when more targets pass
  than requested (`num_targ_*`), draw probabilistically (uniform random vs
  tag-derived priority probabilities, looping until N selected). Selection is
  stochastic, not an optimizer.
- `target_table_from_frbs(frbs, mode)` — builds the target table rows: TNS
  name, FRB RA/Dec, DM, survey, tags, and the **top-two host candidates by
  PATH P(O|x)** (name, RA/Dec, P_Ox, magnitude+filter), plus `mode`.

### Plan/log round-trip — `YSE_App/frb_observing.py`

- `ingest_obsplan(obsplan: pandas.DataFrame, user, iresource)` — a *night plan*
  is a simple table with columns `TNS`, `Resource`, `mode`. Ingest scrubs
  previous pending requests for the resource, validates each target's status
  against its mode, creates `FRBFollowUpRequest` rows, and updates statuses.
  Returns `(int, str)` HTTP-like status codes.
- `ingest_obslog(obslog: pandas.DataFrame, ...)` — the *observing log* comes
  back as a table with columns `TNS, Resource, mode, Conditions, texp, date,
  success`, creating `FRBFollowUpObservation` rows and advancing each
  transient's status (lifecycle logic in `YSE_App/frb_status.py`:
  NeedImage → NeedSpectrum → ... driven by what data exist).

### What FFFF_PZ teaches night-planner

- The **shape of a plan**: run (instrument + UT validity window + N targets per
  mode + selection criteria + max airmass) → filtered target table → priority
  down-select → flat table handed to the observer → log table ingested back.
- The **min-airmass-over-run feasibility filter** (twilight-bounded, 30-min
  sampling, vectorized SkyCoord) is a compact, proven astroplan pattern we can
  reuse almost verbatim.
- Facility config as Observatory → Telescope(lat/lon/elev) → Instrument →
  Config hierarchy; observing time as Classical/Queue/ToO resources.
- Highly relevant socially: same FRB community (fork "for FRB follow-up by
  F4"), PATH P(O|x) host association — the author's own science workflow.
- Caveat: FFFF_PZ selects *which* targets are observable in a run; it does
  **not** sequence targets within a night (no per-night ordering/scheduling).
  That gap is exactly what night-planner should fill.

---

## 2. JSkyCalc — Thorstensen's "time and the sky" calculator

**Repo:** <https://github.com/jrthorstensen/JSkyCalc> — John Thorstensen's
(Dartmouth) classic interactive observing-planning tool, the Java GUI
descendant of his C `skycalc`. The GitHub repo ships **only `JSkyCalc.jar` and
a README** ("The source is not included; message me if you would like it").

To examine actual code I read the author's Python port,
**<https://github.com/jrthorstensen/thorsky>** ("Python time-and-the-sky
programs built mostly on astropy", successor to deprecated `pyskycalc`), which
implements the same computations: modules `thorskyutil.py` (~1600 lines of
functions), `thorskyclasses3.py` (site/observation classes), and
`pyskycalc3.py` (a Tkinter GUI "generally similar to the java program
JSkyCalc"). Statements below cite those files.

### Core data structures (`thorskyclasses3.py`)

- `obs_site` — observatory: name, `EarthLocation` (geocentric xyz), local
  timezone; defaults to MDM/Kitt Peak; `get_sites()` reads a site file.
- `Observation` — bundles `celest` (a `SkyCoord`), `t` (an astropy `Time`), and
  a site. Methods: `computesky()`, `computesunmoon()`, `computeplanets()`,
  `computebary()` / `computequickbary()`, `setnightevents()`,
  `compute_hours_up()`, `printnow()`, `printnight()`.

### Instantaneous circumstances (`Observation.computesky` + `printnow`)

For one (site, time, target), JSkyCalc computes and displays:

- **LST** — `lpsidereal(time, location)` (fast low-precision sidereal time).
- Current-equinox coordinates (precession matrices, `currentFK5frame` /
  `currentgeocentframe`) and constellation.
- **Hour angle** = LST − RA, wrapped to ±12 h (`wrap_at(12.*u.hour)`).
- **Alt, Az, parallactic angle** — `altazparang(dec, ha, lat)` (spherical
  trig, no refraction); the parallactic angle (and its ±180° alternative) is
  printed for slit-orientation decisions.
- **True airmass** — `true_airmass(alt)`: a 4th-order polynomial fit to the
  Snell & Heiser (1968, PASP 80, 336) KPNO airmass tables in (sec z − 1),
  i.e. *better than plain sec z at large zenith distance*; valid to airmass
  ~12, returns sec z − 1.5 beyond.
- **Moon**: position (`lpmoon` fast / `accumoon` accurate), altitude/azimuth,
  **illuminated fraction**, human phase description (`phase_descr`, via
  `flmoon` Meeus-style phase JDs), **moon–object angular separation**, and
  **lunar sky brightness in V mag/arcsec²** — `lunskybright(...)` implementing
  **Krisciunas & Schaefer (1991, PASP 103, 1033)** (dark sky ≈ 21.5).
- **Sun**: position (`lpsun`), alt/az; twilight state, with `ztwilight(alt)`
  giving how many mag brighter than dark sky the twilit sky is.
- **Barycentric corrections**: time and velocity — the slow path uses astropy's
  `SkyCoord.radial_velocity_correction()` and
  `Time.light_travel_time(coord, kind='barycentric')`; prints "add X sec and
  Y km/s to observed" plus barycentric JD.
- Planetary positions (`computeplanets`), and a bright-star sky display done
  with cached rotation matrices (`precessmatrix`, `cel2localmatrix`,
  `icrs2topoxyz`) for speed.

### Per-night almanac (`setnightevents` / `printnight`; `nightevents()` in thorskyutil)

The "night events" block — the skeleton every night plan hangs on:

- **Sunset/sunrise** at altitude **−0.833°** (zenith distance 90° 50′,
  refraction + solar semi-diameter).
- **Evening/morning astronomical twilight** at sun altitude **−18°**.
- **Center of night** (midpoint), **moonrise/moonset** (same −0.833°).
- Algorithm: analytic first guess from hour angles (`ha_alt(dec, lat, alt)` =
  the HA at which a dec reaches a given altitude), then iterative refinement
  (`jd_sun_alt`, `jd_moon_alt`). All reported in local time (or UT).

### Observability helpers (`thorskyutil.py`)

- `min_max_alt(lat, dec)` — min/max altitude a declination ever reaches.
- `ha_alt(dec, lat, alt)` — hour angle at which the target crosses altitude
  `alt` (rise/set/critical-airmass HA).
- `hrs_up(timeup, timedown, evening, morning)` — **hours a target is above a
  critical altitude within the observing night** (clipped to twilights);
  exposed per-object as `Observation.compute_hours_up()`. This "hours up
  tonight at airmass < X" number is the single most useful observability
  scalar for ranking targets.

### What JSkyCalc teaches night-planner

- The **canonical quantity checklist** for any per-target, per-time display:
  LST, HA, alt/az, airmass, parallactic angle, moon alt/illumination/
  separation/sky-brightness, sun alt/twilight state, barycentric corrections.
- The **night-event definitions to adopt**: rise/set at −0.833°, astronomical
  twilight at −18°, night center; moon events likewise.
- Two clean layers: *instantaneous circumstances* vs *per-night events* —
  a good module split for our code.
- Physics upgrades over naive formulas worth carrying: true-airmass polynomial
  (Snell & Heiser) instead of sec z near the horizon; Krisciunas & Schaefer
  moon sky-brightness model rather than a bare moon-separation cut.
- astroplan reproduces most of this (Observer.twilight_*, moon_illumination,
  parallactic_angle, target rise/set), so we get JSkyCalc's outputs through
  our existing dependency — thorsky is the reference for *definitions* and for
  anything astroplan lacks (e.g., `lunskybright`, `hrs_up`).

---

## 3. astropy — the primitives underneath everything

(Skimmed at docs.astropy.org, stable: the `astropy.coordinates` and
`astropy.time` docs, plus the example-gallery page "Determining and plotting
the altitude/azimuth of a celestial object" — an end-to-end observation-
planning walkthrough.)

### The three pillars

- **`astropy.units`** (`u.deg`, `u.hourangle`, `u.m`, ...) — every angle,
  length, and time interval is a `Quantity`; both repos above pass units
  explicitly (e.g. `telescope.longitude*units.deg`).
- **`astropy.time.Time`** — time scales `utc, ut1, tt, tai, tdb, tcg, tcb,
  local`; formats `jd, mjd, iso, isot, datetime, ...`; arithmetic via
  `TimeDelta` (used by FFFF_PZ for 30-min/1-day stepping:
  `TimeDelta(1800, format='sec')`). Sidereal time:
  `t.sidereal_time('apparent'|'mean', longitude)` (needs a longitude or a
  `location` on the Time). Barycentric/heliocentric light-travel time:
  `t.light_travel_time(skycoord, kind='barycentric', location=...)` → add to
  `t` for BJD (exactly what thorsky's `computebary` does).
- **`astropy.coordinates`** —
  - `SkyCoord(ra=..., dec=..., unit='deg')`, accepts arrays (vectorize over
    targets); `SkyCoord.from_name('M33')` resolves names via Simbad/Sesame.
  - `EarthLocation.from_geodetic(lon, lat, height)` or
    `EarthLocation.of_site('keck')` (named-observatory database).
  - `AltAz` frame: the whole observability computation is one line —
    `target.transform_to(AltAz(obstime=times, location=loc))` → `.alt`, `.az`,
    and **`.secz`** for airmass. Passing an *array* of times gives the
    altitude/airmass track for a night in a single vectorized call.
  - `get_sun(time)` and `get_body('moon', time, location)` for solar/lunar
    positions → sun altitude < −18° defines dark time; moon–target separation
    via `SkyCoord.separation()`.

### How they combine (the canonical recipe)

```
loc    = EarthLocation.of_site(...)               # or from_geodetic
times  = midnight + delta_hours                    # Time + np.array*u.hour
frame  = AltAz(obstime=times, location=loc)
altaz  = target.transform_to(frame)                # .alt, .az, .secz
sunalt = get_sun(times).transform_to(frame).alt    # twilight/dark windows
moon   = get_body('moon', times, loc)              # separation, altitude
```

### Caveats noted

- `.secz` is the plane-parallel approximation — fine to Z ≈ 70–75°, degrades
  near the horizon (hence JSkyCalc's Snell & Heiser polynomial).
- The `AltAz` transform includes atmospheric refraction only if you supply
  `pressure` (and optionally temperature/humidity/obswl); by default it is
  unrefracted.
- Moon positions should be requested with a `location` for topocentric
  accuracy; sun/moon coordinates come back in GCRS, so transform both target
  and body into the same `AltAz` frame before taking separations near the
  horizon.

### The astroplan connection

**astroplan** (already in our `setup.cfg`/`requirements.txt`) is a thin,
Astropy-affiliated layer over exactly these primitives: `Observer` wraps
`EarthLocation` + timezone (adding `altaz()`, `twilight_evening_astronomical()`,
`twilight_morning_astronomical()`, moon/sun conveniences, `parallactic_angle()`),
`FixedTarget` wraps `SkyCoord`, and its constraints/schedulers operate on grids
of the same `AltAz` transforms. FFFF_PZ's `calc_airmasses` is a working example
of driving astroplan this way; thorsky shows the same computations done from
raw astropy (plus faster low-precision shortcuts). night-planner should follow
FFFF_PZ's pattern (astroplan on top) and use thorsky/JSkyCalc as the reference
for definitions and output content.

---

## Synthesis for night-planner

1. **Plan structure** (from FFFF_PZ): an observing run = instrument + UT window
   + per-mode target counts + selection criteria + max airmass; the deliverable
   is a flat target table; the return product is an observing log table.
2. **Night skeleton** (from JSkyCalc): sunset/−18° twilight/night center/
   −18° twilight/sunrise + moon rise/set/illumination — compute these first,
   then place targets.
3. **Per-target metrics** (both): HA, alt/az, airmass (true airmass if pushing
   high Z), parallactic angle, moon separation + lunar sky brightness,
   hours-up-tonight below the airmass limit.
4. **Engine**: astropy `SkyCoord`/`Time`/`AltAz` via astroplan `Observer`;
   vectorize targets in one `SkyCoord` array and times in one `Time` array.
5. **Gap we fill**: neither tool *sequences* a night (FFFF_PZ stops at target
   selection; JSkyCalc is a calculator, not a scheduler) — ordering targets by
   transit/airmass windows within the twilight-bounded night is night-planner's
   core job (astroplan's Scheduler is the starting point).

---

## Ephemeris websites (UCO/Lick & Keck calendars)

(Added 2026-07-11, executing `claude_prompts/context_prompts.md`, Websites >
Ephemeris, prompt 1. All pages below were fetched and verified.)

The University of California Observatories hosts pre-computed observing
calendars (compiled by Dr. Arnold Klemola; contact `webeditor@ucolick.org`) —
an authoritative, site-specific nightly almanac for the two facilities we care
most about.

**Read this first — the explanatory readme:**

- <https://ucolick.org/calendar/readme.html> — describes what the calendars
  tabulate: sunrise/sunset, moonrise/moonset, sidereal times (at twilight,
  midnight, and dawn), and length of night (whole night, dark hours, % dark).
  Each calendar comes in **two twilight variants**: nautical (sun −12°) and
  astronomical (sun −18°).

**Lick Observatory (Mt. Hamilton, altitude 1283.0 m; times in PST):**

- <https://ucolick.org/calendar/lickcal2011-20/index.html> — years 2011–2020.
- <https://ucolick.org/calendar/lickcal2021-30/index.html> — years 2021–2030.

**Keck Observatory (Maunakea; computed for altitude 4160.0 m; times in HST):**

- <https://ucolick.org/calendar/keckcal2011-20/index.html> — years 2011–2020.
- <https://ucolick.org/calendar/keckcal2021-30/index.html> — years 2021–2030.

**Structure (verified by fetching the pages):** the four index URLs are pure
navigation pages — for each year they link 12 monthly calendar files per
twilight variant (e.g. `keck2021.18jan` = Keck, January 2021, 18° twilight;
`lick2021.12jan` = Lick, January 2021, 12° twilight). Adjacent-decade indexes
(1998–2010, 2031–2040, 2041–2050) are linked from the same pages.

**Per-month table contents (verified on `lick2021.18jan` and
`keck2021.18jan`):** one row per night — "ONE LINE REFERS TO EVENING DATE AND
FOLLOWING MORNING" — with columns for DATE (local zone), SUN SET, TWILIGHT
ENDS (12° and 18°), MOON RISE / MOON SET, DAWN BEGINS (18° and 12°), SUN RISE,
SIDEREAL TIMES (at twilight end, midnight, and dawn), NIGHT LENGTH / DARK
LENGTH, and the Moon at midnight (RA, Dec, distance). All dates/times are in
the site's local standard zone (PST for Lick, HST for Keck) *except* the
sidereal times; footers also list the month's moon-phase dates (new/quarters/
full).

**Use for night-planner:** these tables are an independent, observatory-
blessed reference for exactly the night-skeleton quantities we compute with
astroplan/thorsky (sunset/sunrise, 12°/18° twilights, moon rise/set, LST,
night/dark length) — ideal for **cross-checking our computed values** for any
Lick or Keck night in 2011–2030, and as a quick human-readable lookup when no
code is at hand.
