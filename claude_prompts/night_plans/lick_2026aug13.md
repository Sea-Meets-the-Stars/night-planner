# Night plan for Lick Observatory + Shane 3m on 2026-08-13

This file will guide the construction of a night plan for the Lick Observatory + Shane 3m on 2026-08-13.  We will be using the Kast spectrograph and exclusively observing canddiate FRB host galaxies.   Possibly all of the targets will be drawn from the CHIME survey.

## Context

See the files `context/claudes_context.md` and `context/claudes_brain.md` for the context.

### FFFF-PZ

You will need to interface with the CHIME FFFF-PZ database to get the list of targets.
There is a copy of the HOWTO doc here: `context/HOWTOs/FFFF-PZ-HOWTO.pdf`.
The repository of code is here: `Projects/FRBs/chime-ffff-pz`.

If you need to run Python, be sure to use the `astro` conda environment.

## Websites

### Ephemeris

1. Here is a list of websites that provide ephemeris data:

   - https://ucolick.org/calendar/readme.html
   - Lick
        - https://ucolick.org/calendar/lickcal2011-20/index.html
        - https://ucolick.org/calendar/lickcal2021-30/index.html
   - Keck
        - https://ucolick.org/calendar/keckcal2011-20/index.html
        - https://ucolick.org/calendar/keckcal2021-30/index.html

Add this to your context file and log your work.

### Instrument manuals

1. Examine the instrument manuals for the following telescopes and add them to your context file:

   - Lick
     - https://mthamilton.ucolick.org/techdocs/instruments/kast/
   - Keck
     - https://www2.keck.hawaii.edu/inst/hires/
     - https://www2.keck.hawaii.edu/inst/lris/lrishome.html
     - https://www2.keck.hawaii.edu/inst/mosfire/home.html
     - https://www2.keck.hawaii.edu/inst/deimos/
     - https://www2.keck.hawaii.edu/inst/esi/
     - https://www2.keck.hawaii.edu/inst/kcwi/
   - Palomar
     - https://caltechopticalobservatories.github.io/NGPS/
   - Gemini
     - https://www.gemini.edu/instrumentation/gmos

## Prompts

###  Target list

1. Using the `chime-ffff-pz` package, we will generate a Resource file for 2026 August 13 called `Lick-2026B-01`.  Before doing so, review your context files and pose questions in the Q&A section below.  Use Fable if you can.  Log your work

2. We have answered the Q&A section below.  Now, proceed with generating a night plan for the first night of the run.  You should:

   - Generate the Resource file and upload to FFFF-PZ
   - Create a target list from FFFF-PZ
   - Create a spreadsheet that mimics the ones in the `/mnt/scratch/xavier/Observing/Observations/Lick_Kast/obs_docs/2026` folder.

If you have any new questions, pose them in the Q&A section below.  Use Fable if you can.  Log your work.

### Night plan

1. Thanks!  Now generate a Night plan doc, modeled after the ones in the `/mnt/scratch/xavier/Observing/Observations/Lick_Kast/obs_docs/2026` folder, e.g. `Lick_2026A-4_Night_plan.xlsx`. Name it `Lick_2026B-01_Night_plan.xlsx`. Name the sheets as the targets in the target list.  Log your work.  Use Fable if you can. Explain your reasonsing for the targets chosen in the Reports section below.  It should include the tags for each FRB.  

2. For the Kast setup, we will use the d57 dichroic, 600/7500 grism, and the 600/4310 grism with a 2" slit.
Please estimate exposure times based on that and our previous Night plans.
Then update the Night plan spreadsheet accordingly.  Use Fable if you can.
Log your work.

## Reports

### Target selection report — Lick-2026B-01, night 1 (2026-08-10, via Fable 5)

#### How the targets were chosen

The selection was criteria-driven, not hand-ranked — it is worth being honest
about the mechanism:

1. **The Resource encodes the criteria** confirmed in the Q&A below. The
   FFFF-PZ Resource `Lick-2026B-01` specifies: instrument `KAST` (Lick Shane
   3 m), `frb_surveys = "all"` (this FFFF-PZ instance is CHIME-only, so
   effectively CHIME/FRB), longslit mode → server-default status
   **NeedSpectrum**, `max_AM = 2.0`, `max_mag = 20.5` (PATH primary-host
   r-band), `frb_tags = null` and `min_POx` omitted (no tag or P(O|x)
   restriction), `num_targ_longslit = 15`, valid window the night of
   2026-08-13→14 UT.
