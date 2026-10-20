"""
General Lick/Kast night planning: any target table, any date.

The machinery this stands on is already general -- `target_window()`,
`find_twilight()` and the earliest-window-close-first scheduler all live
in lick_2026b02_calculations / lick_2026b02_night2_calculations. What was
missing was an entry point not pinned to one run: those modules hardcode
Lick-2026B-02 and 2026-09-15.

This mirrors the Keck module's interface (--targets-csv / --output-dir /
--date / --start / --block / --force) so the CLI and the viewer can drive
either instrument the same way.

Created by JXP and Claude
"""

import os
import sys
from pathlib import Path
from datetime import timedelta

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / 'scripts'))

from scripts.lick_2026b02_calculations import (
    DEC_LIMIT, HA_MAX, HA_MIN, LICK, PST, SLEW_MINUTES,
    find_twilight, ha_at, target_window,
)
# schedule_greedy is general (observable frame + explicit start/end, with
# blocked-window support); it just happens to live in the night-2 module.
from scripts.lick_2026b02_night2_calculations import schedule_greedy
# _overlapping_block is the one place that knows how a slot and a block
# collide; a forced slot has to truncate on the same rule the scheduler
# fits around, so it is borrowed rather than reimplemented here.
from schedule_overrides import (advance, _overlapping_block, fit_around_blocks,
                                push_past_blocks)
from night_planner.targets_io import load_targets
from night_plan_io import (
    OBSERVATORY_TZ, load_config, resolve_blocks, resolve_local_dt,
    save_night_meta,
)
from night_planner.estimate_kast_exposures import estimate_exposure

# Opening overheads, matching the Lick Excel builders.
FOCUS_MINUTES = 10
STD_STAR_MINUTES = 10

# Shortest partial exposure worth pointing the telescope at. A target the
# scheduler dropped for want of time is put in anyway for whatever is left,
# but a two-minute slot buys nothing and costs a slew either side.
MIN_PARTIAL_MINUTES = 10


def analyze_targets(targets_csv, date_str, mapping=None):
    """
    Per-target HA window for a Lick night.

    Unlike lick_2026b02_calculations.analyze_targets, a target above the
    Dec limit is kept with a reason rather than dropped: the viewer's
    rejection page should be able to say *why* something is absent, and
    "silently filtered out" is the one answer that helps nobody.

    Parameters
    ----------
    targets_csv : str or DataFrame
        Any table; columns normalized by night_planner.targets_io.
    date_str : str
    mapping : targets_io.ColumnMapping, optional

    Returns
    -------
    (results_df, twilight)
    """
    df = load_targets(targets_csv, mapping=mapping)
    twilight = find_twilight(date_str)

    rows = []
    for _, row in df.iterrows():
        ra_hours = row['ra_deg'] / 15.0
        dec_deg = row['dec_deg']
        rec = {
            'TNS': row['name'], 'RA_deg': row['ra_deg'], 'Dec_deg': dec_deg,
            'RA_hours': ra_hours, 'mag_r': row['mag'], 'POx': row['pox'],
            'tags': row['tags'], 'DM': row['dm'],
            'priority': row['priority'],
        }

        if dec_deg > DEC_LIMIT:
            rec.update(observable=False, entry_pst=None, exit_pst=None,
                       ha_entry=None, ha_exit=None, window_min=0,
                       limit_reason=(f'Dec {dec_deg:+.2f} > +{DEC_LIMIT:.0f}: '
                                      f'above the Shane mechanical limit'))
            rows.append(rec)
            continue

        window = target_window(ra_hours, dec_deg, twilight)
        if window is None:
            rec.update(observable=False, entry_pst=None, exit_pst=None,
                       ha_entry=None, ha_exit=None, window_min=0,
                       limit_reason=(f'never inside the Shane HA window '
                                      f'({HA_MIN:+.2f}h to {HA_MAX:+.2f}h) '
                                      f'during the night'))
        else:
            entry, exit_, ha_entry, ha_exit = window
            rec.update(observable=True, entry_pst=entry, exit_pst=exit_,
                       ha_entry=ha_entry, ha_exit=ha_exit, limit_reason='',
                       window_min=(exit_ - entry).total_seconds() / 60.0)
        rows.append(rec)

    results_df = pd.DataFrame(rows).sort_values('RA_hours').reset_index(drop=True)
    return results_df, twilight


