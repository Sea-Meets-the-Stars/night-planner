"""
Search for filler targets (mag > 18) to reduce idle time in the Keck/LRIS
2026-10-06 plan (Keck-2026B-02).

Created by JXP and Claude

The main Keck selection rule keeps only mag > 19 (Lick covers brighter). Per
the author (2026-09-30), mag 18-19 targets are acceptable as *fillers* for
otherwise idle time. This script:

  1. Collects every target from all local FFFF-PZ pulls
     (chime-ffff-pz/.../Observing/*/*_targets.csv), keeping the most
     recent row per TNS and only mag > 18. These pulls were made for other
     runs, so a target's status may have changed since (e.g. already
     observed) -- a fresh FFFF-PZ pull is needed to confirm.
  2. Drops targets already in the Keck-2026B-02 pool (already evaluated)
     and mag > 21 targets without a mask (MOS_MASKS_AVAILABLE).
  3. Runs the same Oct 6 sky checks (AM < 2.0 window, Keck limits, Keck I
     Nasmyth deck) via keck_2026oct06_calculations.
  4. Finds the idle slots in the current schedule (gaps between blocks, and
     the end of the night up to dawn minus the morning standard) and, for
     each candidate whose window overlaps a slot, checks whether
     slew-in + ETC exposure + slew to the next block fits.

Inputs : Night_plans/Keck-2026B-02/selected_targets.csv, local FFFF-PZ pulls
Outputs: Night_plans/Keck-2026B-02/filler_candidates.csv, printed summary
"""

import glob
import io
import json
import os
from contextlib import redirect_stdout
from datetime import timedelta

import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

import keck_2026oct06_calculations as kc
from keck_overheads import keck_slew_minutes, KECK_SLEW_BASE_MIN

OBS_DIR = '/home/lordrick/Projects/chime-ffff-pz/chime_ffff_pz/data/Observing'
RUN_DIR = '/home/lordrick/Projects/night-planner/Night_plans/Keck-2026B-02'
DATE = '2026-10-06'
FILLER_MAG_MIN = 18.0
MIN_SLOT_MIN = 20          # ignore idle slots shorter than this
MORNING_STD_MIN = 5        # Feige 110 exposure; slew to it added separately
OUTFILE = f'{RUN_DIR}/filler_candidates.csv'
# Lick-excluded high-Dec targets the author asked to check (2026-09-30),
# kept regardless of mag. Above Dec ~84 they never reach AM < 2.0 from Keck
# (lat 19.8), so they are tracked across the whole night and only packed if
# they meet MAX_AM -- per the author, never force a target above AM 2.
HIGH_DEC_EXTRA = ['FRB20260510A', 'FRB20251003A']
MAX_AM = 2.0
# Local pulls can be stale: only pack targets whose *current* FFFF-PZ status
# (read-only chk_frb query, server from FFFF_PZ_URL) still needs a spectrum.
PACKABLE_STATUSES = {'NeedSpectrum'}


def collect_local_pulls():
    """
    Merge all local FFFF-PZ target CSVs, newest row per TNS, mag > 18.

    Returns
    -------
    DataFrame with FFFF-PZ target columns plus 'source_pull'
    """
    frames = []
    for f in glob.glob(f'{OBS_DIR}/*/*_targets.csv'):
        df = pd.read_csv(f)
        df['source_pull'] = os.path.basename(os.path.dirname(f))
        df['_mtime'] = os.path.getmtime(f)
        frames.append(df)
    allt = pd.concat(frames, ignore_index=True)
    allt = allt.sort_values('_mtime').drop_duplicates('TNS', keep='last')
    keep = (allt['Pri_mag'] > FILLER_MAG_MIN) | allt['TNS'].isin(HIGH_DEC_EXTRA)
    return allt[keep].drop(columns='_mtime')


def ffff_pz_status(tns):
    """
    Current FFFF-PZ status of an FRB via the read-only chk_frb endpoint.

    Parameters
    ----------
    tns : str

    Returns
    -------
    str status, or 'query failed (<code>)'
    """
    r = requests.put(url=os.getenv('FFFF_PZ_URL') + 'chk_frb/',
                     data=json.dumps({'name': tns}),
                     auth=HTTPBasicAuth(os.getenv('FFFF_PZ_USER'),
                                        os.getenv('FFFF_PZ_PASS')),
                     timeout=60)
    if r.status_code != 201:
        return f'query failed ({r.status_code})'
    return json.loads(r.content)['status']


