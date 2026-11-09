# Night plan for Lick Observatory + Shane 3m on 2026-09-14

This file will guide the construction of a night plan for the Lick Observatory + Shane 3m on 2026-09-14. This is run #2 of semester 2026B (`Lick-2026B-02`), a single night, following the same Kast/CHIME-FRB-host workflow as `lick_2026aug13.md` (`Lick-2026B-01`).

## Context

See `context/claudes_context.md` and `context/claudes_brain.md` for full background (FFFF-PZ Resource conventions, Kast setup, Shane pointing limits, prior Lick-2026B-01 run).

### FFFF-PZ

Interface via the CHIME FFFF-PZ database (`chime-ffff-pz` repo, `astro` conda env). HOWTO: `context/HOWTOs/FFFF-PZ-HOWTO.pdf`.

## Prompts

### Prompt 1 — Resource + target pull (2026-09-14)

> Read `/home/lordrick/Projects/night-planner/claude_prompts/night_plans/lick_2026aug13.md`
>
> And all the nightplans we have made so far, and progress we have made in this nightplan
>
> And then starting with a resource json Lick-2026B-02.json, make the resource pull the the targets for the date Sep 14th 2026, then update this prompt file to a proper format and record all steps taken and propmpts in this file.
>
> You can make the new folders and files in the appropiate directory

## Q&A

### Claude's questions (2026-09-14 plan prep, via Sonnet 5)

Read `lick_2026aug13.md` in full (Lick-2026B-01 Q&A + Reports) plus `context/claudes_brain.md`'s "FFFF-PZ Resource creation" section before drafting. Since most parameters were already settled for Lick-2026B-01 and nothing in the new prompt suggests changing them, I only asked what actually differs for this run, live in conversation (recorded here rather than as blocking `>A.` rows):

- **Naming/run number:** `Lick-2026B-02` (padded, per the established convention confirmed in aug13 Q1.1) — run #2 of 2026B, since `Lick-2026B-01` already exists.
- **Branch handling:** `chime-ffff-pz` is currently on branch `Lick-2026B-01` with that run's files still uncommitted, plus an unrelated uncommitted `Lick-2026A-5` folder (not touched). Asked how the new file should land on a proper branch.
  >A. I will switch branches myself; write the JSON wherever the repo is currently checked out.
- **Resource parameters:** proposed reusing the Lick-2026B-01 defaults verbatim (only name/dates change). Asked whether to keep or change any value.
  >A. Reuse the Lick-2026B-01 defaults.

#### Proposed JSON (written to `chime_ffff_pz/data/Observing/Lick-2026B-02/Lick-2026B-02.json`)

```json
{
    "instrument": "KAST",
    "name": "Lick-2026B-02",
    "valid_start": "2026-09-15T02:00:00Z",
    "valid_stop": "2026-09-16T13:30:00Z",
    "num_targ_img": 0,
    "num_targ_mask": 0,
    "num_targ_longslit": 15,
    "max_AM": 2.0,
    "frb_surveys": "all",
    "obs_type": null,
    "Period": null,
    "frb_tags": null,
    "frb_statuses": null,
    "max_mag": 20.5
}
```

Window is loose (server clips to astronomical twilight regardless, per the HOWTO and aug13 Q2.1): local evening date 2026-09-14 → mostly UT 2026-09-15 (sunset ≈19:30 PDT Sep 14, sunrise ≈06:30 PDT Sep 15).
`valid_stop` was hand-edited by the author from `2026-09-15T13:30:00Z` to `2026-09-16T13:30:00Z` before sign-off — widens the window by one more day (covers the following night too), same pattern as the aug13 Resource's night-2 widening note. Not reverted; taken as the author's deliberate call.

#### Command sequence (executed 2026-09-14, after sign-off)

```bash
# frb_env conda env (not "astro" — see correction below), FFFF_PZ_USER/PASS/URL from ~/.bashrc
conda run -n frb_env chime_ffff_pz_add_furesource chime_ffff_pz/data/Observing/Lick-2026B-02/Lick-2026B-02.json
conda run -n frb_env chime_ffff_pz_targets Lick-2026B-02
```

>A. Made a small edit (`valid_stop` → Sep 16), go ahead.

**Execution result:** `chime_ffff_pz_add_furesource` → `Your request succeeded!` (clean, no benign-error string this time). `chime_ffff_pz_targets` → wrote `Lick-2026B-02_targets.csv` (15 rows) on the first pull, no rerun needed.