def reserve_forced(results_df, forced, science_start, night_end, blocks,
                    failures=None):
    """
    Place forced targets inside their own windows, ahead of the greedy pass.

    Appending a forced target after the normal schedule only ever works
    for something still up at the end of the night. The targets actually
    worth rescuing are the opposite case: a fast-setting host the
    scheduler dropped because its *full* exposure would not fit the
    sliver of HA window it had left. By the time the normal schedule
    finishes, that window shut hours ago, so an append-only rescue can
    only fail.

    Each forced target is therefore placed at the earliest clock time the
    mount can legally point there, truncated to whatever its window and
    the night allow, and the slot -- plus a slew either side -- is handed
    back as a blocked window so schedule_greedy fills the rest of the
    night around it instead of over it.

    Parameters
    ----------
    results_df : DataFrame
        Output of analyze_targets().
    forced : list of (TNS, minutes)
    science_start, night_end : datetime
    blocks : list of (start, end, reason)
        Blocks already in force (ToO, weather); forced slots dodge these.
    failures : list, optional
        Appended with {'TNS', 'reason'} for every target not placed, so
        the viewer can say why rather than silently dropping the request.

    Returns
    -------
    (rows, reservations)
        Schedule rows to concatenate, and (start, end, reason) tuples to
        add to the block list before scheduling the rest.
    """
    rows, reservations = [], []
    res = results_df.set_index('TNS')
    slew = timedelta(minutes=SLEW_MINUTES)

    def fail(tns, reason):
        if failures is not None:
            failures.append({'TNS': tns, 'reason': reason})
        print(f'  Forced {tns}: {reason}')

    for tns, minutes in forced:
        if tns not in res.index:
            fail(tns, 'not in the target table')
            continue
        row = res.loc[tns]
        if not row['observable'] or row['exit_pst'] is None:
            fail(tns, f"not observable tonight -- {row['limit_reason']}")
            continue

        taken = list(blocks) + reservations
        close = min(row['exit_pst'], night_end)
        earliest = push_past_blocks(max(science_start, row['entry_pst']), taken)
        if earliest >= close:
            fail(tns, f"window closes {close:%H:%M}, and the earliest clear "
                      f"slot is {earliest:%H:%M}")
            continue

        # As late inside its own window as the requested time allows. A
        # setting target lands at the top of the night because that is all
        # it has; a rising one lands at the end, where it was going to be
        # observed anyway -- either way the reservation eats the least of
        # everyone else's time.
        start = max(earliest, advance(close, -minutes))
        start = push_past_blocks(start, taken)
        end = min(advance(start, minutes), close)
        # Truncate at the next block rather than refusing the target: a
        # partial spectrum is the whole point of forcing it in.
        hit = _overlapping_block(start, end, taken)
        if hit is not None:
            end = hit[0]
        got = (end - start).total_seconds() / 60.0
        if got < 1:
            fail(tns, f"no usable time at {start:%H:%M} before the next "
                      f"block or its {close:%H:%M} window close")
            continue

        red, blue, _ = estimate_exposure(row['mag_r'])
        rows.append(dict(row, TNS=tns, scheduled=True, start_pst=start,
                         end_pst=end, duration_min=got, red_side=red,
                         blue_side=blue,
                         skip_reason=(f'FORCED truncated exposure: {got:.0f} of '
                                       f'{minutes:g} min requested')))
        reservations.append((start - slew, end + slew, f'forced {tns}'))
        print(f'  Forced {tns}: {start:%H:%M}-{end:%H:%M} ({got:.0f} min)')
    return rows, reservations


