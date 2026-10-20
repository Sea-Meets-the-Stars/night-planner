"""
Final Keck starlist + target list for Keck/LRIS 2026-10-06 (Keck-2026B-02).

Created by JXP and Claude

Inputs
------
- chime-ffff-pz/.../Observing/Keck-2026B-02/keck.starlist, written by
  `chime_ffff_pz_starlist keck` from the `chime_ffff_pz_finder` JSONs
  (primary + offset-star rows with raoffset/decoffset and rotdest).
- Night_plans/Keck-2026B-02/selected_targets.csv (the schedule).

Outputs (Night_plans/Keck-2026B-02/)
-------
- Keck-2026B-02.starlist: the chime_ffff_pz rows, reordered into schedule
  order, positive Decs given an explicit '+', each row annotated with its
  scheduled time/mode, with the two flux standards added (BD+28 4211, Feige
  110; not in FFFF-PZ, so written here with a correctly signed southern Dec
  -- chime_ffff_pz.scripts.starlist double-signs negative Dec minutes/secs).
- Keck-2026B-02_target_list.md: one row per target in observing order.
- finders/: copies of the chime_ffff_pz_finder PNGs.
"""

import json
import os
import shutil

import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord

import sys
from pathlib import Path

# Repo-relative, so this runs wherever the checkout lives.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from night_planner.paths import ffffpz_data, plans_dir

_PLANS = plans_dir()

OBS_DIR = str(ffffpz_data('Observing', 'Keck-2026B-02'))
RUN_DIR = f'{_PLANS}/Keck-2026B-02'
STARLIST_OUT = f'{RUN_DIR}/Keck-2026B-02.starlist'
TARGETLIST_OUT = f'{RUN_DIR}/Keck-2026B-02_target_list.md'

# Flux standards (name, RA, Dec, comment), written in Keck starlist format
STANDARDS_EVENING = [('BD28d4211', '21 51 11.02', '+28 51 50.4',
                      'vmag=10.5 # Evening flux standard 19:10 HST')]
STANDARDS_MORNING = [('Feige110', '23 19 58.40', '-05 09 56.2',
                      'vmag=11.8 # Morning flux standard')]


def sign_dec(row):
    """
    Give a positive Dec in a chime_ffff_pz Keck starlist row an explicit '+'.

    Parameters
    ----------
    row : str, e.g. 'FRB..  18 33 56.81 46 51 41.4 2000.0 ...'

    Returns
    -------
    str
    """
    parts = row.split()
    # name, hh, mm, ss, dd, mm, ss, epoch, ...
    if not parts[4].startswith(('+', '-')):
        parts[4] = '+' + parts[4]
    return f"{parts[0]:<16}" + ' '.join(parts[1:])


def load_rows():
    """
    Parse keck.starlist into {TNS: [primary_row, offset_row]}.

    Returns
    -------
    dict
    """
    rows = {}
    with open(f'{OBS_DIR}/keck.starlist') as f:
        for line in f:
            if not line.strip():
                continue
            name = line.split()[0]
            tns = name[:-2] if name.endswith('_S') else name
            rows.setdefault(tns, []).append(sign_dec(line.strip()))
    return rows


def primary_row_from_coords(tns, ra_deg, dec_deg):
    """
    Build a Keck-format starlist row for a target with no finder JSON.

    Used for targets added to the schedule after the finder run (e.g. a
    forced truncated exposure). Carries coordinates only -- no offset star
    and no rotdest, because inventing either would be worse than their
    absence being obvious at the telescope.

    Parameters
    ----------
    tns : str
    ra_deg, dec_deg : float

    Returns
    -------
    str
    """
    coord = SkyCoord(ra=ra_deg * u.deg, dec=dec_deg * u.deg, frame='icrs')
    ra = coord.ra.to_string(unit=u.hour, sep=' ', precision=2, pad=True)
    dec = coord.dec.to_string(sep=' ', precision=1, alwayssign=True, pad=True)
    return f'{tns:<16}{ra} {dec} 2000.0'