**Environment correction:** this machine has no conda env literally named `astro` (`conda env list`: base, KRO, LRO, cigale, frb_env, git_page_env, pyar_env, pyp_env, plus micromamba `stenv`). The `chime_ffff_pz_*` CLI tools are installed in **`frb_env`** — used that instead. `FFFF_PZ_USER/PASS/URL` load correctly from `~/.bashrc` inside it (`user=root`, `url=http://0.0.0.0:8000/`, the same docker-hosted instance noted in `claudes_brain.md`).

## Reports

### Target selection report — Lick-2026B-02, night of 2026-09-14/15 (via Sonnet 5)

**Pull:** 15 targets returned on the first `chime_ffff_pz_targets` call (no rerun needed) — matches `num_targ_longslit = 15` exactly, unlike Lick-2026B-01's 14/15.

**Shane Dec ≤ +82° cut** (server only filters on airmass, per aug13 Q7.1): dropped **3** of the 15 —
`FRB20251003A` (Pri_Dec +84.70°), `FRB20260510A` (Pri_Dec +86.34°), `FRB20260625A` (Pri_Dec +82.40°) — leaving **12** targets, copied to
`Night_plans/Lick-2026B-02/Lick-2026B-02_targets.csv`.

Sorted by RA, PATH primary-host values:

| TNS | FRB tags | P(O\|x) (primary) | host r-mag | RA (h:m:s) | Dec (d:m:s) | DM |
|---|---|---|---|---|---|---|
| FRB20260623C | CHIME-Unbiased, CHIME-Lowz | 0.999 | 16.98 | 00:38:52.17 | +32:52:28.12 | 332.8 |
| FRB20260507D | CHIME-Unbiased, CHIME-Lowz | 1.000 | 18.56 | 01:43:48.55 | +32:46:08.52 | 341.3 |
| FRB20230805A | CHIME-Repeater, CHIME-Blind | 0.771 | 17.99 | 02:24:03.98 | +52:41:35.99 | 638.5 |
| FRB20260418B | CHIME-Lowz | 0.976 | 20.23 | 06:11:02.72 | +39:21:33.41 | 211.3 |
| FRB20260305A | CHIME-Blind | 0.998 | 18.52 | 08:02:10.58 | +36:59:49.54 | 297.1 |
| FRB20260514A | CHIME-Unbiased | 1.000 | 20.27 | 08:28:30.61 | +69:14:22.75 | 617.5 |
| FRB20260310B | CHIME-Unbiased, CHIME-Lowz | 0.998 | 18.95 | 11:42:52.56 | +79:37:05.46 | 287.5 |
| FRB20201128D | CHIME-Blind | 0.957 | 16.32 | 12:12:29.87 | +73:17:42.88 | 158.1 |
| FRB20260406B | CHIME-Unbiased | 1.000 | 19.51 | 12:49:24.47 | +52:38:42.85 | 353.4 |
| FRB20240324A | CHIME-Blind | 0.956 | 19.18 | 12:51:21.51 | +78:49:57.44 | 163.7 |
| FRB20260521A | CHIME-Unbiased, CHIME-Lowz | 0.969 | 17.77 | 15:22:12.36 | +68:59:32.68 | 336.8 |
| FRB20260627D | CHIME-Unbiased, CHIME-Lowz | 1.000 | 19.64 | 16:13:46.62 | +68:15:35.36 | 280.2 |

Tag counts in the 12-target set: CHIME-Unbiased 7, CHIME-Lowz 6, CHIME-Blind 4, CHIME-Repeater 1 (five targets carry two tags: CHIME-Unbiased+CHIME-Lowz each).

**Overlap with Lick-2026B-01:** `FRB20240324A` and `FRB20201128D` reappear from the Aug 13 pull with identical host coordinates/mag/DM (same underlying FFFF-PZ catalog entries, re-drawn by the stochastic sampler) — expected, not a bug; `FRB20251003A` (dropped there too, for the same Dec>+82° reason) reappears again on this pull as well.

**Honesty note:** as with Lick-2026B-01, this set is criteria-driven and feasibility/Dec-filtered with a stochastic draw, not hand-ranked; observability (LST windows, HA limits) and down-selection to ~5-6 targets for the actual night is deferred to the Night-plan step (not yet run — see "What this pass does not do" below).

## Prompts

### Prompt 2 — Night plan (2026-09-14)

> make the nightplan, remember the pointing constraints for Lick, and how to spread the targets through the night

