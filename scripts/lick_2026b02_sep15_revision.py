"""
Created by JXP and Claude

Revise the Lick-2026B-02 Night-2 (2026-09-15/16) spare/filler schedule per
the author's two explicit changes to the plan already built by
lick_2026b02_night2_calculations.py / build_lick_2026b02_night2_plan.py:

  1. Replace the spare/filler target 2026yum with an author-supplied DLA
     sightline, DLA_J0210+1702 (RA 02:10:11.00, Dec +17:02:45.0, J2000),
     given a fixed exptime=3600 s directly (not derived from the
     mag-based Kast heuristic in estimate_kast_exposures.estimate_exposure
     -- this target has no magnitude given, only a literal exposure time).
  2. Add 2026sqf (a spare the author flagged night 1 as "really
     interesting... rising right now") at the very end of the night, per
     the author's explicit 2026-09-15 instruction. lick_2026b02_night2_
     calculations.py already worked out that 2026sqf's Shane HA-legal
     window (-5.0h<=HA<=+3.75h) does not open until AFTER both the formal
     18-deg morning twilight (05:22 PDT) and actual sunrise (06:50 PDT) --
     07:03 PDT, 13 min after sunrise -- so this is not a truncation-style
     forced attempt (c.f. FRB20260627D's forced_first on both nights): the
     mount cannot physically point there until full daylight. Scheduled
     anyway, transparently, as a post-twilight bonus/dawn attempt per the
     author's explicit override, not folded into the dark-night schedule.

The FRB-repeat schedule (main priority) is untouched -- read directly from
night2_frb_repeat_schedule.csv -- since neither change affects it; only the
spare/filler analysis + schedule (night2_spare_analysis.csv,
night2_spare_schedule.csv) are regenerated, using the same idle-gap-finding
and greedy earliest-window-close-first logic as
lick_2026b02_night2_calculations.py, so the two stay procedurally
consistent.
"""

import sys
from datetime import timedelta

import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord

sys.path.insert(0, '/home/lordrick/Projects/night-planner')
from scripts.lick_2026b02_calculations import find_twilight, target_window
from scripts.lick_2026b02_night2_calculations import (
    OUT_DIR, DATE, SLEW_MINUTES, SPARE_TARGETS, analyze, schedule_greedy,
    never_legal_diagnostic,
)
from night_planner.estimate_kast_exposures import estimate_exposure

# Author's explicit swap, 2026-09-15: drop 2026yum, add this DLA sightline
# in its place. Fixed exptime given directly (no magnitude/filter supplied).
DLA_TARGET = dict(TNS='DLA_J0210+1702', ra_str='02:10:11.00',
                   dec_str='+17:02:45.0', exptime_s=3600)

# Author's explicit end-of-night add, 2026-09-15.
FORCE_LAST_TNS = '2026sqf'

# Targets with an author-given fixed exptime instead of a Kast mag-based
# estimate (schedule_greedy would otherwise call estimate_exposure(mag_r),
# which is undefined here since no mag was supplied for the DLA sightline).
FIXED_EXPTIME_S = {DLA_TARGET['TNS']: DLA_TARGET['exptime_s']}


def load_updated_spare_targets():
    """Rebuild the spare/filler target list with 2026yum replaced by the
    DLA sightline, in the same RA_hours/RA_deg/Dec_deg/mag_r schema
    load_spare_targets() uses in lick_2026b02_night2_calculations.py.

    Returns
    -------
    pd.DataFrame
    """
    rows = []
    for t in SPARE_TARGETS:
        if t['TNS'] == '2026yum':
            continue  # replaced by the DLA sightline below
        c = SkyCoord(f"{t['ra_str']} {t['dec_str']}", unit=(u.hourangle, u.deg))
        rows.append(dict(TNS=t['TNS'], RA_hours=c.ra.hour, RA_deg=c.ra.deg,
                          Dec_deg=c.dec.deg, mag_r=t['mag'], POx=None,
                          tags=f"spare/filler ({t['filt']}-band mag given, "
                               "used as r-mag proxy)",
                          DM=None, origin='spare'))

    c = SkyCoord(f"{DLA_TARGET['ra_str']} {DLA_TARGET['dec_str']}",
                 unit=(u.hourangle, u.deg))
    rows.append(dict(TNS=DLA_TARGET['TNS'], RA_hours=c.ra.hour, RA_deg=c.ra.deg,
                      Dec_deg=c.dec.deg, mag_r=None, POx=None,
                      tags='author-supplied DLA sightline, fixed exptime=3600s '
                           '(no mag given -- not a Kast-heuristic estimate)',
                      DM=None, origin='spare_fixed_exptime'))
    return pd.DataFrame(rows)


