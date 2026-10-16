# How Target Priority Is Set

Created by JXP and Claude

> **Scope:** describes the repository *as it is* on 2026-10-16, not as it
> should be. The last section lists what is missing.
>
> **See also:** [`priority_comparison_astroscheduler.md`](priority_comparison_astroscheduler.md)
> — how the UCSC AstroScheduler solves the same problem on the same telescope.

---

## Short answer

**There is no priority field anywhere in this pipeline.** No target carries a
rank, weight, or score that the scheduler reads. What looks like "priority" in
a finished night plan is the emergent product of four independent layers:

| Layer | Question it answers | Where science value enters |
|-------|--------------------|-----------------------------|
| 1. Pool selection | *Which targets exist at all?* | **Yes** — upstream, in FFFF-PZ |
| 2. Feasibility gates | *Can the telescope point there?* | No — hard physics |
| 3. Scheduling order | *What goes first?* | **No** — pure urgency |
| 4. Human overrides | *What must not be dropped?* | **Yes** — by hand, per run |

Scientific value is decided in layer 1 (by the FFFF-PZ server) and layer 4 (by
the author, in words). The scheduler in layer 3 is blind to it: it orders
targets by *how soon their window shuts*, never by how much anyone wants them.

---

## Layer 1 — Pool selection (upstream, FFFF-PZ)

The target pool comes from an FFFF-PZ *Resource* (a JSON describing the run),
pulled with `chime_ffff_pz_targets`. The server applies:

- `frb_statuses` — default for longslit is `NeedSpectrum`, i.e. hosts that
  still need a spectrum. Completed states (`GoodSpectrum`, `Redshift`) and
  hostless ones (`RunPublicPATH`) never appear.
- `max_mag`, `max_AM`, `valid_start`/`valid_stop` — feasibility, clipped
  server-side to astronomical twilight.
- **A tag-weighted stochastic draw.** The per-tag weights and cuts
  (`CHIME-Repeater`, `-Lowz`, `-Bright`, …) live in `chime-ffff-pz` at
  `chime_ffff_pz/data/Criteria/*.json`.

Two consequences matter for priority:

1. **The draw is the priority system.** Tag weights are the only place where
   "this FRB is more interesting" is encoded numerically, and they act by
   changing the *probability of being in the pool at all* — not by ranking
   targets inside it. Once a target is in the CSV, it is indistinguishable
   from every other row.
2. **The draw is stochastic per-pull, not per-Resource.** Re-running
   `chime_ffff_pz_targets` on an unchanged Resource returns a different set.
   There is therefore no stable ordering to inherit, even for the same run.

`min_POx` is deliberately left unset in Resource JSONs — setting it overrides
the status logic (HOWTO warning). So P(O|x) does *not* gate the primary pool.

### The gap-fill tier (the one explicit two-tier scheme)

[`scripts/lick_2026b02_extras.py`](../scripts/lick_2026b02_extras.py) builds a
deliberately **lower-priority** second pool, bypassing the Resource entirely
(`chime_ffff_pz_frbtable` — whole table, no stochastic sampling):

```python
EXTRA_STATUSES = ('AmbiguousHost', 'TooDusty')   # :46
POX_MIN = 0.6                                     # :47
```

These are written to a **separate** CSV / `.md` / Excel sheet
(`Extras (Gap-Fill)`) and scheduled only into idle intervals left by the
primary schedule, so the two tiers can never be confused. This is the clearest
statement of priority in the repo — and it is expressed as *two separate
pipelines*, not as a column.

---

## Layer 2 — Feasibility gates (not priority)

