"""
Per-instrument adapters: translate what each instrument's scheduler
actually returns into the one normalized PlanResult shape.

These live here rather than inside the instrument scripts on purpose. The
scripts are per-run one-offs (`keck_2026oct06_*`, `lick_2026b02_night2_*`)
that get copied for the next night; the translation is stable and
shouldn't be copy-pasted along with them. Keyed by instrument, a central
adapter keeps working when next month's script is a copy with the same
function names.

Created by JXP and Claude
"""

import pandas as pd
from astropy import units as u
from astropy.coordinates import EarthLocation
from zoneinfo import ZoneInfo

from .plan_result import PlanResult, ScheduledTarget, TargetDecision
from .sun_events import find_sun_events

# Site constants, matching what each instrument script already uses.
# Verified against astropy's EarthLocation.of_site() (IRAF Observatory
# Database); see keck_2026oct06_calculations.py / lick_2026b02_calculations.py.
# Morning flux standard (Feige 110), for the closing-slew estimate.
MORNING_STANDARD_DEC = -5.1656

SITES = {
    'lris': {
        'telescope': 'Keck I',
        'location': EarthLocation(lat=19.828333 * u.deg, lon=-155.478333 * u.deg,
                                   height=4160 * u.m),
        'tz': ZoneInfo('Pacific/Honolulu'),
    },
    'kast': {
        'telescope': 'Shane 3m (Lick)',
        'location': EarthLocation(lat=37.3414 * u.deg, lon=-121.6429 * u.deg,
                                   height=1283 * u.m),
        'tz': ZoneInfo('America/Los_Angeles'),
    },
}