2. **The server filtered for feasibility and drew the set.** FFFF-PZ applies
   a twilight-bounded minimum-airmass filter (astroplan-based) for that night
   at Lick and returns targets from the qualifying pool; when more targets
   qualify than requested, the draw is **stochastic** (tag-weighted, not an
   optimizer). It returned **14** targets — a feasible, criteria-satisfying
   set, not a scientifically ranked one.
3. **We then applied the Shane Dec ≤ +82° pointing limit** (the server cuts
   only on airmass, per Q7.1). This dropped **2** of the 14:
   **FRB20250102C** (Pri_Dec ≈ +84.08°) and **FRB20251003A**
   (Pri_Dec ≈ +84.70°), leaving the **12** targets in the plan
   (`Night_plans/Lick-2026B-01/Lick-2026B-01_possible_targs.xlsx`).
4. **Observability:** in mid-August at Lick the astronomical night spans
   roughly LST 19 h → 2.5 h, so the 12 targets (RA ≈ 0.5 h–15.7 h, most
   circumpolar or nearly so) are all reachable at airmass ≤ 2 at some point
   in the night. Six of the 12 sit at Dec +67.9° to +79.6°
   (FRB20240901A, FRB20260310B, FRB20250202A, FRB20201128D, FRB20260215E,
   FRB20240324A) — legal but within ~15° of the +82° limit, a plan-stage
   caution for slews and tracking near the pole.

#### The 12 targets (with FRB tags)

Sorted by RA. Coordinates are the PATH primary-host positions (as in the
possible-targs sheet); P(O|x) and r-mag are the PATH primary-host values.

| TNS | FRB tags | P(O\|x) (primary) | host r-mag | RA (h:m:s) | Dec (d:m:s) | DM |
|---|---|---|---|---|---|---|
| FRB20200702C | CHIME-Repeater | 0.996 | 15.98 | 00:33:04.69 | +28:49:52.56 | 201.3 |
| FRB20250902A | CHIME-Unbiased | 0.995 | 18.57 | 01:37:12.16 | +11:29:16.98 | 364.4 |
| FRB20230805A | CHIME-Repeater, CHIME-Blind | 0.771 | 17.99 | 02:24:03.98 | +52:41:35.99 | 638.5 |
| FRB20231223B | CHIME-Repeater | 0.918 | 16.27 | 05:14:47.75 | +48:45:03.64 | 499.4 |
| FRB20240901A | CHIME-Blind | 0.990 | 19.05 | 09:49:01.75 | +75:11:20.22 | 506.4 |
| FRB20260310B | CHIME-Unbiased, CHIME-Lowz | 0.998 | 18.95 | 11:42:52.56 | +79:37:05.46 | 287.5 |
| FRB20250202A | CHIME-GBO | 0.682 | 18.97 | 12:05:16.27 | +76:38:44.90 | 724.2 |
| FRB20201128D | CHIME-Blind | 0.957 | 16.32 | 12:12:29.87 | +73:17:42.88 | 158.1 |
| FRB20260215E | CHIME-Unbiased | 0.992 | 19.79 | 12:40:56.95 | +67:56:47.80 | 403.2 |
| FRB20240324A | CHIME-Blind | 0.956 | 19.18 | 12:51:21.51 | +78:49:57.44 | 163.7 |
| FRB20200621B | CHIME-Blind | 0.921 | 16.87 | 15:27:07.55 | +58:43:19.10 | 637.3 |
| FRB20230729A | CHIME-Blind | 0.962 | 18.44 | 15:44:13.00 | +39:33:23.25 | 599.8 |

No target in this set has a missing tag, P(O|x), magnitude, or DM. (The two
targets in the 14-row pull that were cut for Dec carried tags CHIME-Blind
for FRB20250102C and CHIME-Unbiased, CHIME-Lowz for FRB20251003A.)

#### What the tags mean

The tags are CHIME/FRB sample/subsample labels; each corresponds to a
criteria definition in `chime-ffff-pz` (`chime_ffff_pz/data/Criteria/*.json`),
which also sets the selection weight used in the stochastic draw. Only the
tags present in this set are defined here, quoting the criteria files'
descriptions:

- **CHIME-Blind** (weight 0.2): "Catch all sample for FRBs that do not meet
  any of the standard tagging criteria."
- **CHIME-Repeater** (weight 0.9): the criteria file carries no description;
  by name this is the sample of repeating CHIME FRBs (interpretation from
  the name, not documented).
- **CHIME-Unbiased** (weight 0.5): "Sample of FRBs with precise localization
  occuring within the DESI or Euclid footprints."
- **CHIME-Lowz** (weight 0.9): "Sample of FRBs which may be at very low
  redshift, with precise localization" (its criteria include DM ≤ 300).
- **CHIME-GBO** (weight 0.8): "Sample of FRBs observed by the Green Bank
  Outrigger" (i.e. with a GBO baseband localization).

Tag counts in the 12-target set: CHIME-Blind 6, CHIME-Repeater 3,
CHIME-Unbiased 3, CHIME-Lowz 1, CHIME-GBO 1 (two targets carry two tags).

#### Honesty note

P(O|x) and magnitudes are PATH primary-host values reported by FFFF-PZ; the
set is criteria-driven and feasibility-filtered (with a stochastic draw),
not hand-curated — the observer still down-selects roughly 5–6 targets for
the night by RA coverage and priority.

## Q&A

### Claude's questions (2026-08-13 plan prep, via Fable 5)

Sources reviewed: `context/HOWTOs/FFFF-PZ-HOWTO.pdf` (esp. "Generate an FRB
FollowUp Resource", p. 6–7, and "Request Targets for the Resource", p. 7);
the `chime-ffff-pz` repo (`CLAUDE.md`, `docs/add_furesource.md`,
`docs/targets.md`, `docs/obsplan.md`, `chime_ffff_pz/scripts/{add_modify_resource,targets}.py`);
and all 12 existing `Lick-*` resource folders in
`chime_ffff_pz/data/Observing/` (especially `Lick-2025B-1/2/3` and
`Lick-2026A-2`, the four most recent Kast runs). Where those sources already
answer a question I state it as an assumption; each open question carries my
recommended default so you can just confirm or correct.

#### 1. Resource definition & naming

- **Assumption (no question):** a Resource = *one observing run* (1–3
  nights), not a semester. Every existing folder (`Lick-2025B-1..3`,
  `Lick-2026A-2`) spans 1–3 consecutive nights, and the name encodes
  `<Site>-<Semester>-<run # within semester>`.
- **Q1.1 — Zero padding:** all 85+ existing resources use unpadded run
  numbers (`Lick-2023B-1`, `Lick-2026A-2`); `Lick-2026B-01` would be the
  first zero-padded name. Keep the literal `Lick-2026B-01`, or follow
  convention with `Lick-2026B-1`?
  *Recommendation:* use `Lick-2026B-1` to match the established convention
  (the name is the key for every downstream command — `chime_ffff_pz_targets`,
  `_obsplan`, `_logobs`, `_finder`, the `Resource` column, the git branch,
  and the CANFAR folder — so consistency matters); but the DB accepts any
  string, so I will use `Lick-2026B-01` verbatim if you prefer.
>A. Yes, please pad
- **Q1.2 — First 2026B run:** no `Lick-2026B-*` folder exists yet in
  `data/Observing/`, so run #1 is correct (UC semester 2026B = 2026 Aug 1 –
  2027 Jan 31, so Aug 13 is early 2026B). Confirm?
  *Recommendation:* yes, run #1.
>A. I confirm

#### 2. Site / instrument / time window

- **Assumption:** `"instrument": "KAST"` (uppercase), exactly as in all four
  recent Lick JSONs. The instrument→telescope→observatory chain (Shane 3 m,
  Mt. Hamilton, lat +37.34°) lives server-side in FFFF-PZ and drives its
  twilight-bounded min-airmass filter (`frb_targeting.calc_airmasses`).
- **Assumption:** Kast is a single-longslit, dual-arm spectrograph — no
  masks, and we want spectra, so `num_targ_img = 0`, `num_targ_mask = 0`,
  and only `num_targ_longslit > 0`. (Matches every past Lick resource.)
