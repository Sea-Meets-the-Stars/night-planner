"""
Gap-filling "extras" analysis for Lick-2026B-02 (night of 2026-09-14).

Created by JXP and Claude

Pulls the *entire* FFFF-PZ target table (`chime_ffff_pz_frbtable`, not the
per-Resource stochastic sample used for the primary 12-target list -- see
`lick_2026b02_calculations.py`) and looks for lower-priority FRBs that
could fill the primary schedule's dead-time gaps.

Candidate pool (author-confirmed criteria, 2026-09-14):
  - FFFF-PZ `status` in {AmbiguousHost, TooDusty} -- i.e. explicitly NOT
    NeedSpectrum/SpectrumPending (those are the primary pipeline's own
    active targets). RunPublicPATH is deliberately excluded (no
    identified host to point at). GoodSpectrum/Redshift are excluded
    too -- already have a measured spectrum/redshift, so re-observing
    them would waste telescope time.
  - Host P(O|x) >= 0.6 (no upper threshold is hard-coded anywhere in this
    repo -- recent Resources leave `min_POx` unset -- so 0.6 is used as
    the sole floor, per author sign-off).
  - Shane Dec <= 82 deg (same polar limit as the primary list).
  - Not already in the primary Lick-2026B-02_targets.csv pull.

These are a strictly lower tier than the primary list (lower/unknown
association confidence, or a host FFFF-PZ has already flagged as
problematic) -- kept on separate CSVs, a separate markdown table, and a
separate Excel sheet so they are never confused with the primary science
targets.
"""

import sys
from datetime import timedelta

import pandas as pd

sys.path.insert(0, '/home/lordrick/Projects/night-planner')
from scripts.lick_2026b02_calculations import DEC_LIMIT, find_twilight, target_window
from night_planner.estimate_kast_exposures import estimate_exposure

OUT_DIR = '/home/lordrick/Projects/night-planner/Night_plans/Lick-2026B-02'
FULL_TABLE_CSV = f'{OUT_DIR}/full_frb_table.csv'
PRIMARY_TARGETS_CSV = f'{OUT_DIR}/Lick-2026B-02_targets.csv'
PRIMARY_SCHEDULE_CSV = f'{OUT_DIR}/selected_targets_night1.csv'
DATE = '2026-09-14'

EXTRA_STATUSES = ('AmbiguousHost', 'TooDusty')
POX_MIN = 0.6
SLEW_MINUTES = 5


def load_candidates():
    """Filter the full FFFF-PZ table down to the extras candidate pool.

    Returns
    -------
    pd.DataFrame with TNS, RA_hours, RA_deg, Dec_deg, mag_r, POx, status,
    Tags, z -- sorted by RA_hours.
    """
    full = pd.read_csv(FULL_TABLE_CSV)
    primary = pd.read_csv(PRIMARY_TARGETS_CSV)
    already_pulled = set(primary['TNS'])

    cand = full[
        full['status'].isin(EXTRA_STATUSES)
        & (full['POx'] >= POX_MIN)
        & (full['dec'] <= DEC_LIMIT)
        & (~full['TNS'].isin(already_pulled))
        & full['Host_mag'].notna()
    ].copy()

    cand['RA_hours'] = cand['ra'] / 15.0
    cand = cand.rename(columns={'ra': 'RA_deg', 'dec': 'Dec_deg',
                                 'Host_mag': 'mag_r'})
    return (cand[['TNS', 'RA_hours', 'RA_deg', 'Dec_deg', 'mag_r', 'POx',
                  'status', 'Tags', 'z']]
            .sort_values('RA_hours').reset_index(drop=True))