def parse_args(argv=None):
    """CLI mirroring the Keck module, so the dispatcher can drive either."""
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', help='Night-plan JSON config; CLI flags win.')
    p.add_argument('--start', help='Manual night-start override, HH:MM real '
                                   'local Lick time (PST or PDT by date).')
    p.add_argument('--block', action='append', default=[],
                   help='Blocked window, "HH:MM-HH:MM[@reason]". Repeatable.')
    p.add_argument('--force', action='append', default=[],
                   help='Force a target in with a truncated exposure, '
                        '"TNS@MINUTES". Repeatable.')
    p.add_argument('--targets-csv')
    p.add_argument('--output-dir')
    p.add_argument('--date')
    p.add_argument('--max-targets', type=int)
    p.add_argument('--no-partials', action='store_true',
                   help='Do not backfill idle time with truncated exposures '
                        'of targets that were dropped for want of time.')
    p.add_argument('--min-partial', type=float, default=MIN_PARTIAL_MINUTES,
                   help=f'Shortest partial exposure worth scheduling, in '
                        f'minutes (default {MIN_PARTIAL_MINUTES}).')
    return p.parse_args(argv)


def _parse_block_flag(spec):
    window, _, reason = spec.partition('@')
    start, end = window.split('-')
    return {'start': start, 'end': end, 'reason': reason or 'blocked'}


def free_gaps(placements, window_start, window_end, slew_min=SLEW_MINUTES):
    """
    Idle intervals left over between a set of placements.

    Created by JXP and Claude

    Written here rather than reused because nothing existing fits: the
    well-formed one, PlanResult.idle_gaps(), needs an assembled PlanResult
    and so runs a layer after the scheduler, while free_intervals() in
    lick_2026b02_extras.py is bound to one run's CSV paths and date. This
    is the same sweep as the inline one in lick_2026b02_night2_calculations,
    kept as a function so the tier loop and its tests can both call it.

    Each gap is shrunk by a slew at both ends, because the mount has to get
    there and then get back to whatever was already booked.

    Inputs
    ------
    placements : iterable of mapping
        Rows with 'start_pst' and 'end_pst'; anything else is ignored.
    window_start, window_end : datetime
        Bounds of the night being filled.
    slew_min : float
        Minutes reserved either side of every existing placement.

    Outputs
    -------
    list of (start, end) datetime pairs, in time order, each strictly
    positive in length. Includes the leading and trailing edges -- time
    before the first target and after the last is just as fillable as a
    hole in the middle.
    """
    busy = sorted((p['start_pst'], p['end_pst']) for p in placements)

    gaps, cursor = [], window_start
    for start, end in busy:
        gap_end = advance(start, -slew_min)
        if gap_end > cursor:
            gaps.append((cursor, gap_end))
        # max(): placements can abut or overlap (a forced reservation sits
        # across one), and a cursor that walked backwards would invent a gap.
        cursor = max(cursor, advance(end, slew_min))
    if window_end > cursor:
        gaps.append((cursor, window_end))
    return gaps


