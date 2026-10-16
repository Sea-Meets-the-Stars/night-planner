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
from datetime import timedelta

import pandas as pd

sys.path.insert(0, '/home/lordrick/Projects/night-planner')
sys.path.insert(0, '/home/lordrick/Projects/night-planner/scripts')

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
from schedule_overrides import advance, _overlapping_block, push_past_blocks
from night_planner.targets_io import load_targets
from night_plan_io import (
    OBSERVATORY_TZ, load_config, resolve_blocks, resolve_local_dt,
    save_night_meta,
)
from night_planner.estimate_kast_exposures import estimate_exposure

# Opening overheads, matching the Lick Excel builders.
FOCUS_MINUTES = 10
STD_STAR_MINUTES = 10


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
    return p.parse_args(argv)


def _parse_block_flag(spec):
    window, _, reason = spec.partition('@')
    start, end = window.split('-')
    return {'start': start, 'end': end, 'reason': reason or 'blocked'}


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

    sched, _ = schedule_greedy(observable, science_start, night_end,
                                blocks=list(blocks) + reservations)
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
        keep = sched[sched['scheduled']].nsmallest(args.max_targets, 'start_pst')
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