- **Q2.1 — Single night & UT window:** I read "2026 August 13" as the local
  evening date, i.e. the night of Aug 13→14 PDT (UT−7), which in UT is
  mostly Aug 14. Confirm it is a single full night?
  *Recommendation:* `valid_start = 2026-08-14T03:00:00Z` (≈ sunset ~20:00
  PDT Aug 13) and `valid_stop = 2026-08-14T13:30:00Z` (≈ sunrise ~06:20 PDT
  Aug 14). Past resources use loose windows (e.g. `Lick-2025B-3` starts
  18:30 UT, local daytime) because the server clips to astronomical
  twilight anyway — so a generous window is safe; the *date* being right is
  what matters.
>A. It is a 2 night run, but we are only going to generate a plan for the first night.
- **Q2.2 — max_AM:** every past Lick resource uses `max_AM = 2.0`. Keep?
  *Recommendation:* yes, 2.0 (alt ≥ 30°, sensible for Shane pointing and
  Kast throughput).
>A. I confirm
- **Feasibility note (reasoned from LST, not computed):** mid-August the sun
  is at RA ≈ 9.4 h, so LST ≈ 21.4 h at local midnight; the astronomical
  night runs roughly LST 19 h → 2.5 h. With max_AM 2.0 the server will keep
  targets roughly RA ≈ 15h–6h (wider at high dec; CHIME targets at
  dec ≳ +53° are circumpolar at Lick and nearly always pass). Expect the
  target list to cluster at RA ~16h–4h. I will verify with our own
  airmass script (written to disk per CLAUDE.md) before the final plan.

#### 3. Target selection criteria

- **Q3.1 — Surveys:** `frb_surveys = "all"` in every past resource; the
  FFFF-PZ instance is CHIME-only (`frb_survey = CHIME/FRB`), so "all" ≡
  CHIME. Keep "all"?
  *Recommendation:* yes, `"all"`.
>A. I confirm
- **Q3.2 — Statuses:** `frb_statuses = null` in all recent resources →
  server default (longslit mode selects `NeedSpectrum`; per the HOWTO p. 7,
  `NeedSecondary` targets come only via `--include_secondary` on
  `chime_ffff_pz_targets`). Keep null, and *exclude* NeedSecondary?
  *Recommendation:* null; no `--include_secondary` (they don't show as
  valid in the resource until marked pending — HOWTO caveat).
>A. Keep null
- **Q3.3 — Tags:** `frb_tags = null` (no restriction) in all recent Lick
  resources; alternatives are samples like `CHIME-Bright`, `CHIME-KKO`
  (see `data/Criteria/*.json`). Any tag restriction for this run?
  *Recommendation:* null — take the full pool, prioritize by hand at the
  pending/cut step.
>A. Keep null
- **Q3.4 — min_POx:** recent resources omit it; the HOWTO (p. 6–7) warns
  that setting `min_POx` *overrides* the status logic (e.g. 0.90 selects
  only single-candidate P(O|x) > 0.9 hosts and drops combined-top-two
  cases). Omit?
  *Recommendation:* omit (null), matching `Lick-2025B-*`/`Lick-2026A-2`.
>A. Omit
- **Q3.5 — Magnitude limits:** past Lick values: `max_mag` 19.5 (2025B-1,
  which also set `min_mag = 9.0`), 20.36 (2025B-2), 19.5 (2025B-3), 20.5
  (2026A-2). Magnitudes are the PATH primary host r-band. New moon falls
  ~Aug 12, 2026 (the Spain total solar eclipse), so Aug 13 should be
  essentially moonless dark time — please verify against the Lick 2026
  calendar. What limit do you want?
  *Recommendation:* `max_mag = 20.5` (dark time supports the faint limit;
  matches the most recent run), and omit `min_mag` unless you want to
  filter bright/nearby galaxies (then 9.0 as in 2025B-1).
>A. Use max_mag = 20.5

#### 4. Target counts (how many fit a Kast night)

- **Q4.1 — num_targ_longslit:** past runs *requested* 20–30 but the obslogs
  show only ~4–6 longslit targets actually observed per Kast night
  (2025B-3: 5/4/4 over three nights; 2026A-2: 6/5 over two). Selection
  server-side is stochastic when more pass than requested, and the HOWTO
  (p. 7) says one may need to run the targets script a few times. For a
  single August night, what request size?
  *Recommendation:* `num_targ_longslit = 20` — enough surplus to choose
  ~8–10 pending targets spread in RA, expecting ~5–6 observed.
>A. Use num_targ_longslit = 15

#### 5. Database access & environment