def free_intervals(twilight, primary_schedule_csv=PRIMARY_SCHEDULE_CSV):
    """Idle stretches strictly *between* consecutive scheduled science
    targets (deliberately excludes evening-twilight->first-target and
    last-target->morning-twilight: those edges are already consumed by
    the fixed focus/standard-star/bias/flat calibration blocks that
    build_lick_2026b02_night_plan.py wraps around the science schedule,
    not free time). Each interval is shrunk by one SLEW_MINUTES buffer on
    both ends, so a placed extra never eats into the slew to/from the
    primary targets bracketing the gap.

    Returns
    -------
    list of (start_pst, end_pst) tuples, in time order.
    """
    sched = pd.read_csv(primary_schedule_csv)
    sched = sched[sched['scheduled'].astype(str) == 'True'].copy()
    sched['start_pst'] = pd.to_datetime(sched['start_pst'], format='mixed')
    sched['end_pst'] = pd.to_datetime(sched['end_pst'], format='mixed')
    sched = sched.sort_values('start_pst').reset_index(drop=True)

    intervals = []
    for i in range(len(sched) - 1):
        start = sched.loc[i, 'end_pst'] + timedelta(minutes=SLEW_MINUTES)
        end = sched.loc[i + 1, 'start_pst'] - timedelta(minutes=SLEW_MINUTES)
        if (end - start).total_seconds() > 0:
            intervals.append((start, end))
    return intervals


def analyze_candidates(cand_df, twilight):
    """Compute each candidate's HA-legal window for the night (same
    target_window() used for the primary list).

    Returns
    -------
    pd.DataFrame, one row per candidate, with observable/entry_pst/
    exit_pst/ha_entry/ha_exit added.
    """
    rows = []
    for _, row in cand_df.iterrows():
        window = target_window(row['RA_hours'], row['Dec_deg'], twilight)
        rec = dict(row)
        if window is None:
            rec.update(observable=False, entry_pst=None, exit_pst=None,
                       ha_entry=None, ha_exit=None)
        else:
            entry_time, exit_time, ha_entry, ha_exit = window
            rec.update(observable=True, entry_pst=entry_time,
                       exit_pst=exit_time, ha_entry=ha_entry, ha_exit=ha_exit)
        rows.append(rec)
    return pd.DataFrame(rows).sort_values('RA_hours').reset_index(drop=True)


def schedule_extras(analysis_df, twilight):
    """Greedily slot HA-observable extras into the primary schedule's idle
    intervals, earliest-window-close-first (mirrors schedule_night() in
    lick_2026b02_calculations.py, but placing into gaps rather than a
    fresh timeline).

    Returns
    -------
    pd.DataFrame, one row per HA-observable candidate, scheduled=True/False
    plus start_pst/end_pst/skip_reason as appropriate.
    """
    # cursor per interval starts at that interval's (already slew-buffered)
    # start; gap_end is fixed (also already slew-buffered against the next
    # primary target)
    cursors = free_intervals(twilight)

    observable = analysis_df[analysis_df['observable']].copy()
    observable = observable.sort_values('exit_pst').reset_index(drop=True)

    schedule = []
    for _, row in observable.iterrows():
        red, blue, dur_s = estimate_exposure(row['mag_r'])
        dur_min = dur_s / 60.0

        placed = False
        for idx, (cursor, gap_end) in enumerate(cursors):
            window_close = min(gap_end, row['exit_pst'])
            start = max(cursor, row['entry_pst'])
            end = start + timedelta(minutes=dur_min)
            if start < window_close and end <= window_close:
                schedule.append(dict(row, scheduled=True, start_pst=start,
                                      end_pst=end, duration_min=dur_min,
                                      red_side=red, blue_side=blue,
                                      gap_used=idx))
                cursors[idx] = (end + timedelta(minutes=SLEW_MINUTES), gap_end)
                placed = True
                break
        if not placed:
            schedule.append(dict(
                row, scheduled=False,
                skip_reason=("no idle interval overlaps this target's HA "
                             "window for long enough to fit its "
                             f"{dur_min:.0f} min exposure")))

    return pd.DataFrame(schedule)


def fmt_hms(hours):
    hours = hours % 24
    h = int(hours)
    m = int((hours - h) * 60)
    s = ((hours - h) * 60 - m) * 60
    return f"{h:02d}h{m:02d}m{s:04.1f}s"