def main():
    """Write the ordered starlist, the target list and copy the finders."""
    sched = pd.read_csv(RUN_DIR + '/selected_targets.csv')
    for c in ('scheduled_start', 'science_start', 'scheduled_end'):
        sched[c] = pd.to_datetime(sched[c])
    sched = sched.sort_values('scheduled_start')
    rows = load_rows()

    missing = sorted(set(sched['TNS']) - set(rows))
    if missing:
        print(f'WARNING: no chime_ffff_pz_finder output for {", ".join(missing)} '
              f'-- writing coordinates-only rows (no offset star, no PA). '
              f'Run chime_ffff_pz_finder against the Resource\'s own FFFF-PZ '
              f'server to fill these in.')

    out = ['# Keck/LRIS starlist, 2026-10-06 HST (Keck-2026B-02)',
           '# Created by JXP and Claude: chime_ffff_pz_finder/starlist rows, '
           'schedule order',
           '# _S rows = offset star; raoffset/decoffset = star -> target (arcsec)',
           '']
    for name, ra, dec, com in STANDARDS_EVENING:
        out.append(f'{name:<16}{ra} {dec} 2000.0 {com}')
    out.append('')

    md = ['# Keck/LRIS 2026-10-06 — target list (Keck-2026B-02)', '',
          'Created by JXP and Claude, from `chime_ffff_pz_finder` JSONs and the '
          'night plan.', '',
          '| # | Science (HST) | TNS | RA | Dec | mag | Mode | Exposure | PA (deg) '
          '| Offset star | Offset RA/Dec (") | Finder |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|']
    os.makedirs(f'{RUN_DIR}/finders', exist_ok=True)

    for i, (_, t) in enumerate(sched.iterrows(), start=1):
        tns = t['TNS']
        mode = t['lris_mode']
        if mode == 'MOS (mask required)':
            note = 'MOS mask; rotdest = longslit default, use mask PA'
        elif str(mode).startswith('longslit (forced'):
            note = 'longslit, NO MASK, low S/N'
        else:
            note = 'longslit'
        when = (f"{t['science_start']:%H:%M}-{t['scheduled_end']:%H:%M} HST, "
                f"{t['red_exp']}")
        if str(t.get('info', '')).startswith('FORCED'):
            note += ' | FORCED truncated exposure'

        if tns in rows:
            prim, off = rows[tns][0], rows[tns][1]
            out.append(f'{prim} # {when} | {note}')
            out.append(off)

            with open(f'{OBS_DIR}/{tns}_finder.json') as f:
                fj = json.load(f)
            shutil.copy(f'{OBS_DIR}/{tns}_finder.png', f'{RUN_DIR}/finders/')
            ra = ' '.join(prim.split()[1:4])
            dec = ' '.join(prim.split()[4:7])
            pa = f"{fj.get('slit_pa', float('nan')):.1f}"
            star = (f"{fj['offset_star_offset']:.1f}\" away | "
                    f"{fj['offset_ra']:+.2f} / {fj['offset_dec']:+.2f}")
            finder = f'[png](finders/{tns}_finder.png)'
        else:
            prim = primary_row_from_coords(tns, t['RA_deg'], t['Dec_deg'])
            out.append(f'{prim} # {when} | {note} | NO FINDER: no offset star/PA')
            ra = ' '.join(prim.split()[1:4])
            dec = ' '.join(prim.split()[4:7])
            pa, star, finder = '—', '— | —', '—'

        md.append(f"| {i} | {t['science_start']:%H:%M}-{t['scheduled_end']:%H:%M} "
                  f"| {tns} | {ra} | {dec} | {t['mag_r']:.2f} | {note} | "
                  f"{t['red_exp']} | {pa} | {star} | {finder} |")

    out.append('')
    for name, ra, dec, com in STANDARDS_MORNING:
        out.append(f'{name:<16}{ra} {dec} 2000.0 {com}')

    with open(STARLIST_OUT, 'w') as f:
        f.write('\n'.join(out) + '\n')
    md += ['', 'Standards: BD+28 4211 (evening, 19:10 HST) and Feige 110 '
           '(morning, after the last target).', '',
           'Offsets are from the offset star to the target, as in the '
           'starlist `_S` rows.']
    with open(TARGETLIST_OUT, 'w') as f:
        f.write('\n'.join(md) + '\n')
    print(f'Wrote {STARLIST_OUT}\nWrote {TARGETLIST_OUT}\n'
          f'Copied {len(sched)} finders to {RUN_DIR}/finders/')


if __name__ == '__main__':
    main()