- **Assumption:** credentials come from `FFFF_PZ_USER` / `FFFF_PZ_PASS` /
  `FFFF_PZ_URL` (HOWTO p. 1: `https://frb.chimenet.ca/f4pz/`), normally
  loaded from `chime-ffff-pz/automation/config/secrets.env` (gitignored);
  CLI scripts check them via `chk_user_set()`. Everything runs in the
  `astro` conda env.
- **Q5.1:** is `secrets.env` (or your shell profile) already populated on
  this machine so the CLI scripts authenticate, and should I source it
  explicitly when I run the commands?
  *Recommendation:* I will run commands as
  `conda run -n astro env $(grep -v '^#' .../automation/config/secrets.env | xargs) <command>`
  unless the vars are already in your login environment.
>A. They are in my .bashrc shell profile.
- **Q5.2 — Git/PR workflow:** the HOWTO (p. 7) says: branch from `main` on
  `chime_ffff_pz`, add the JSON in a new same-named directory, and PR;
  branch naming follows the campaign (repo CLAUDE.md, e.g. `Keck-2025B-6`).
  Since you run all git commands: shall I only *write* the JSON file and
  leave branch/commit/PR to you?
  *Recommendation:* yes — I write
  `chime_ffff_pz/data/Observing/<name>/<name>.json`; you create the branch
  `<name>` and PR.
>A. I've put us on the right branch.
- **Q5.3 — CANFAR registration:** the HOWTO (p. 7) flags a known issue —
  add the resource name to `data/Observing/fu_resources.csv` with `N`, then
  run `chime_ffff_pz_canfar_upload -f` (needs local CANFAR auth) to create
  the folder and flip it to `Y`. Do that now, or defer until we have data
  to upload?
  *Recommendation:* defer; it's only needed for the raw-data upload after
  the run. I'll add the `N` row to `fu_resources.csv` when I make the JSON.
>A. We will not need CANFAR for this.

#### 6. Output format & location + the exact commands I propose

- **Assumption (from HOWTO p. 6–8 + scripts):** the products are
  1. `chime_ffff_pz/data/Observing/<name>/<name>.json` — the Resource
     definition (written by hand from the fields above);
  2. the DB record, created by `chime_ffff_pz_add_furesource <json>`
     (HTTP PUT to `add_frb_resource/`; expects 200, and the HOWTO notes it
     "will often return an apparent 'error' message which is benign");
  3. `<name>_targets.csv` in the same folder, written by
     `chime_ffff_pz_targets <name>` (PUT to
     `targets_from_frb_followup_resource/`, HTTP 201) with columns
     `TNS, FRB_RA, FRB_Dec, FRB_DM, FRB_Survey, FRB_tags,
     Pri_name/RA/Dec/POx/mag/filter, Sec_name/RA/Dec/POx/mag/filter,
     mode, Resource`.
  Later steps (not this task): `_pending.csv` + `chime_ffff_pz_obsplan`,
  finders (`chime_ffff_pz_finder TNS <name>`), starlist
  (`chime_ffff_pz_starlist <observatory>`), obslog (`chime_ffff_pz_logobs`).
- **Q6.1 — Proposed JSON (please vet before I execute anything):**

  ```json
  {
      "instrument": "KAST",
      "name": "Lick-2026B-01",
      "valid_start": "2026-08-14T03:00:00Z",
      "valid_stop": "2026-08-14T13:30:00Z",
      "num_targ_img": 0,
      "num_targ_mask": 0,
      "num_targ_longslit": 20,
      "max_AM": 2.0,
      "frb_surveys": "all",
      "obs_type": null,
      "Period": null,
      "frb_tags": null,
      "frb_statuses": null,
      "max_mag": 20.5
  }
  ```

  (name/dates/counts/mag per your answers to Q1.1, Q2.1, Q4.1, Q3.5.)
>A. I confirm

- **Q6.2 — Proposed command sequence (to run only after your sign-off):**

  ```bash
  # in the astro conda env, with FFFF-PZ credentials set
  chime_ffff_pz_add_furesource /home/xavier/Projects/FRBs/chime-ffff-pz/chime_ffff_pz/data/Observing/Lick-2026B-01/Lick-2026B-01.json
  # confirm the Resource appears on the FFFF-PZ web dashboard
  chime_ffff_pz_targets Lick-2026B-01        # → Lick-2026B-01_targets.csv (rerun if too few)
  ```

  OK?