def idle_slots(selected, twilight):
    """
    Idle slots in the current schedule.

    Returns
    -------
    list of dict with 'start', 'prev_dec', 'next_science_start' (None at end
    of night), 'next_dec', 'limit' (latest science end), 'minutes'
    """
    sel = selected.sort_values('scheduled_start').reset_index(drop=True)
    for c in ('scheduled_start', 'scheduled_end', 'science_start'):
        sel[c] = pd.to_datetime(sel[c])
    slots = []
    for i in range(len(sel) - 1):
        a, b = sel.iloc[i], sel.iloc[i + 1]
        gap = (b['science_start'] - a['scheduled_end']).total_seconds() / 60
        if gap - b['slew_min'] >= MIN_SLOT_MIN:
            slots.append({'start': a['scheduled_end'], 'prev_dec': a['Dec_deg'],
                          'next_science_start': b['science_start'],
                          'next_dec': b['Dec_deg'], 'limit': b['science_start'],
                          'minutes': gap})
    last = sel.iloc[-1]
    # End of night: science must finish in time to slew to and observe the
    # morning standard before 18 deg dawn (arcs/flats are internal lamps).
    dawn = twilight['morning_hst']
    # Slew to Feige 110 (Dec -5) is never a northward crossing: base slew.
    limit = dawn - timedelta(minutes=KECK_SLEW_BASE_MIN + MORNING_STD_MIN)
    slots.append({'start': last['scheduled_end'], 'prev_dec': last['Dec_deg'],
                  'next_science_start': None, 'next_dec': kc.MORNING_STANDARD_DEC,
                  'limit': limit,
                  'minutes': (limit - last['scheduled_end']).total_seconds() / 60})
    return slots


def high_dec_check(row, slot, twilight):
    """
    Altitude/airmass/Keck-limit track of a high-Dec target across a slot
    (slot=None: the whole 18 deg dark night).

    Parameters
    ----------
    row : Series from analyze_targets() output
    slot : dict from idle_slots(), or None
    twilight : dict from find_twilight()

    Returns
    -------
    dict with 'am_min', 'am_max', 'alt_min', 'alt_max', 'az_range',
    'keck_ok' (all 10-min samples pass check_keck_limits), 'exposure',
    'science_min', 'slew_in'
    """
    t = slot['start'] if slot else twilight['evening_hst']
    t_end = slot['limit'] if slot else twilight['morning_hst']
    ams, alts, azs, ok = [], [], [], True
    while t <= t_end:
        am, alt, az, ha = kc.calculate_airmass(row['RA_deg'], row['Dec_deg'],
                                               t.astimezone(kc.timezone.utc))
        ams.append(am); alts.append(alt); azs.append(az)
        ok = ok and kc.check_keck_limits(row['RA_deg'], row['Dec_deg'], ha, alt, az)[0]
        t += timedelta(minutes=10)
    exp = kc.estimate_lris_exposure(row['mag_r'], airmass=max(ams))
    return {'am_min': min(ams), 'am_max': max(ams), 'alt_min': min(alts),
            'alt_max': max(alts), 'az_range': (min(azs), max(azs)), 'keck_ok': ok,
            'exposure': exp['red_exp'], 'science_min': exp['science_min'],
            'slew_in': (keck_slew_minutes(slot['prev_dec'], row['Dec_deg'])
                        if slot else None)}


def pack_end_slot(cands, slot, required=(), max_n=5):
    """
    Best ordered set of fillers for the end-of-night slot, by exhaustive
    search over orderings (candidate lists here are small). Each target
    starts after the previous one plus its Keck slew, inside its own window,
    and must finish by the slot limit. Objective: maximize on-target
    minutes; ties go to the fainter (more Keck-worthy) set.

    Parameters
    ----------
    cands : list of dict with 'TNS', 'mag_r', 'Dec_deg', 'w0', 'w1'
        (tz-aware window bounds), 'science_min'
    slot : dict from idle_slots() (end-of-night slot)
    required : TNS names that must be in the plan
    max_n : maximum number of fillers

    Returns
    -------
    list of dict with 'TNS', 'mag_r', 'slew_start', 'slew_min',
    'science_start', 'science_end'
    """
    from itertools import permutations
    best, best_key = [], (-1, 0)
    for n in range(1, max_n + 1):
        for seq in permutations(cands, n):
            names = {c['TNS'] for c in seq}
            if not set(required) <= names:
                continue
            plan, now, prev_dec, ok = [], slot['start'], slot['prev_dec'], True
            for c in seq:
                slew = keck_slew_minutes(prev_dec, c['Dec_deg'])
                sci0 = max(now + timedelta(minutes=slew), c['w0'])
                sci1 = sci0 + timedelta(minutes=c['science_min'])
                if sci1 > min(c['w1'] + timedelta(minutes=10), slot['limit']):
                    ok = False
                    break
                plan.append({'TNS': c['TNS'], 'mag_r': c['mag_r'],
                             'slew_start': sci0 - timedelta(minutes=slew),
                             'slew_min': slew, 'science_start': sci0,
                             'science_end': sci1})
                now, prev_dec = sci1, c['Dec_deg']
            if not ok:
                continue
            key = (sum(c['science_min'] for c in seq), sum(c['mag_r'] for c in seq))
            if key > best_key:
                best, best_key = plan, key
    return best