### Shane 3m pointing constraints (per `context/claudes_brain.md` and Lick-2026B-01's `HOWTO_night_plan_creation.md`, "Critical Corrections Made")

Two hard mechanical limits, no more:

1. **Dec ≤ +82°** (polar limit) — already applied above.
2. **Hour angle: −5.0h ≤ HA ≤ +3.75h**, where HA = LST − RA (wrapped to ±12h). Negative HA = east of meridian (rising, before transit); positive HA = west (setting, after transit). **No RA limit** — which RAs are legal depends entirely on the night's LST range, which shifts with the calendar date; a target legal in August can be illegal in September and vice versa.

The 2026B-01 run initially got this backwards (believed a fake "RA ≥ 5h" rule and missed the east HA limit), which put 4 of 6 wrong targets into that plan before a patch script (`fix_ha_limits.py`) caught it after the fact. For this run the HA window (entry/exit time, clipped to twilight) is computed **per target, before scheduling** — `scripts/lick_2026b02_calculations.py`'s `target_window()` — so nothing is scheduled outside the legal HA range in the first place.

### How targets were spread through the night

An **earliest-window-close-first** greedy scheduler (`schedule_night()` in the same script): each HA-observable target is offered in order of when its legal window closes (`exit_pst`); if its Kast exposure time (from the existing calibrated `night_planner/estimate_kast_exposures.estimate_exposure`) fits between "now" and its window close, it is scheduled starting immediately after the previous target (+5 min slew); otherwise it is skipped with an explicit reason (mirrors the "log the reason at every skip point" lesson from the Keck pipeline in `claudes_brain.md`, rather than silently dropping it). This generalizes the aug13 rule "observe setting targets before they're lost" into something computed rather than hand-picked.

### Twilight for 2026-09-14 (18° astronomical, PST = UTC−8 fixed, per the Lick-calendar convention established for Lick-2026B-01)

Computed with astropy (`find_twilight()`): evening 19:44 PST (LST 19.23h), morning 04:21 PST (LST 3.87h), night length 8.62h.

**Cross-checked against the Lick calendar** (`ucolick.org/calendar/lickcal2021-30/lick2026.12sep`, raw row for Sep 14): 18° twilight ends 19:46 PST, 18° dawn begins 04:19 PST — both within 2 min of the astropy calculation, same precision as the aug13 verification. (A first WebFetch of that page mis-parsed the fixed-width columns and returned the 12°-dawn value under the 18° label; re-fetched asking for the verbatim raw text line + header to resolve it — noting this here since it's an easy way to get a subtly wrong-but-plausible twilight time from that page.)

### Target selection & schedule for the night of 2026-09-14/15

Applying the HA window to the 12 Dec-cut targets: **only 5 of 12 ever have a legal HA window this night** — the rest (RA ≈ 8h–15.4h: `FRB20260305A`, `FRB20260514A`, `FRB20260310B`, `FRB20201128D`, `FRB20260406B`, `FRB20240324A`, `FRB20260521A`) sit at HA > +3.75h for the entire night at this date's LST range (19.2h→3.9h) and never enter the window — the same "never accessible" RA band the aug13 HOWTO documented, just shifted for the new date/LST.

Of the 5 with a window, `FRB20260627D` (RA 16.23h) enters right at evening twilight but only has a 45-minute window before exiting at HA=+3.75h — too short for its required 90 min (mag 19.64) — so it is correctly skipped. The remaining **4 are scheduled**:

| Start–End (PST) | TNS | RA (h) | mag_r | HA start→end | Red | Blue |
|---|---|---|---|---|---|---|
| 20:08–20:48 | FRB20260623C | 0.65 | 16.98 | −5.00 → −4.33 | 4×600 | 2×1200 |
| 21:13–22:13 | FRB20260507D | 1.73 | 18.56 | −5.00 → −4.00 | 6×600 | 3×1200 |
| 22:18–23:18 | FRB20230805A | 2.40 | 17.99 | −4.58 → −3.58 | 6×600 | 3×1200 |
| 01:40–03:10 | FRB20260418B | 6.18 | 20.23 | −5.00 → −3.50 | 9×600 | 3×1800 |

**250 min science / 517 min night (48% utilization).** There is one genuine, unfillable 137-minute dead-time gap (23:18–01:35): no pulled target has a legal HA window during that stretch — it is written into the timeline explicitly as an "Idle — no target in HA-legal window" row rather than silently skipped. All 4 scheduled targets happen to be rising (morning-side) targets this run; this date's LST range puts almost the whole 12-target pool either always-too-far-west (7 targets) or in a window too short to use (1 target, `FRB20260627D`).

**Standard stars:** of the project's 3-star option list (HZ_44, Feige_110, BD+28_4211), only **Feige_110** (RA 23:19:58.4, Dec −05:09:56, mag 11.8) satisfies the HA limits at *both* the start of the night (HA −4.10h, airmass ≈3.1 — the highest-airmass legal option, per the aug13 Q&A's "highest airmass at the beginning of the night" rule) and right after the last science target ends at 03:10 (HA +3.35h, airmass ≈2.2). HZ_44 and BD+28_4211 both fall outside the HA window at one or both of those times for this date — so Feige_110 is used twice (different airmass each time) rather than forcing an out-of-limits star.