These reject; they never rank. Lick/Shane
([`scripts/lick_2026b02_calculations.py:61-63`](../scripts/lick_2026b02_calculations.py#L61-L63)):

```python
HA_MIN = -(5 + 40 / 60)   # -05:40 east limit
HA_MAX = 3 + 45 / 60      # +03:45 west limit
DEC_LIMIT = 82.0          # Shane polar limit
```

Keck/LRIS ([`scripts/keck_2026oct06_calculations.py:394-395`](../scripts/keck_2026oct06_calculations.py#L394-L395)):
`KECK_MAG_FAINT_LIMIT = 19.0`, `LICK_DEC_LIMIT = 82.0` — anything brighter than
19 **and** reachable from Lick is pushed back to Lick rather than spending Keck
time on it. That is a facility-allocation rule masquerading as a cut, and it is
the only place instrument capability feeds back into target assignment.

`target_window()` turns these limits into a per-target clock window
(`entry_pst`, `exit_pst`) **before** scheduling. Rejections are recorded with a
`limit_reason` rather than dropped silently; the staged labels
(`1. Keck selection` → `2. Sky` → `2b. Mask` → `3. Scheduling` → `4. Forced`)
are assigned in [`night_planner/adapters.py:170-240`](../night_planner/adapters.py#L170-L240)
and are what the viewer's rejection page shows.

---

## Layer 3 — Scheduling order: urgency, not value

### The current scheduler: earliest-window-close-first

`schedule_greedy()`
([`scripts/lick_2026b02_night2_calculations.py:149`](../scripts/lick_2026b02_night2_calculations.py#L149),
reused by the general entry point `scripts/kast_calculations.py`) walks targets
in order of **when their HA window shuts** and places each as late inside its
own window as it will fit. Keck does the same thing in different words
([`keck_2026oct06_calculations.py:910-912`](../scripts/keck_2026oct06_calculations.py#L910-L912)):

```python
# Sort by window end time (observe setting targets first)
observable = observable.sort_values('window_end')
```

The logic is sound — a target about to set is the one you lose if you wait —
but it is **urgency only**. A high-value target and a filler with the same
window close are tied, and the tie is broken by table order.

**The documented failure mode:** the CHIME repeater FRB20250408A is bumped out
of the crowded early-evening block in both the Keck-2026B-01 and B-02 plans
because cheaper targets closed earlier. Recorded twice in
[`context/claudes_brain.md`](../context/claudes_brain.md) (v0.37, v0.38) as
*"the scheduler still has no priority input."* This is the single strongest
argument for building layer 3 properly.

### The legacy scheme: `setting_priority` (Lick-2026B-01 only)

[`scripts/lick_2026b01_calculations.py:298-346`](../scripts/lick_2026b01_calculations.py#L298-L346)
used an explicit flag:

```python
observable['setting_priority'] = 0
observable.loc[observable['ha_evening'] < -2, 'setting_priority'] = 1
observable = observable.sort_values(['setting_priority', 'min_airmass'],
                                    ascending=[False, True])
```

`setting_priority` is a **binary evening/morning class, not a science rank** —
it survives in `Night_plans/Lick-2026B-01/selected_targets_night1.csv` and is
consumed by [`scripts/fix_ha_limits.py:124-132`](../scripts/fix_ha_limits.py#L124-L132)
to pick the HA sign convention. Do not read it as importance, and do not
extend it; `schedule_greedy` supersedes it.

### Other orderings that are not priority

- **Workbook sheet order is RA order**, not observing order
  ([`night_planner/make_lick_night_plan.py`](../night_planner/make_lick_night_plan.py)).
- **Standard stars are ranked by airmass only**
  ([`night_planner/standards.py:101`](../night_planner/standards.py#L101)).
- **Exposure time comes from magnitude alone** (`estimate_exposure(mag_r)`);
  no target is given longer integration for being more valuable.

---

## Layer 4 — Human overrides (where value re-enters)

Because the scheduler has no priority input, every real priority decision is
injected by hand:

1. **Forced targets** — `--force TNS:minutes`, handled by `reserve_forced()`
   ([`scripts/kast_calculations.py:110`](../scripts/kast_calculations.py#L110)).
   The target is placed inside its own window *ahead of* the greedy pass, and
   its slot plus a slew either side is handed back as a blocked window so the
   greedy pass fills around it. A truncated exposure is accepted deliberately
   ("a partial spectrum is the whole point of forcing it in"). Appending after
   the greedy pass cannot work — by then a fast-setting target's window shut
   hours ago.
2. **Hard-coded forced-first** — `FORCED_FIRST_TNS = 'FRB20260627D'`
   ([`lick_2026b02_calculations.py:353`](../scripts/lick_2026b02_calculations.py#L353)),
   a per-run constant for a target whose window is too tight to survive the
   greedy order.
3. **Blocks** (`--block`) — ToO/weather exclusions that every pass dodges.
4. **Author statements in prose.** "FRBs are always the main priority";
   "2026sqf is a priority filler — really interesting, but it's rising right
   now". These are honoured by *restructuring the script* for that run
   (separate pools, a forced attempt near twilight), not by setting a value.

**Precedent worth keeping** (brain v0.32): on a repeat night, the earlier
primary/extras tier split **does not carry over**. Priority is re-derived from
the author's current framing, not from a stale internal category.

---

## What is explicitly *not* a priority input

- **`priority` is not a recognised column.** `load_targets()` maps only
  `name, ra, dec, mag` (required) and `pox, tags, dm` (optional)
  ([`night_planner/targets_io.py:33-52`](../night_planner/targets_io.py#L33-L52)).
  The synthetic test tables *do* emit one —
  `'priority': np.where(df['mag'] < 18, 'A', 'B')`
  ([`scripts/make_test_target_tables.py:191`](../scripts/make_test_target_tables.py#L191)),
  visible in `test_targs/spring_ra_hours.csv` — and it is **silently dropped**
  on load. Any future priority work should start by claiming that column name.
- **P(O|x) is carried but never ranked on.** It reaches the plan only as a
  Comments string (`P(O|x)=0.993`) for the observer to read. Its one
  operational use is the `POX_MIN = 0.6` floor on the gap-fill pool.
- **Tags** (`CHIME-Repeater` etc.) are likewise display-only downstream; their
  weight was already spent in the layer-1 draw.
- **Magnitude** drives exposure time, not selection order.

The honest summary, already written in
[`Night_plans/Lick-2026B-01/HOWTO_night_plan_creation.md:584`](../Night_plans/Lick-2026B-01/HOWTO_night_plan_creation.md#L584):
*"The night plan selects from that set based on observability, not scientific
priority. Observers still down-select ~5-6 targets at the telescope based on
conditions and priorities."*

---

## Gaps a real priority system would have to close

1. **A priority column end-to-end** — recognised by `targets_io.ALIASES`,
   carried through `analyze_targets`, consumed by the scheduler, surfaced in
   the starlist and the workbook.
2. **A tie-break inside `schedule_greedy`.** The minimal change: order by
   window close, break ties by priority. The stronger change: allow a
   high-priority target to *displace* a lower one whose window is wider.
3. **A cost function** rather than a sort key — value × feasibility, so the
   FRB20250408A case resolves without a hand-written `--force`.
4. **A record of why.** Priority must land in the `TargetDecision` reason
   string, or the rejection page will explain the physics and hide the
   judgement.
5. **A convention for who sets it.** Server-side (FFFF-PZ tag weights,
   reproducible) vs. per-run (author's call, needs to be captured in a file
   rather than in chat).

---

## File map

| Concern | File |
|---------|------|
| Column recognition (no `priority`) | `night_planner/targets_io.py` |
| Primary pool / Resource JSON | `chime-ffff-pz`; see `context/claudes_context.md` |
| Gap-fill lower tier | `scripts/lick_2026b02_extras.py` |
| HA/Dec windows | `scripts/lick_2026b02_calculations.py` |
| Greedy scheduler | `scripts/lick_2026b02_night2_calculations.py` |
| General Kast entry point + forced targets | `scripts/kast_calculations.py` |
| Keck selection + mag/Dec handoff | `scripts/keck_2026oct06_calculations.py` |
| Legacy `setting_priority` | `scripts/lick_2026b01_calculations.py`, `scripts/fix_ha_limits.py` |
| Rejection staging | `night_planner/adapters.py`, `night_planner/plan_result.py` |