def schedule_greedy_fixed(observable_df, start_time, end_time):
    """Same earliest-window-close-first greedy scheduler as
    lick_2026b02_night2_calculations.schedule_greedy(), except a target
    named in FIXED_EXPTIME_S uses its author-given exptime directly
    instead of estimate_exposure(mag_r) (undefined for a target with no
    magnitude, like the DLA sightline).
    """
    observable = observable_df.copy().sort_values('exit_pst').reset_index(drop=True)
    schedule = []
    current_time = start_time

    for _, row in observable.iterrows():
        if row['TNS'] in FIXED_EXPTIME_S:
            dur_s = FIXED_EXPTIME_S[row['TNS']]
            red, blue = f'1 x {dur_s}', 'n/a (fixed exptime, no Kast heuristic)'
        else:
            red, blue, dur_s = estimate_exposure(row['mag_r'])
        dur_min = dur_s / 60.0

        start = max(current_time, row['entry_pst'])
        end = start + timedelta(minutes=dur_min)

        if start >= row['exit_pst'] or start >= end_time:
            schedule.append(dict(row, scheduled=False,
                                  skip_reason=f"window already closed by the "
                                              f"time this target would be "
                                              f"reached (start {start:%H:%M})"))
            continue
        if end > row['exit_pst']:
            schedule.append(dict(row, scheduled=False,
                                  skip_reason=f"needs {dur_min:.0f} min but "
                                              f"only {(row['exit_pst'] - start).total_seconds() / 60:.0f} "
                                              f"min left in its HA window"))
            continue
        if end > end_time:
            schedule.append(dict(row, scheduled=False,
                                  skip_reason='would run past morning twilight'))
            continue

        schedule.append(dict(row, scheduled=True, start_pst=start, end_pst=end,
                              duration_min=dur_min, red_side=red, blue_side=blue,
                              skip_reason=''))
        current_time = end + timedelta(minutes=SLEW_MINUTES)

    return pd.DataFrame(schedule), current_time