def backfill_partials(schedule_rows, science_start, night_end, blocks,
                      min_minutes=MIN_PARTIAL_MINUTES):
    """
    Put dropped targets into the leftover gaps, truncated to fit.

    Created by JXP and Claude

    The scheduler is all-or-nothing: a target needing 90 minutes with 60
    left in its window is dropped, and those 60 minutes are then spent on
    nothing at all. A short spectrum is usually worth more than an empty
    telescope -- it can still classify, and it is data where otherwise
    there was none -- so anything dropped for want of time is placed anyway
    for however long is actually available.

    These are marked, not hidden. Every row this adds carries a skip_reason
    beginning 'PARTIAL', which the viewer turns into its own colour and a
    note saying how much of the needed exposure it got, so the observer can
    drop it at the telescope if they would rather have the idle time.

    Targets that were never observable are untouched -- no amount of
    truncation fixes a target below the horizon.

    Inputs
    ------
    schedule_rows : DataFrame
        The schedule so far, scheduled and rejected rows together.
    science_start, night_end : datetime
        Bounds of the schedulable night.
    blocks : list of (start, end, reason)
        Blocked windows, which partials must dodge like anything else.
    min_minutes : float
        Shortest partial worth placing.

    Outputs
    -------
    DataFrame with the same rows, except that any target this pass could
    place is replaced by its scheduled, truncated row.
    """
    # On a night where nothing is up, schedule_greedy returns a frame with no
    # columns at all -- see the schema guarantee in run(). Nothing to backfill
    # into, and asking for 'scheduled' would raise.
    if not len(schedule_rows) or 'scheduled' not in schedule_rows.columns:
        return schedule_rows

    scheduled_mask = schedule_rows['scheduled'].fillna(False).astype(bool)
    placed = schedule_rows[scheduled_mask].to_dict('records')
    dropped = schedule_rows[~scheduled_mask]
    if not len(dropped):
        return schedule_rows

    # Only targets that have a real window tonight and simply ran out of
    # room in it. A missing entry/exit means it was never up.
    candidates = [r for _, r in dropped.iterrows()
                  if r.get('observable') and pd.notna(r.get('entry_pst'))
                  and pd.notna(r.get('exit_pst'))]
    if not candidates:
        return schedule_rows

    # Best targets first: a partial of a P1 host beats a partial of a P3
    # filler when both want the same gap.
    candidates.sort(key=lambda r: (r.get('priority', 1.0), r['exit_pst']))

    filled = {}
    for row in candidates:
        for gap_start, gap_end in free_gaps(placed, science_start, night_end):
            # The usable slice is the overlap of the gap with the target's
            # own HA window -- truncating does not excuse pointing the
            # mount somewhere it cannot go.
            start = max(gap_start, row['entry_pst'])
            close = min(gap_end, row['exit_pst'])
            if (close - start).total_seconds() / 60.0 < min_minutes:
                continue
            start, end = fit_around_blocks(
                start, (close - start).total_seconds() / 60.0, close, blocks)
            if start is None:
                continue

            got = (end - start).total_seconds() / 60.0
            if got < min_minutes:
                continue

            red, blue, dur_s = estimate_exposure(row['mag_r'])
            needed = dur_s / 60.0
            new_row = dict(
                row, scheduled=True, start_pst=start, end_pst=end,
                duration_min=got, red_side=red, blue_side=blue,
                skip_reason=(
                    f'PARTIAL: {got:.0f} of the {needed:.0f} min this target '
                    f'needs ({got / needed * 100:.0f}%). Scheduled into idle '
                    f'time rather than left out -- expect low S/N, and drop '
                    f'it if you would rather have the gap.'))
            filled[row['TNS']] = new_row
            placed.append(new_row)
            break

    if not filled:
        return schedule_rows

    total = sum(r['duration_min'] for r in filled.values())
    print(f'\nBackfilled {len(filled)} partial exposure(s) into idle time '
          f'({total:.0f} min): ' + ', '.join(sorted(filled)))

    # Rebuild from records throughout: mixing Series and dicts in the list
    # makes pandas try to align them and fail on the dtype.
    rows = [filled.get(r['TNS'], r) for r in schedule_rows.to_dict('records')]
    return pd.DataFrame(rows).reset_index(drop=True)