>A. I confirm

#### 7. Open unknowns

- **Q7.1 — Half night vs full night, and any Shane pointing/hour-angle
  limits** beyond the airmass cut I should fold into the plan? (The
  night-planner branch history mentions "Lick pointing limits" work.)
  *Recommendation:* assume a full night; I'll apply any documented Shane
  limits at the *plan* stage, since the server only applies max_AM.
>A. Assume a full night; we are not allowed to point at Dec > 82 deg.
- **Q7.2 — Kast setup** (dichroic d46/d57, grism/grating, slit width) is
  not part of the Resource, only of the night plan — defer to the plan
  step? *Recommendation:* yes, defer.
>A. Yes, defer.
- **Q7.3 — Editing after creation:** if any parameter changes, I rerun
  `chime_ffff_pz_add_furesource` on the edited JSON (HOWTO p. 7:
  "If you need to edit/update the resource, rerun the script"). No
  question — just noting the correction path.

### Notes from generation (2026-08-10, via Fable 5)

- **Night 2 of the run:** the run is 2 nights but this Resource's valid
  window covers only night 1 (2026-08-14 03:00–13:30Z), as confirmed. If a
  night-2 plan is later wanted, widen `valid_stop` to ~2026-08-15T13:30Z in
  `Lick-2026B-01.json` and rerun `chime_ffff_pz_add_furesource` (cheap,
  per Q7.3), then rerun `chime_ffff_pz_targets`.
- **Generation results:** the upload returned a clean "Your request
  succeeded!" (no benign-error message this time). `chime_ffff_pz_targets`
  returned 14 targets on the first pull (no reruns needed). The Dec > +82°
  Shane pointing cut (Q7.1) dropped 2 targets — FRB20250102C (Pri_Dec
  +84.08°) and FRB20251003A (Pri_Dec +84.70°) — leaving 12 in
  `Night_plans/Lick-2026B-01/Lick-2026B-01_possible_targs.xlsx`.
- **New question for the author:** the server returned 14 targets even
  though `num_targ_longslit` was 15 and the Dec cut then removed 2 more.
  With 12 viable targets for a ~15-target night, is that acceptable, or
  should we rerun the (stochastic) target selection — or raise
  `num_targ_longslit` slightly to buffer against the Dec cut?
>A. That will be enough targets.

### Night-plan sheet design (2026-08-10, via Fable 5)

- Built `Night_plans/Lick-2026B-01/Lick_2026B-01_Night_plan.xlsx` via the new
  `night_planner/make_lick_night_plan.py`, modeled on
  `Lick_2026A-4_Night_plan.xlsx`. Per the prompt, the science sheets are
  named by target: 15 sheets in order — `Observing Checklist`, then one
  sheet per TNS (12, RA-sorted), then `FRB Observing Summary` and
  `Post Observing Tracking`. The template's `dont use` scratch sheet was
  not reproduced.
- Each target sheet carries the template's 15-column timeline header
  (A→O), a `slew to --> ` row, and a `Science + overhead` row with
  RA/DEC (text), Pri/Sec mags, and Comments = `P(O|x)=…; tag=…` merged
  from `Lick-2026B-01_targets.csv`. Start/Duration/End, `red side`,
  `blue side`, and `Redshift;` are deliberately blank (Kast setup and
  exposure times deferred per Q7.2). The Calibrations/Red/Blue side block
  (Focus/Bias/Flats, unchecked) is on every target sheet.
- The first target sheet (`FRB20200702C`) carries the standard-star
  bookend note (evening & morning twilight; BD+28 4211 / Feige 110 /
  HZ 44 as August options, no commitment) plus the template's
  Standard Star Options table — with RA/DEC written as text, since the
  template stored several declinations as Excel time cells (e.g. Feige110's
  −05° dec was stored as a positive time).
- The `Observing Checklist` was copied verbatim from the template with all
  `Done` flags reset to False for this run.
- Correct or redirect any of these choices and I will regenerate — the
  script is parameterized (inputs, template, output paths).

### Night-plan REGENERATION request (2026-08-10, lordrick_fussin branch)