def main():
    twilight = find_twilight(DATE)
    frb_sched = pd.read_csv(f'{OUT_DIR}/night2_frb_repeat_schedule.csv')
    # Re-attach the real America/Los_Angeles zone (not just its numeric
    # UTC offset) after the CSV round-trip -- pd.to_datetime on a
    # CSV-stored "...-07:00" string produces a generic fixed-offset
    # tzinfo whose .tzname() prints "UTC-07:00", not "PDT"; tz_convert
    # re-attaches the named zone (same real instant) so anything derived
    # from these columns (the idle-gap cursor below, and the printed
    # schedule) displays "PDT"/"PST" consistently with times computed
    # fresh from find_twilight() elsewhere in this script.
    frb_sched['start_pst'] = pd.to_datetime(
        frb_sched['start_pst'], format='mixed').dt.tz_convert('America/Los_Angeles')
    frb_sched['end_pst'] = pd.to_datetime(
        frb_sched['end_pst'], format='mixed').dt.tz_convert('America/Los_Angeles')

    spares = load_updated_spare_targets()
    spare_analysis = analyze(spares, twilight)

    print("=== SPARE/FILLER (revised): HA-WINDOW ANALYSIS ===")
    disp = spare_analysis.copy()
    disp['entry_pst'] = disp['entry_pst'].apply(lambda t: t.strftime('%H:%M') if pd.notna(t) else '-')
    disp['exit_pst'] = disp['exit_pst'].apply(lambda t: t.strftime('%H:%M') if pd.notna(t) else '-')
    print(disp[['TNS', 'RA_hours', 'Dec_deg', 'mag_r', 'observable',
                'entry_pst', 'exit_pst', 'ha_entry', 'ha_exit', 'window_min']]
          .to_string(index=False))

    # Idle gaps strictly between/after the (unchanged) FRB-repeat blocks.
    frb_scheduled_sorted = (frb_sched[frb_sched['scheduled']]
                             .sort_values('start_pst').reset_index(drop=True))
    gaps = []
    cursor = twilight['evening_pst']
    for _, row in frb_scheduled_sorted.iterrows():
        if (row['start_pst'] - cursor).total_seconds() > 0:
            gaps.append((cursor, row['start_pst']))
        cursor = row['end_pst'] + timedelta(minutes=SLEW_MINUTES)
    if (twilight['morning_pst'] - cursor).total_seconds() > 0:
        gaps.append((cursor, twilight['morning_pst']))

    spare_schedule_rows = []
    spare_pool = spare_analysis[
        spare_analysis['observable'] & (spare_analysis['TNS'] != FORCE_LAST_TNS)
    ].copy()
    for gap_start, gap_end in gaps:
        if spare_pool.empty:
            break
        sched, _ = schedule_greedy_fixed(spare_pool, gap_start, gap_end)
        placed = sched[sched['scheduled']] if len(sched) else sched
        if len(placed):
            spare_schedule_rows.append(placed)
            spare_pool = spare_pool[~spare_pool['TNS'].isin(placed['TNS'])]

    # --- Force 2026sqf at the very end of the night (author's explicit
    # 2026-09-15 override) -- see never_legal_diagnostic() output below for
    # the real numbers on why this is a bonus post-twilight/post-sunrise
    # attempt, not part of the dark-night schedule proper. ---
    sqf_row = spare_analysis[spare_analysis['TNS'] == FORCE_LAST_TNS].iloc[0]
    entry_time, exit_time, sunset, sunrise = never_legal_diagnostic(
        FORCE_LAST_TNS, sqf_row['RA_hours'], twilight)
    red, blue, dur_s = estimate_exposure(sqf_row['mag_r'])
    dur_min = dur_s / 60.0
    forced_start = entry_time  # earliest clock time the mount can legally point there
    forced_end = forced_start + timedelta(minutes=dur_min)
    reason = (f"FORCED LAST per author's explicit override (2026-09-15): Shane HA "
              f"window (-5.0h..+3.75h) only opens {forced_start:%H:%M} {forced_start.tzname()} -- "
              f"{(forced_start - sunset).total_seconds() / 3600:.1f} h after sunset "
              f"({sunset:%H:%M}), {(forced_start - twilight['morning_pst']).total_seconds() / 60:.0f} "
              f"min after the formal 18-deg morning twilight ({twilight['morning_pst']:%H:%M}), and "
              f"{(forced_start - sunrise).total_seconds() / 60:.0f} min after actual sunrise "
              f"({sunrise:%H:%M}). This is a full-daylight dawn attempt, not a dark-night "
              f"or twilight exposure -- flagged, not silently folded into the schedule.")
    print(f"\n=== FORCED LAST: {FORCE_LAST_TNS} ===\n{reason}")

    sqf_scheduled = pd.DataFrame([dict(
        sqf_row, observable=True, scheduled=True, start_pst=forced_start,
        end_pst=forced_end, duration_min=dur_min, red_side=red, blue_side=blue,
        skip_reason=reason)])
    spare_schedule_rows.append(sqf_scheduled)

    spare_sched = (pd.concat(spare_schedule_rows, ignore_index=True)
                   if spare_schedule_rows else pd.DataFrame())

    print("\n=== SCHEDULE: spare/filler targets (revised) ===")
    for _, row in spare_sched.sort_values('start_pst').iterrows():
        print(f"  {row['start_pst']:%m-%d %H:%M}-{row['end_pst']:%H:%M} {row['end_pst'].tzname()}  "
              f"{row['TNS']:16s} RA {row['RA_hours']:.3f}h Dec {row['Dec_deg']:.3f}  "
              f"red {row['red_side']} blue {row['blue_side']}"
              + (f"  [{row['skip_reason']}]" if row['skip_reason'] else ''))

    spare_analysis.to_csv(f'{OUT_DIR}/night2_spare_analysis.csv', index=False)
    spare_sched.to_csv(f'{OUT_DIR}/night2_spare_schedule.csv', index=False)
    print(f"\nWrote night2_spare_analysis.csv, night2_spare_schedule.csv to {OUT_DIR}")

    return spare_analysis, spare_sched, twilight


if __name__ == '__main__':
    main()