def schedule_by_priority(observable, science_start, night_end, blocks):
    """
    Schedule in priority tiers, best first, lower tiers filling the gaps.

    Created by JXP and Claude

    The model is the UCSC AstroScheduler's priority-sequential solve (see
    docs/priority_comparison_astroscheduler.md): tiers are scheduled in
    order and everything already placed is immovable, so a lower-priority
    target can never displace a higher-priority one.

    Lower tiers are scheduled gap by gap rather than by one more pass over
    the whole night with the earlier placements passed as blocks. That is
    forced by the machinery, not a preference: fit_around_blocks() can only
    ever push a target *later* (schedule_overrides.py), and schedule_greedy
    walks a cursor that never rewinds -- so a single later pass would sail
    past every gap it had already crossed. Restarting inside each gap is
    what the night-2 module does, and it works.

    With one tier this makes exactly one schedule_greedy call over the whole
    night, which is the call this function replaced -- an un-prioritised
    table therefore schedules precisely as it did before tiers existed.

    Inputs
    ------
    observable : DataFrame
        Observable targets from analyze_targets(), carrying 'priority'.
    science_start, night_end : datetime
        Bounds of the schedulable night.
    blocks : list of (start, end, reason)
        Blocked windows, honoured by every tier.

    Outputs
    -------
    DataFrame of schedule rows, one per target: the scheduled rows from
    every tier, plus one rejected row for each target no tier could place.
    """
    tiers = sorted(observable['priority'].dropna().unique())
    if len(tiers) <= 1:
        # The single-tier path is the old behaviour, preserved exactly.
        sched, _ = schedule_greedy(observable, science_start, night_end,
                                   blocks=blocks)
        return sched

    print(f'\nScheduling in {len(tiers)} priority tiers: '
          + ', '.join(f'P{t:g}' for t in tiers))

    frames = []
    placed = []     # every row placed so far, across all tiers

    for position, tier in enumerate(tiers):
        pool = observable[observable['priority'] == tier]
        if not len(pool):
            continue

        if position == 0:
            sched, _ = schedule_greedy(pool, science_start, night_end,
                                       blocks=blocks)
            frames.append(sched)
            got = sched[sched['scheduled']] if len(sched) else sched
            placed.extend(got.to_dict('records'))
            print(f'  P{tier:g}: {len(got)}/{len(pool)} scheduled '
                  f'(first pass, whole night)')
            continue

        # Lower tiers: one pass per idle interval the tiers above left.
        gaps = free_gaps(placed, science_start, night_end)
        remaining = pool
        for gap_start, gap_end in gaps:
            if not len(remaining):
                break
            sched, _ = schedule_greedy(remaining, gap_start, gap_end,
                                       blocks=blocks)
            got = sched[sched['scheduled']] if len(sched) else sched
            if not len(got):
                continue
            frames.append(got)
            placed.extend(got.to_dict('records'))
            remaining = remaining[~remaining['TNS'].isin(got['TNS'])]

        # One rejection per target, not one per gap it failed in: a target
        # that missed four gaps is still a single target the observer has
        # to decide about, and four identical rows only bury that.
        for _, row in remaining.iterrows():
            _, _, dur_s = estimate_exposure(row['mag_r'])
            frames.append(pd.DataFrame([dict(
                row, scheduled=False,
                skip_reason=(f'priority P{tier:g}: needs '
                             f'{dur_s / 60.0:.0f} min, and no idle interval '
                             f'left by the {position} higher-priority '
                             f'tier(s) was long enough inside its HA window'))]))

        print(f'  P{tier:g}: {len(pool) - len(remaining)}/{len(pool)} '
              f'scheduled into {len(gaps)} gap(s)')

    return pd.concat(frames, ignore_index=True)