def write_report(analysis_df, sched_df, twilight, outfile):
    intervals = free_intervals(twilight)
    lines = []
    lines.append(f"# Gap-fill extras analysis -- Lick-2026B-02, night of "
                  f"{DATE}")
    lines.append("")
    lines.append("Candidate pool: FFFF-PZ full-table pull "
                  f"(`{FULL_TABLE_CSV.split('/')[-1]}`), status in "
                  f"{EXTRA_STATUSES}, P(O|x) >= {POX_MIN}, Dec <= "
                  f"{DEC_LIMIT:.0f} deg, excluding TNS already in the "
                  "primary 12-target pull. These are a lower tier than "
                  "the primary science list -- kept separate here and on "
                  "their own Excel sheet.")
    lines.append("")
    lines.append("Idle intervals available in the primary schedule "
                  "(evening twilight/between targets/morning twilight):")
    for start, end in intervals:
        mins = (end - start).total_seconds() / 60.0
        lines.append(f"- {start:%H:%M}-{end:%H:%M} PST ({mins:.0f} min)")
    lines.append("")

    n_cand = len(analysis_df)
    n_obs = int(analysis_df['observable'].sum())
    n_sched = int(sched_df['scheduled'].sum()) if len(sched_df) else 0
    lines.append(f"**Summary:** {n_cand} candidates after filtering, "
                  f"{n_obs} HA-observable tonight, {n_sched} scheduled "
                  "into gaps.")
    lines.append("")

    lines.append("## Scheduled extras")
    lines.append("")
    lines.append("| TNS | RA (h) | Dec (deg) | mag | P(O\\|x) | status | "
                  "HA start->end | Start-End (PST) | red | blue |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    if n_sched:
        for _, r in sched_df[sched_df['scheduled']].sort_values('start_pst').iterrows():
            lines.append(
                f"| {r['TNS']} | {r['RA_hours']:.2f} | {r['Dec_deg']:.2f} | "
                f"{r['mag_r']:.2f} | {r['POx']:.3f} | {r['status']} | "
                f"{r['ha_entry']:+.2f} -> {r['ha_exit']:+.2f} | "
                f"{r['start_pst']:%H:%M}-{r['end_pst']:%H:%M} | "
                f"{r['red_side']} | {r['blue_side']} |")
    lines.append("")

    lines.append("## HA-observable but not scheduled")
    lines.append("")
    lines.append("| TNS | RA (h) | mag | P(O\\|x) | status | HA window | reason |")
    lines.append("|---|---|---|---|---|---|---|")
    if len(sched_df):
        skipped = sched_df[~sched_df['scheduled']]
        for _, r in skipped.iterrows():
            lines.append(
                f"| {r['TNS']} | {r['RA_hours']:.2f} | {r['mag_r']:.2f} | "
                f"{r['POx']:.3f} | {r['status']} | {r['ha_entry']:+.2f} -> "
                f"{r['ha_exit']:+.2f} | {r['skip_reason']} |")
    lines.append("")

    lines.append("## Never HA-legal tonight")
    lines.append("")
    lines.append("| TNS | RA (h) | mag | P(O\\|x) | status |")
    lines.append("|---|---|---|---|---|")
    for _, r in analysis_df[~analysis_df['observable']].iterrows():
        lines.append(f"| {r['TNS']} | {r['RA_hours']:.2f} | {r['mag_r']:.2f} "
                      f"| {r['POx']:.3f} | {r['status']} |")
    lines.append("")

    with open(outfile, 'w') as f:
        f.write("\n".join(lines) + "\n")


def main():
    twilight = find_twilight(DATE)

    cand_df = load_candidates()
    analysis_df = analyze_candidates(cand_df, twilight)
    sched_df = schedule_extras(analysis_df, twilight)

    analysis_df.to_csv(f'{OUT_DIR}/extras_analysis.csv', index=False)
    sched_df.to_csv(f'{OUT_DIR}/extras_schedule.csv', index=False)
    write_report(analysis_df, sched_df, twilight,
                 f'{OUT_DIR}/extras_gap_fill_analysis.md')

    n_sched = int(sched_df['scheduled'].sum()) if len(sched_df) else 0
    print(f"{len(cand_df)} extras candidates after filtering "
          f"(status in {EXTRA_STATUSES}, POx>={POX_MIN}, Dec<={DEC_LIMIT:.0f}, "
          "not already in primary pull)")
    print(f"{int(analysis_df['observable'].sum())} HA-observable tonight; "
          f"{n_sched} scheduled into idle intervals")
    print(f"Wrote {OUT_DIR}/extras_analysis.csv, "
          f"{OUT_DIR}/extras_schedule.csv, "
          f"{OUT_DIR}/extras_gap_fill_analysis.md")
    return analysis_df, sched_df, twilight


if __name__ == '__main__':
    main()