def _f(value, default=None):
    """float() that passes NaN/None through as `default`."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _dt(value):
    """Coerce a pandas/py datetime to a plain tz-aware datetime, or None."""
    if value is None or (not isinstance(value, str) and pd.isna(value)):
        return None
    if isinstance(value, str):
        value = pd.to_datetime(value)
    return value.to_pydatetime() if hasattr(value, 'to_pydatetime') else value


def keck_lris(out):
    """
    Build a PlanResult from scripts/keck_2026oct06_calculations.run()'s output.

    Parameters
    ----------
    out : dict
        As returned by that module's run().

    Returns
    -------
    PlanResult
    """
    site = SITES['lris']
    results_df = out['results_df']
    selected = out['selected']
    skips = out['skips']

    schedule = []
    for _, r in selected.iterrows():
        schedule.append(ScheduledTarget(
            name=r['TNS'],
            ra_deg=_f(r['RA_deg']),
            dec_deg=_f(r['Dec_deg']),
            mag=_f(r['mag_r']),
            mode=r['lris_mode'],
            start=_dt(r['scheduled_start']),
            science_start=_dt(r['science_start']),
            end=_dt(r['scheduled_end']),
            slew_min=_f(r['slew_min'], 0.0),
            on_target_min=_f(r['on_target_min'], 0.0),
            exposure_red=str(r.get('red_exp', '')),
            exposure_blue=str(r.get('blue_exp', '')),
            airmass=_f(r.get('min_airmass')),
            window_start=_dt(r.get('window_start')),
            window_end=_dt(r.get('window_end')),
            notes=str(r.get('info') or ''),
        ))

    decisions = _keck_decisions(out, results_df, selected, skips)
    overheads = _keck_overheads(out['start_local'], schedule)

    night_end = out['twilight']['morning_hst']
    return PlanResult(
        instrument='lris',
        telescope=site['telescope'],
        date=out['date'],
        output_dir=out['output_dir'],
        timezone=str(site['tz']),
        sun=find_sun_events(out['date'], site['location'], site['tz']),
        night_start=out['start_local'],
        night_end=night_end,
        schedule=schedule,
        decisions=decisions,
        blocks=list(out['blocks']),
        overheads=overheads,
    )


def _keck_overheads(night_start, schedule):
    """
    The non-science blocks the Keck sequence always runs.

    Mirrors print_night_plan()/build_keck_night_plan(): evening standard
    and focus before the first target, then a slew to the morning
    standard, the standard itself, arcs and flats after the last one.
    Emitting them explicitly keeps 'idle' meaning time that could have
    held another target, instead of silently counting planned work.
    """
    from datetime import timedelta
    from keck_overheads import keck_slew_minutes

    out, cursor = [], night_start
    for label, minutes in (('Evening standard (BD+28 4211)', 5),
                            ('Focus check', 5)):
        out.append((cursor, cursor + timedelta(minutes=minutes), label))
        cursor += timedelta(minutes=minutes)

    if not schedule:
        return out

    cursor = max(t.end for t in schedule)
    last_dec = sorted(schedule, key=lambda t: t.end)[-1].dec_deg
    closing = (('Slew to Feige 110', keck_slew_minutes(last_dec, MORNING_STANDARD_DEC)),
               ('Morning standard (Feige 110)', 5),
               ('Arc lamps', 10),
               ('Internal flats', 10))
    for label, minutes in closing:
        out.append((cursor, cursor + timedelta(minutes=minutes), label))
        cursor += timedelta(minutes=minutes)
    return out


def _keck_decisions(out, results_df, selected, skips):
    """
    One TargetDecision per target in the original pulled table.

    Mirrors the staging in scripts/keck_2026oct06_rejection_analysis.py:
    1. Keck selection -> 2. Sky -> 2b. Mask -> 3. Scheduling.
    """
    # Imported lazily: the instrument module is on sys.path only once
    # night_planner.cli has added scripts/ (see _load_module there).
    from keck_2026oct06_calculations import KECK_MAG_FAINT_LIMIT, LICK_DEC_LIMIT

    from .targets_io import load_targets

    pulled = load_targets(out['targets_csv'])
    res = results_df.set_index('TNS')
    sel = selected.set_index('TNS') if len(selected) else pd.DataFrame()

    window = (None, None)
    decisions = []
    for _, p in pulled.iterrows():
        tns, mag, dec = p['name'], _f(p['mag']), _f(p['dec_deg'])
        ra = _f(p['ra_deg'])

        if tns not in res.index:
            status, stage = 'rejected', '1. Keck selection'
            reason = (f"mag {mag:.2f} <= {KECK_MAG_FAINT_LIMIT} and Dec "
                      f"{dec:+.1f} <= {LICK_DEC_LIMIT} (Lick can take it)")
        elif str(res.loc[tns, 'limit_reason']).startswith('No mask'):
            status, stage = 'rejected', '2b. Mask'
            reason = res.loc[tns, 'limit_reason']
        elif not res.loc[tns, 'observable']:
            r = res.loc[tns]
            status, stage = 'rejected', '2. Sky'
            reason = (f"{r['limit_reason']} (min AM {r['min_airmass']:.2f}, "
                      f"{r['observable_hours']:.2f} h at AM<2.0; need >0.5 h)")
        elif len(sel) and tns in sel.index:
            s = sel.loc[tns]
            status, stage = 'scheduled', '3. Scheduling'
            reason = (f"slew {_dt(s['scheduled_start']):%H:%M} "
                      f"({int(s['slew_min'])} min), on target "
                      f"{_dt(s['science_start']):%H:%M}-{_dt(s['scheduled_end']):%H:%M} "
                      f"({s['on_target_min']:g} min, {s['lris_mode']})")
        else:
            status, stage = 'rejected', '3. Scheduling'
            skip = skips.get(tns)
            if isinstance(skip, dict):
                reason = skip['reason']
                window = (skip.get('window_start'), skip.get('window_end'))
            else:
                reason = skip or 'not reached (max_targets hit)'
                window = (None, None)

        decisions.append(TargetDecision(
            name=tns, ra_deg=ra, dec_deg=dec, mag=mag,
            status=status, stage=stage, reason=reason,
            window_start=_dt(window[0]), window_end=_dt(window[1])))

    # A forced target the scheduler could not place must not vanish --
    # the caller asked for it by name.
    for failure in out.get('forced_failures') or []:
        decisions = [d for d in decisions if d.name != failure['TNS']]
        row = res.loc[failure['TNS']] if failure['TNS'] in res.index else None
        decisions.append(TargetDecision(
            name=failure['TNS'],
            ra_deg=_f(row['RA_deg']) if row is not None else None,
            dec_deg=_f(row['Dec_deg']) if row is not None else None,
            mag=_f(row['mag_r']) if row is not None else None,
            status='rejected', stage='4. Forced',
            reason=f"forced but not placed -- {failure['reason']}"))
    return decisions


def _attribute_kast_slews(schedule, night_start):
    """
    Charge the inter-target gap to the slew that actually fills it.

    The Kast scheduler advances its cursor by SLEW_MINUTES after each
    target rather than emitting a slew row, so without this every slew
    would surface as idle time in the viewer. Walk the sorted schedule
    and, where the preceding target ends exactly one slew earlier, extend
    this target's start back over that gap and record it as slew.
    """
    from lick_2026b02_night2_calculations import SLEW_MINUTES

    slew = pd.Timedelta(minutes=SLEW_MINUTES)
    prev_end = night_start
    for target in schedule:
        slew_start = target.science_start - slew
        if slew_start >= prev_end:
            target.start = slew_start
            target.slew_min = float(SLEW_MINUTES)
        prev_end = target.end


def lick_kast(out):
    """
    Build a PlanResult from
    scripts/lick_2026b02_night2_calculations.run()'s output.

    That scheduler already carries its own per-row `skip_reason` and a
    `scheduled` flag, so decisions come straight off the two schedule
    frames (FRB repeats + spare/filler) rather than being reconstructed.
    """
    site = SITES['kast']

    frames = [f for f in (out['frb_sched'], out['spare_sched']) if len(f)]
    sched_df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    schedule, decisions = [], []
    for _, r in sched_df.iterrows():
        name = r['TNS']
        ra_deg = _f(r.get('RA_hours'))
        ra_deg = ra_deg * 15.0 if ra_deg is not None else None
        dec_deg, mag = _f(r.get('Dec_deg')), _f(r.get('mag_r'))

        if r.get('scheduled'):
            start, end = _dt(r['start_pst']), _dt(r['end_pst'])
            schedule.append(ScheduledTarget(
                name=name, ra_deg=ra_deg, dec_deg=dec_deg, mag=mag,
                mode='longslit',
                start=start, science_start=start, end=end,
                slew_min=0.0,  # Kast scheduler models slew as a gap, not a block
                on_target_min=_f(r.get('duration_min'), 0.0),
                exposure_red=str(r.get('red_side', '')),
                exposure_blue=str(r.get('blue_side', '')),
                window_start=_dt(r.get('entry_pst')),
                window_end=_dt(r.get('exit_pst')),
                notes=str(r.get('skip_reason') or ''),
            ))
            decisions.append(TargetDecision(
                name=name, ra_deg=ra_deg, dec_deg=dec_deg, mag=mag,
                status='scheduled', stage='3. Scheduling',
                reason=(f"{start:%H:%M}-{end:%H:%M} "
                        f"({_f(r.get('duration_min'), 0):.0f} min)")))
        else:
            decisions.append(TargetDecision(
                name=name, ra_deg=ra_deg, dec_deg=dec_deg, mag=mag,
                status='rejected', stage='3. Scheduling',
                reason=str(r.get('skip_reason') or 'not scheduled')))

    # Targets that never reached the scheduler: no HA-legal window tonight.
    scheduled_or_skipped = {d.name for d in decisions}
    for frame in (out['repeat_analysis'], out['spare_analysis']):
        for _, r in frame.iterrows():
            if r['TNS'] in scheduled_or_skipped or r.get('observable'):
                continue
            ra_deg = _f(r.get('RA_hours'))
            decisions.append(TargetDecision(
                name=r['TNS'],
                ra_deg=ra_deg * 15.0 if ra_deg is not None else None,
                dec_deg=_f(r.get('Dec_deg')), mag=_f(r.get('mag_r')),
                status='rejected', stage='2. Sky',
                reason='never HA-legal tonight (Shane mount limit)'))

    schedule.sort(key=lambda t: t.start)
    _attribute_kast_slews(schedule, out['start_local'])

    return PlanResult(
        instrument='kast',
        telescope=site['telescope'],
        date=out['date'],
        output_dir=out['output_dir'],
        timezone=str(site['tz']),
        sun=find_sun_events(out['date'], site['location'], site['tz']),
        night_start=out['start_local'],
        night_end=out['night_end'],
        schedule=schedule,
        decisions=decisions,
        blocks=list(out['blocks']),
    )


ADAPTERS = {
    'lris': keck_lris,
    'kast': lick_kast,
}