User feedback: "looks like it build some files but did not make a coherent night plan, a night plan looks something like this /home/lordrick/Projects/night-planner/Night_plans/Lick-2026A-4_template/Lick_2026A-4_Night_plan.xlsx, notice the naming of the sheets, make sure you have the ability to get START TIMES end TIMES, LST Time for any given dates, make a branch with the same name add _lordrick_fussin at the end and let's try, also update the specific prompt file with this prompt and I'll answer any questions or assumptions you generate there"

**What's wrong:**
Current plan has sheets named by TARGET (one per FRB). Template has sheets named by DATE (e.g., "May 15th", "May 16th", "May 17th") with multiple targets listed sequentially on each night sheet.

**Template structure observed:**
- Sheets: `Observing Checklist`, `<Date>` (one per night), `FRB Observing Summary`, `Post Observing Tracking`
- Each date sheet has columns: Start (LST), Start (UT), Start (PST), Duration, End (PST), Action, target, RA, DEC, mag(r), sec mag, red side, blue side, Redshift, Comments
- Timeline uses formulas: `=C4 + TIME(14,30,0)` for LST from PST, `=E4 + D4` for end times
- Sidereal time calculator section in columns U-W
- Multiple targets per night listed sequentially with slew + science rows
- Standard stars included (HZ_44, etc.)

**Claude's questions & assumptions (lordrick_fussin iteration):**

1. **Sheet naming for 2-night run:** Use "August 13th" and "August 14th" (or "Aug 13th"/"Aug 14th")? Match template's full month name?
   *Recommendation:* "August 13th", "August 14th"
   Sure use "August 13th", "August 14th"

2. **Sidereal time calculation:** Need LST at arbitrary PST times for Aug 13/14, 2026 at Lick. Will write Python script to calculate:
   - LST at local midnight (for sidereal time calculator section)
   - LST at 12° twilight (evening/morning)
   - LST ↔ PST conversion for target scheduling
   *Assumption:* Use astropy (Lick lon=-121.6429°, lat=+37.3414°, tz=UTC-7 for PDT)
   Use Astropy and compare with online calculators through some API, if not possible offer me your answers and I'll make a table to compare answers with online calculators on your sample times

3. **Timeline start:** What PST time to start the night plan timeline? Template starts at 20:30 PST (~12° twilight). Use astronomical twilight calculator or fixed offset?
   *Recommendation:* Calculate 12° twilight for Aug 13, 2026 at Lick
   Always start at the 1/2 hour mark or hour mark before ~12 degree twilight, so if 12 degree 20:43, start at 20:30, if 12 degree is 21:18, start at 21:00 and so forth and so on.

4. **Target selection for night 1:** We have 12 viable targets. How many to schedule on night 1 (Aug 13th sheet)?
   *Recommendation:* ~5-6 based on past obslogs, prioritized by RA coverage for LST window ~19h-2.5h
   While selecting targets for Lick, we also have to think about hour angle and airmass, we can't observe targets West of 3:45 hours, therefore we If a target is going to set, we shall observe it first, if it needs more time that how long it will be up before crossing our pointing limit, then we don't observe it, we also generally like to observe targets at it's highest airmass but this is not a priority, we also cannot point west of 5:00 hours. Ask questions about this if you don't understand, also your note your reasoning for the selecting the targets and why that particular order.

5. **Exposure times (Kast d57, 600/7500, 600/4310, 2" slit):** Template shows patterns like "4 x 900" red, "2 x 1800" blue. Scale by target brightness? Use template as guide?
   *Recommendation:*
   - r ≤ 17: 3×900 red, 2×1350 blue (≈45 min + overhead)
   - r 17-19: 4×900 red, 2×1800 blue (≈60 min)
   - r 19-20.5: 6×900 red, 3×1800 blue (≈90 min)
   (Total overhead ~30% → 1h blocks become ~1.3h)

   Yap, for things brighter that 15 mag, I would go for 30min + overhead

6. **Standard stars:** Template lists HZ_44 (RA 13:23:35), Feige 110, BD+28 4211. Which for Aug 13 night? One at twilight, one at dawn?
   *Recommendation:* Pick by RA visibility; HZ_44 transits ~LST 13h (visible Aug eve)
   Also, at highest airmass during begining of the night

7. **Output location:** Overwrite `Night_plans/Lick-2026B-01/Lick_2026B-01_Night_plan.xlsx` or new filename?
   *Recommendation:* Overwrite (it's on new branch _lordrick_fussin)
   overwrite

>A. [AWAITING ANSWERS]

## Logs