def run(args):
    """Execute the pipeline for an already-parsed args namespace."""
    cfg = load_config(args.config) if args.config else None

    targets_csv = args.targets_csv or (cfg.targets_csv if cfg else None)
    output_dir = args.output_dir or (cfg.output_dir if cfg else None)
    date = args.date or (cfg.date if cfg else None)
    if not (targets_csv and output_dir and date):
        raise SystemExit('kast needs --targets-csv, --output-dir and --date')

    tz = OBSERVATORY_TZ['lick']
    start_spec = args.start or (cfg.start_override if cfg else None)
    block_specs = list(cfg.blocks) if cfg else []
    block_specs += [_parse_block_flag(b) for b in args.block]
    blocks = resolve_blocks(date, block_specs, tz)
    start_override = resolve_local_dt(date, start_spec, tz) if start_spec else None

    forced = []
    for spec in args.force:
        tns, _, minutes = spec.partition('@')
        forced.append((tns, float(minutes)))

    os.makedirs(output_dir, exist_ok=True)

    results_df, twilight = analyze_targets(targets_csv, date)
    night_start = start_override or twilight['evening_pst']
    night_end = twilight['morning_pst']
    if night_start >= night_end:
        # A start past dawn is a typo, not a short night. Without this
        # the run reports a negative-length night and schedules nothing,
        # which reads as "no targets are up".
        raise SystemExit(
            f'--start {night_start:%H:%M} is at or after morning twilight '
            f'({night_end:%H:%M}); there is no night left to schedule')

    print(f"\n=== LICK/KAST {date} ===")
    print(f"Evening 18deg twilight: {twilight['evening_pst']:%H:%M} "
          f"{twilight['evening_pst'].tzname()}")
    print(f"Morning 18deg twilight: {night_end:%H:%M} {night_end.tzname()}")
    if start_override:
        print(f'Manual night start: {night_start:%H:%M}')
    for b_start, b_end, reason in blocks:
        print(f'  blocked {b_start:%H:%M}-{b_end:%H:%M} ({reason})')

    n_obs = int(results_df['observable'].sum())
    print(f'\nObservable: {n_obs} / {len(results_df)}')

    # Science starts after the dome-open focus and the evening standard.
    science_start = advance(night_start, FOCUS_MINUTES + STD_STAR_MINUTES)
    forced_failures, forced_rows, reservations = [], [], []
    if forced:
        forced_rows, reservations = reserve_forced(
            results_df, forced, science_start, night_end, blocks,
            failures=forced_failures)

    observable = results_df[results_df['observable']]
    placed = {r['TNS'] for r in forced_rows}
    if placed:
        # Already slotted above; leaving it in would schedule it twice.
        observable = observable[~observable['TNS'].isin(placed)]

    sched = schedule_by_priority(observable, science_start, night_end,
                                  list(blocks) + reservations)
    if not getattr(args, 'no_partials', False):
        sched = backfill_partials(sched, science_start, night_end,
                                   list(blocks) + reservations,
                                   min_minutes=getattr(args, 'min_partial',
                                                       MIN_PARTIAL_MINUTES))
    if forced_rows:
        sched = pd.concat([sched, pd.DataFrame(forced_rows)], ignore_index=True)

    # schedule_greedy builds a dict per row and only a *scheduled* row
    # gets a start time, so on a night where nothing is observable these
    # columns are absent entirely rather than empty. "Nothing is up
    # tonight" is a legitimate answer -- running a winter table on a
    # summer date, say -- and it must produce an empty plan, not a
    # KeyError. Guaranteeing the schema here fixes every consumer at
    # once, the written CSV included.
    for column in ('scheduled', 'start_pst', 'end_pst', 'duration_min',
                    'red_side', 'blue_side', 'skip_reason'):
        if column not in sched.columns:
            sched[column] = False if column == 'scheduled' else pd.NA

    if args.max_targets:
        # Trim by priority first, then by time. Trimming by start time alone
        # -- which is what this did before tiers existed -- would throw away
        # a top-priority target late in the night to keep a filler that
        # happened to start early, quietly undoing the tier loop above.
        keep = (sched[sched['scheduled']]
                .sort_values(['priority', 'start_pst'])
                .head(args.max_targets))
        sched = pd.concat([keep, sched[~sched['scheduled']]], ignore_index=True)

    done = sched[sched['scheduled'].fillna(False).astype(bool)]
    science_min = done['duration_min'].sum() if len(done) else 0
    night_min = (night_end - night_start).total_seconds() / 60
    share = 100 * science_min / night_min if night_min else 0
    print(f'Scheduled {len(done)} targets, {science_min:.0f} min science / '
          f'{night_min:.0f} min night ({share:.0f}%)')
    for _, r in done.sort_values('start_pst').iterrows():
        print(f"  {r['start_pst']:%H:%M}-{r['end_pst']:%H:%M}  {r['TNS']:14s} "
              f"mag {r['mag_r']:.2f}  red {r['red_side']} blue {r['blue_side']}")

    results_df.to_csv(f'{output_dir}/target_analysis.csv', index=False)
    sched.to_csv(f'{output_dir}/selected_targets.csv', index=False)
    save_night_meta(output_dir, start_local=night_start,
                     evening_twilight_local=twilight['evening_pst'],
                     morning_twilight_local=night_end,
                     blocks=blocks, date=date)
    print(f'\nWrote target_analysis.csv, selected_targets.csv, '
          f'night_meta.json to {output_dir}')

    return {
        'repeat_analysis': results_df,
        'spare_analysis': results_df.iloc[0:0],
        'frb_sched': sched,
        'spare_sched': sched.iloc[0:0],
        'twilight': twilight,
        'start_local': night_start,
        'night_end': night_end,
        'blocks': blocks,
        'forced_failures': forced_failures,
        'output_dir': output_dir,
        'date': date,
    }


def main():
    """Standalone entry point."""
    return run(parse_args())


if __name__ == '__main__':
    main()