**Output:** `Night_plans/Lick-2026B-02/Lick_2026B-02_Night_plan.xlsx` (sheets: `Observing Checklist`, `September 14th`), built by `scripts/build_lick_2026b02_night_plan.py` from `scripts/lick_2026b02_calculations.py`'s `target_analysis.csv` / `selected_targets_night1.csv`. Finishes calibrations by 03:35 PST, 46 min before 18° morning twilight.

## What this pass did not do

- No possible-targs spreadsheet, no CANFAR registration, no finder charts/starlist — not requested this round.

## Prompt 3 — HA-wrap bug fix in the rejection analysis (2026-09-14)

> make sure the HA angle at beginning and end of night are wrapped around -12 to 12

**Bug:** `scripts/target_rejection_analysis.py`'s `ha_never_legal_reason()` computes the morning-twilight HA two ways: a wrapped value (via `ha_at()`, always in (−12, +12]) for the legality checks, then unwraps a *copy* past +12h (adding 24h repeatedly) so it stays monotonically ≥ the evening HA — needed for the "HA only increases through the night" comparison logic. The unwrapped copy was reused for the **displayed** HA in the report text, so `target_rejection_analysis.md` could show an end-of-night HA outside ±12h (e.g. `+14.32h` for `FRB20260305A`, `+14.76h` for `FRB20260514A`, before the fix).

**Fix:** kept the unwrapped value (`ha_morn`) for the internal comparisons only; added `ha_morn_wrapped` (the plain `ha_at()` output) and used it in every displayed string. Re-ran `target_rejection_analysis.py` to regenerate the report — all HA values in `target_rejection_analysis.md` now fall within ±12h (e.g. `FRB20260305A`: beg `+11.20h`, end `-4.16h`).