def main():
    """Run the filler search and write filler_candidates.csv."""
    selected = pd.read_csv(f'{RUN_DIR}/selected_targets.csv')
    pool = pd.read_csv(f'{RUN_DIR}/Keck-2026B-02_targets.csv')

    cands = collect_local_pulls()
    n_all = len(cands)
    cands = cands[~cands['TNS'].isin(pool['TNS'])]
    tmp_csv = f'{RUN_DIR}/_filler_input.csv'
    cands.to_csv(tmp_csv, index=False)

    # Same Oct 6 analysis, with the Keck mag cut relaxed to the filler limit
    kc.KECK_MAG_FAINT_LIMIT = FILLER_MAG_MIN
    with redirect_stdout(io.StringIO()):
        res, twilight, _ = kc.analyze_targets(tmp_csv, DATE)
    os.remove(tmp_csv)
    res = res.merge(cands[['TNS', 'source_pull']], on='TNS')

    slots = idle_slots(selected, twilight)
    print(f"Local pulls: {n_all} unique mag>{FILLER_MAG_MIN:.0f} targets; "
          f"{len(cands)} not already in Keck-2026B-02; "
          f"{int(res['observable'].sum())} pass Oct 6 sky/mask checks")
    print("Idle slots (>= {} min):".format(MIN_SLOT_MIN))
    for s in slots:
        print(f"  {s['start']:%H:%M} -> science must end by {s['limit']:%H:%M} "
              f"({s['minutes']:.0f} min)")

    rows = []
    for _, r in res.iterrows():
        out = {'TNS': r['TNS'], 'mag_r': r['mag_r'], 'Dec_deg': round(r['Dec_deg'], 2),
               'RA_hours': round(r['RA_hours'], 2), 'lris_mode': r['lris_mode'],
               'tags': r['tags'], 'source_pull': r['source_pull'],
               'fits': False, 'reason': ''}
        if not r['observable']:
            out['reason'] = r['limit_reason'] or 'not observable'
            rows.append(out)
            continue
        w0, w1, _ = kc.find_observable_window(r['RA_deg'], r['Dec_deg'], twilight, r['mag_r'])
        out.update(window=f"{w0:%H:%M}-{w1:%H:%M}")
        out['ffff_pz_status'] = ffff_pz_status(r['TNS'])
        if out['ffff_pz_status'] not in PACKABLE_STATUSES:
            out['reason'] = f"FFFF-PZ status now {out['ffff_pz_status']} (needs NeedSpectrum)"
            rows.append(out)
            continue
        fit_msgs = []
        for s in slots:
            slew_in = keck_slew_minutes(s['prev_dec'], r['Dec_deg'])
            sci0 = max(s['start'] + timedelta(minutes=slew_in), w0)
            latest_end = min(w1 + timedelta(minutes=10), s['limit'])
            if s['next_science_start'] is not None:
                # leave time to slew on to the next scheduled block
                latest_end = min(latest_end, s['next_science_start'] - timedelta(
                    minutes=keck_slew_minutes(r['Dec_deg'], s['next_dec'])))
            avail = (latest_end - sci0).total_seconds() / 60
            if avail <= 0:
                continue
            exp = kc.estimate_lris_exposure(r['mag_r'], airmass=r['min_airmass'])
            need = exp['science_min']
            msg = (f"slot {s['start']:%H:%M}: slew {slew_in}, needs {need:g} min, "
                   f"{avail:.0f} min available")
            if need <= avail:
                out.update(fits=True, slot=f"{s['start']:%H:%M}", slew_in=slew_in,
                           science_min=need, exposure=exp['red_exp'],
                           science_start=f"{sci0:%H:%M}")
                fit_msgs = [msg]
                break
            fit_msgs.append(msg)
        out['reason'] = '; '.join(fit_msgs) if fit_msgs else 'window does not overlap any idle slot'
        rows.append(out)

    df = pd.DataFrame(rows).sort_values(['fits', 'mag_r'], ascending=[False, True])
    df.to_csv(OUTFILE, index=False)
    print(f"\nFits an idle slot: {int(df['fits'].sum())}")
    cols = [c for c in ('TNS', 'mag_r', 'Dec_deg', 'RA_hours', 'lris_mode', 'ffff_pz_status', 'window',
                        'slot', 'slew_in', 'science_min', 'exposure', 'source_pull')
            if c in df.columns]
    print(df[df['fits']][cols].to_string(index=False))
    near = df[~df['fits'] & df['reason'].str.startswith('slot')]
    if len(near):
        print("\nOverlap an idle slot but too long:")
        print(near[['TNS', 'mag_r', 'window', 'reason']].to_string(index=False))
    end_slot = slots[-1]
    # Candidate list for packing: every filler that fits alone, plus the
    # high-Dec extras if they pass the Keck limits across the slot
    pack = []
    for _, c in df[df['fits']].iterrows():
        r = res[res['TNS'] == c['TNS']].iloc[0]
        w0, w1, _ = kc.find_observable_window(r['RA_deg'], r['Dec_deg'], twilight, r['mag_r'])
        pack.append({'TNS': c['TNS'], 'mag_r': c['mag_r'], 'Dec_deg': r['Dec_deg'],
                     'w0': w0, 'w1': w1, 'science_min': c['science_min']})
    required = []
    for tns in HIGH_DEC_EXTRA:
        hit = res[res['TNS'] == tns]
        if hit.empty:
            continue
        h = high_dec_check(hit.iloc[0], end_slot, twilight)
        if h['keck_ok'] and h['am_max'] <= MAX_AM:
            pack.append({'TNS': tns, 'mag_r': hit.iloc[0]['mag_r'],
                         'Dec_deg': hit.iloc[0]['Dec_deg'], 'w0': end_slot['start'],
                         'w1': end_slot['limit'], 'science_min': h['science_min']})
            required.append(tns)
    plan = pack_end_slot(pack, end_slot, required=required)
    print(f"\nBest packing of the end slot (required: {required or 'none'}):")
    for p_ in plan:
        print(f"  {p_['slew_start']:%H:%M} slew {p_['slew_min']} | "
              f"{p_['science_start']:%H:%M}-{p_['science_end']:%H:%M} "
              f"{p_['TNS']} mag {p_['mag_r']:.2f}")
    if plan:
        print(f"  idle left before morning standard: "
              f"{(end_slot['limit'] - plan[-1]['science_end']).total_seconds()/60:.0f} min")

    for tns in HIGH_DEC_EXTRA:
        hit = res[res['TNS'] == tns]
        if hit.empty:
            print(f"\n{tns}: not in local pulls")
            continue
        n = high_dec_check(hit.iloc[0], None, twilight)
        print(f"\n{tns} whole night: AM {n['am_min']:.2f}-{n['am_max']:.2f}, "
              f"alt {n['alt_min']:.1f}-{n['alt_max']:.1f} deg; "
              f"reaches AM<={MAX_AM}: {n['am_min'] <= MAX_AM}")
        h = high_dec_check(hit.iloc[0], end_slot, twilight)
        print(f"{tns} (Dec {hit.iloc[0]['Dec_deg']:+.2f}, mag {hit.iloc[0]['mag_r']:.2f}) "
              f"over {end_slot['start']:%H:%M}-{end_slot['limit']:%H:%M}: "
              f"AM {h['am_min']:.2f}-{h['am_max']:.2f}, alt {h['alt_min']:.1f}-"
              f"{h['alt_max']:.1f} deg, az {h['az_range'][0]:.1f}-{h['az_range'][1]:.1f} deg, "
              f"Keck limits OK: {h['keck_ok']}, ETC at AM {h['am_max']:.2f}: "
              f"{h['exposure']} ({h['science_min']:g} min) + slew {h['slew_in']}")

    stale = df[df['reason'].str.startswith('FFFF-PZ status')]
    if len(stale):
        print("\nUp on Oct 6 but no longer need a spectrum:")
        print(stale[['TNS', 'mag_r', 'ffff_pz_status']].to_string(index=False))
    print(f"\nWrote {OUTFILE}")


if __name__ == '__main__':
    main()