Checked the other HA-computation sites while investigating (`ha_at()`, `build_night_plan.py`/`build_keck_night_plan.py`'s `add_row()`, `calculate_airmass()` in the Lick-2026B-01/Keck scripts) — all already wrap correctly; this was the one leak.

## Prompt 4 — Gap-fill "extras" from the full FFFF-PZ table (2026-09-14)

> can we update the night plan to look at entire table of FFFF-PZ and add extra targets which are not in need spectrum or not pending observations, they could be too dusty or POx is less than our thresholds but should be atleast greater than 0.6, and add them to try to fill up the gaps, these should however be on a separate table and a separate sheet on the excel, update our lick_2026sep14.md doc with this and all the changes we made to make our .md rejected target analysis

### Clarifications (asked live, recorded here)

The full FFFF-PZ table exposes 12 status values, not just the `NeedSpectrum`/`SpectrumPending` primary-pipeline states. Two calls needed the author's judgment rather than a guess:

- **Which non-primary statuses count as "extras"?** Candidates: `AmbiguousHost`, `TooDusty`, `RunPublicPATH` (also `GoodSpectrum`/`Redshift`, already-completed).
  >A. `RunPublicPATH` excluded ("won't have hosts to look at"); `AmbiguousHost` and `TooDusty` are good.
- **POx ceiling?** No `min_POx` is hard-coded anywhere in this repo (recent Resources leave it `null`), so there's no existing "normal threshold" to compare against numerically.
  >A. No ceiling — floor of 0.6 only (0.6 to 1.0).

### What was built

**`scripts/lick_2026b02_extras.py`** (new) — the full pipeline:
1. Pulled the entire FFFF-PZ table live via `chime_ffff_pz_frbtable` (not the per-Resource stochastic sample `chime_ffff_pz_targets` used for the primary 12-target list) → `Night_plans/Lick-2026B-02/full_frb_table.csv`, 519 FRBs, `status` column confirmed with 12 distinct values (`AmbiguousHost` 129, `Redshift` 123, `TooDusty` 119, `NeedSpectrum` 43, `NeedImage` 34, `BrightStar` 21, `GoodSpectrum` 15, `RunDeepPATH` 15, `RunPublicPATH` 7, `NeedSecondary` 7, `SpectrumPending` 3, `GiveUp` 2, `UnseenHost` 1).
2. `load_candidates()`: filters to `status ∈ {AmbiguousHost, TooDusty}`, `POx >= 0.6`, `Dec <= 82°` (Shane limit), excluding any TNS already in the primary pull → **65 candidates**.
3. `analyze_candidates()`: reuses `target_window()` from `lick_2026b02_calculations.py` (same HA/twilight math as the primary list) → **51 of 65 are HA-observable** at some point tonight.
4. `free_intervals()` + `schedule_extras()`: identifies idle stretches strictly *between* consecutive primary science targets (not before the first or after the last — those edges are already consumed by the fixed focus/standard-star/bias/flat calibration blocks in `build_lick_2026b02_night_plan.py`, so they're not actually free), each shrunk by a `SLEW_MINUTES=5` buffer on both ends, then greedily packs HA-observable extras into them earliest-window-close-first (same principle as the primary `schedule_night()`).
   - **Bug caught and fixed during this pass:** the first version of the scheduler treated the segments before the first target and after the last as free too, and only reserved slew time on *one* side of a placed extra — it scheduled a candidate ending 90 seconds before the next primary target's start (no slew margin) and another sitting on top of the post-science standard-star/calibration block. Restricted free intervals to interior gaps only and reserved `SLEW_MINUTES` on both ends before recomputing.
5. Two interior gaps this night: 20:53–21:08 PST (15 min, too short for anything) and the known 23:23–01:35 PST gap (132 min after slew buffers). **3 extras scheduled** into the latter:

| TNS | RA (h) | mag | P(O\|x) | status | HA start→end | Start–End (PST) |
|---|---|---|---|---|---|---|
| FRB20230905A | 20.24 | 16.44 | 0.910 | TooDusty | −1.01 → +3.75 | 23:23–00:03 |
| FRB20231111A | 21.63 | 16.53 | 0.800 | AmbiguousHost | −2.39 → +3.75 | 00:08–00:48 |
| FRB20231223B | 5.25 | 16.27 | 0.918 | TooDusty | −5.00 → −1.37 | 00:53–01:33 |

Outputs: `extras_analysis.csv` (all 65, HA windows), `extras_schedule.csv` (scheduled + skip reasons for the rest), `extras_gap_fill_analysis.md` (full accept/reject table with numeric reasons, same convention as `target_rejection_analysis.md` but kept as its own separate document per the "separate table" instruction).

**`scripts/build_lick_2026b02_night_plan.py`** (extended) — added `add_extras_sheet()`, a new **`Extras (Gap-Fill)`** sheet in `Lick_2026B-02_Night_plan.xlsx` (third sheet, after `Observing Checklist` and `September 14th`), listing only the 3 scheduled extras with the same RA/Dec/HA/mag/red-blue columns as the primary sheet plus `P(O|x)` and `status` — visually distinct (orange header) and never merged into the primary science table.

## Prompt 5 — Force-schedule the faint setting target (2026-09-14)

> Another thing, in our main plan, can you slot in this FRB20260627D at the beginning, and then push everything before the gap forward by 45-50mins, I know it's faint and setting, we will try to get it anyway

`FRB20260627D` (mag 19.64, RA 16.23h) was the one target dropped in Prompt 2 for an
insufficient window: it enters legal HA right at evening twilight but exits at HA=+3.75
(the Shane mechanical limit) only ~45 min later, well short of the 90 min its magnitude
needs. Author's call: attempt it anyway as the very first thing of the night, partial
exposure accepted, and shift the rest of the schedule to follow.

**Actual shift computed: ~30 min, not 45-50.** `HA_MAX=+3.75h` is a hard *mechanical*
limit at a fixed clock time (20:28:42 PST tonight) — starting the target earlier doesn't
extend the window, it only gets you more of the ~45 min that's available no matter when
you start. Since `FRB20260623C` (the original first target) couldn't legally start before
20:08:51 anyway (its own `HA_MIN=-5h` rising-side limit), most of `FRB20260627D`'s window
was already-idle time before that — only the leftover (dome-open Focus block + the
relocated evening standard star, both of which now happen *after* this target instead of
before, so they don't eat into its thin window) actually pushes the rest of the night
later.

**Implementation (`scripts/lick_2026b02_calculations.py`):** added `forced_first` param to
`schedule_night()` and a documented `FORCED_FIRST_TNS = 'FRB20260627D'` constant. When set,
the target is scheduled at `max(evening_twilight + FOCUS_MINUTES, entry_pst)`, running
until `min(ideal_end, exit_pst)` — i.e. truncated to whatever the HA cutoff allows — then
`current_time` for the rest of the greedy scheduler is advanced past it plus a slew and the
relocated standard-star block (`SLEW_MINUTES + STD_STAR_MINUTES`), so every downstream
target's start time already accounts for the reordering. Also updated
`target_rejection_analysis.py` to pass the same override (it independently calls
`schedule_night()`) and added a `SCHEDULED (forced, partial)` status with an honest reason
string (previously it would have reused the generic "comfortably fits" wording, which
would have been self-contradicting for a target explicitly *not* getting its full needed
exposure).

**Two bugs caught while wiring this up:**
1. `build_lick_2026b02_night_plan.py`'s date parser (`pd.to_datetime` on the schedule CSV)
   inferred a single strptime format from the first row and broke once `FRB20260627D`'s
   start (`19:44:00`, no fractional seconds -- it's the first observable instant, not a
   `estimate_exposure`-derived duration boundary) sat next to rows that do carry
   microseconds. Fixed with `format='mixed'` in both `build_lick_2026b02_night_plan.py`
   and `lick_2026b02_extras.py` (same read pattern).
2. First version of the Excel builder inserted the relocated standard star (10 min: slew +
   observe) *after* the forced target but didn't feed that time back into
   `schedule_night()`'s `current_time` — so the CSV said `FRB20260623C` could start at
   20:33:42 while the sheet's own standard-star row didn't finish until 20:38, an actual
   overlap. Fixed by modeling the same 10 min inside `schedule_night()`'s forced-first
   branch (new `FOCUS_MINUTES`/`STD_STAR_MINUTES` constants) so both stay consistent by
   construction rather than needing to be kept in sync by hand.

**Final schedule for the night:**

| Start–End (PST) | TNS | mag_r | HA start→end | Duration |
|---|---|---|---|---|
| 19:44–19:49 | *Focus* | | | 5 min |
| 19:49–20:29 | **FRB20260627D** | 19.64 | +3.00 → +3.75 | 40 min (partial; 90 min ideal) |
| 20:33–20:38 | *Standard (Feige_110)* | | | 5 min |
| 20:39–21:19 | FRB20260623C | 16.98 | −5.00 → +3.22 | 40 min |
| 21:24–22:24 | FRB20260507D | 18.56 | −5.00 → +2.14 | 60 min |
| 22:29–23:29 | FRB20230805A | 17.99 | −5.00 → +1.47 | 60 min |
| 23:29–01:35 | *Idle (126 min, down from 137)* | | | |
| 01:40–03:10 | FRB20260418B | 20.23 | −5.00 → −2.31 | 90 min |

285 min science / 517 min night (55%, down slightly from 57% since the forced target only
delivers a partial exposure for its 40 min). Re-ran `lick_2026b02_extras.py` afterward
since the interior idle gap shrank (137→126 min after the new slew buffers): the gap-fill
schedule adjusted itself (3 extras still fit, one swapped for a better-fitting candidate
now that the gap start moved later) — regenerated `extras_analysis.csv`,
`extras_schedule.csv`, `extras_gap_fill_analysis.md`, and the `Extras (Gap-Fill)` sheet.
Also regenerated `target_rejection_analysis.md` with the new `SCHEDULED (forced, partial)`
row for `FRB20260627D`.

## Prompt 6 — Real finder charts and starlists (2026-09-14)

> Use the scripts in chime_ffff_pz to make finder charts for our main and extras and then make a starlist

Earlier, `scripts/make_lick_2026b02_starlist.py` (still on disk, not deleted) admitted in its
own docstring that it was a placeholder: no finder-chart/offset-star step had been run, so
each row just used the PATH primary-host coordinates directly, no offset star, no slit
centering/PA. This replaces that with the real `chime_ffff_pz_finder`/`chime_ffff_pz_starlist`
pipeline (per `chime-ffff-pz`'s `observing-prep` skill).

**Finder charts** (`chime_ffff_pz_finder <TNS> Lick-2026B-02`, run via the `frb_env` conda
env): generated for all 8 targets — the 5 scheduled science targets (`FRB20260627D`,
`FRB20260623C`, `FRB20260507D`, `FRB20230805A`, `FRB20260418B`) plus the 3 scheduled extras
(`FRB20230905A`, `FRB20231111A`, `FRB20250524A`) — each pulling the FRB's live PATH
candidates from FFFF-PZ (not resource-dependent; only the instrument lookup needs a real
Resource name, and `Lick-2026B-02`/KAST covers both groups), querying Pan-STARRS for an
offset star, and computing the KAST slit center/PA. All 8 succeeded on the first pass; PNGs
copied to `Night_plans/Lick-2026B-02/finder_charts/` for easy viewing, JSONs staged
separately per group.

**Starlists** (`chime_ffff_pz_starlist lick`): the tool globs `*finder.json` in the current
directory with no group filter, so the main and extras JSONs were staged into two separate
directories and the tool run once in each — the only way to keep them on separate starlists,
consistent with every other main/extras split this run. Wrote `scripts/lick_2026b02_finalize_starlists.py`
to reorder each group's rows into actual observing sequence (the tool's own glob order isn't
schedule order) and append the standard star (`Feige_110` — not an FRB, so it has no FFFF-PZ
entry/finder.json, added by hand as before) to the main list only. Result:
`Night_plans/Lick-2026B-02/lick.starlist` (5 targets × 3 rows [primary/secondary/slit-center] +
standard star) and `lick_extras.starlist` (3 targets × 3 rows), superseding the old
placeholder `lick.starlist`.

**Note for the author:** `chime_ffff_pz_starlist`'s Dec field (`scripts/starlist.py`, `add_coord_to_row`)
formats degrees as `f'{coord.dec.dms[0]:02.0f}'` with no explicit sign flag, so positive
declinations print unsigned (e.g. `68 15 35.4`, no leading `+`) while negative ones do show
`-` (from the negative float itself, e.g. Feige_110's hand-added `-05 09 56.0`). Every target
this run is Dec-positive (Shane limit), so it didn't affect this starlist's usability, but it's
worth a look if a future run's Lick-format parser expects an explicit sign on every row — this
is upstream `chime-ffff-pz` behavior, not something changed here.

## Logs

- **2026-09-14 (Sonnet 5):** Read `lick_2026aug13.md`, `context/claudes_brain.md`, and the `chime-ffff-pz` repo state. Created
  `chime_ffff_pz/data/Observing/Lick-2026B-02/Lick-2026B-02.json` (reusing Lick-2026B-01's confirmed defaults) and the
  `Night_plans/Lick-2026B-02/` output folder. Reformatted this prompt file into the aug13 Q&A/Reports/Logs shape and held the
  server-write commands for sign-off.
- **2026-09-14, continued (Sonnet 5):** Author edited `valid_stop` → `2026-09-16T13:30:00Z` directly in the JSON and confirmed
  "go ahead." Discovered no `astro` conda env exists on this machine; ran via `frb_env` instead (where the `chime_ffff_pz_*`
  CLI is actually installed; credentials load correctly from `.bashrc`). `chime_ffff_pz_add_furesource` succeeded cleanly;
  `chime_ffff_pz_targets Lick-2026B-02` returned 15 targets on the first pull. Applied the Shane Dec ≤ +82° cut (3 dropped),
  copied the 12-target CSV to `Night_plans/Lick-2026B-02/`, and wrote the target-selection report above. See daily narrative
  log: `Logs/2026/09/2026-09-14.md`.
- **2026-09-14, night plan (Sonnet 5):** Built the Night plan per Prompt 2. Wrote `scripts/lick_2026b02_calculations.py`
  (twilight, per-target HA-window computation, earliest-window-close-first scheduler — HA limits baked into scheduling from
  the start rather than patched afterward, unlike the original 2026B-01 pipeline) and
  `scripts/build_lick_2026b02_night_plan.py` (Excel generation from the schedule). Verified the computed 18° twilight times
  against the live Lick calendar via WebFetch (within 2 min); caught and redid a first WebFetch that mis-parsed the
  fixed-width calendar columns. Result: 4 of 12 targets scheduled (250 min science / 517 min night, 48% utilization), 1
  genuine unfillable dead-time gap logged explicitly on the sheet, 1 target (`FRB20260627D`) correctly skipped for an
  insufficient window. Wrote the full report above. Updated `context/claudes_brain.md` with the reusable scheduling pattern.
- **2026-09-14, HA-wrap fix (Sonnet 5):** Per Prompt 3, found and fixed the display bug in
  `scripts/target_rejection_analysis.py`'s `ha_never_legal_reason()` (unwrapped internal HA leaking into the printed report),
  regenerated `target_rejection_analysis.md`. Checked all other HA-computation sites in the repo; no other leaks found.
- **2026-09-14, gap-fill extras (Sonnet 5):** Per Prompt 4, asked the author to settle two ambiguous points (which non-primary
  FFFF-PZ statuses to draw from; whether a POx ceiling applies) before implementing, then wrote `scripts/lick_2026b02_extras.py`
  (full-table pull via `chime_ffff_pz_frbtable`, status/POx/Dec filtering, HA-window analysis reusing `target_window()`, and a
  gap-scheduler restricted to idle intervals between primary targets). Caught and fixed a scheduling bug in the first version
  (free intervals wrongly included the pre-first/post-last edges already consumed by calibration blocks, and slew time wasn't
  reserved on both sides of a placed extra) before trusting the output. Extended
  `scripts/build_lick_2026b02_night_plan.py` with a new `Extras (Gap-Fill)` sheet. Result: 65 candidates → 51 HA-observable →
  3 scheduled into the 132-min gap. Wrote the full report above.
- **2026-09-14, forced-first target (Sonnet 5):** Per Prompt 5, added `forced_first` support to
  `schedule_night()` (`FORCED_FIRST_TNS='FRB20260627D'`) to attempt the one previously-skipped, too-short-window target anyway,
  as the very first thing of the night, accepting a truncated/partial exposure. Computed the real required schedule shift
  (~30 min) and explained to the author why it's less than their 45-50 min estimate (the HA_MAX cutoff is a fixed clock time,
  and most of the naive 45-min window was already idle time before the next target's own HA window opened). Caught two bugs
  before trusting the output: a mixed-datetime-format parsing failure in `pd.to_datetime` once the forced target's un-fractional
  timestamp sat next to microsecond-precision ones (fixed with `format='mixed'`), and a real scheduling overlap where the
  relocated standard-star block's time wasn't fed back into `schedule_night()`'s `current_time` (fixed by modeling
  `FOCUS_MINUTES`/`STD_STAR_MINUTES` inside the calculations script itself, not just the Excel layer). Re-ran the full
  pipeline in order (calculations → extras → rejection analysis → Excel) so all four outputs stay consistent. Wrote the full
  report above.
- **2026-09-14, finder charts + starlists (Sonnet 5):** Per Prompt 6, ran `chime_ffff_pz_finder`
  for all 8 targets (5 main + 3 extras) against the `Lick-2026B-02` Resource, all succeeding
  on the first pass. Staged the two groups' `*finder.json` files into separate directories
  (the only way to keep them on separate starlists, since `chime_ffff_pz_starlist` globs cwd
  with no filter) and ran `chime_ffff_pz_starlist lick` in each. Wrote
  `scripts/lick_2026b02_finalize_starlists.py` to reorder rows into actual schedule sequence
  and append the standard star to the main list. Replaced the placeholder `lick.starlist`
  (PATH-coordinates-only, no offset star/slit centering, per its own docstring) with the real
  offset-star/slit-PA version; added `lick_extras.starlist`. Noted an upstream cosmetic issue
  (unsigned positive Dec in `chime_ffff_pz`'s starlist formatter) without touching that repo.

### Addendum — copy starlists into chime-ffff-pz (2026-09-14)

> move the target lists and finders to the Lick-2026B-02 folder in chime-ffff-pz

Clarified with the author: "target lists" here meant the two **starlists** (`lick.starlist`,
`lick_extras.starlist`), not the target-pull CSVs; "finders" meant the finder-chart PNG/JSON
pairs. The finders needed no action — `chime_ffff_pz_finder` already wrote both PNGs and JSONs
straight into `chime-ffff-pz/chime_ffff_pz/data/Observing/Lick-2026B-02/` when generated earlier
in Prompt 6 (night-planner's `finder_charts/` folder only ever held a convenience copy of the
PNGs). Copied both starlist files into that same chime-ffff-pz folder (keeping the night-planner
originals too, per the author's preference, so every night-planner script that reads them stays
unaffected).
