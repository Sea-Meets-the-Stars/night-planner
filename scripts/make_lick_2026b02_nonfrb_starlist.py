"""
Created by JXP and Claude

Build the Lick/Shane starlist block (target/_S offset-star/_C slit-center,
3 rows) for each Lick-2026B-02 non-FRB spare/filler target, from the
finder.json files written by lick_2026b02_nonfrb_finders.py.

Deliberately does NOT reuse chime_ffff_pz.scripts.starlist's own
`add_coord_to_row` -- that helper formats Dec minutes/seconds with
`f'{val:02.0f}'` directly on the (possibly negative) `dms` components
without `abs()`, so for a southern-Dec target it emits a doubly-signed
row like `-2 -51 -55.6` instead of `-02 51 55.6` (every prior FRB target
here happened to be Dec-positive, so this never surfaced before 2025pht,
Dec -02:51:55.6). Not this project's upstream repo to patch (matches the
existing "cosmetic issue, noted not fixed" precedent in
claude_prompts/night_plans/lick_2026sep14.md for the unsigned-positive-Dec
issue in the same module) -- reuses instead the already-correct
`starlist_row()` convention from make_lick_2026b02_night2_starlist.py
(`abs()` on Dec arcmin/arcsec, signed zero-padded Dec degrees), applied
per-suffix (target/_S offset-star/_C slit-center) from each non-FRB
target's finder.json.
"""

import json
import os

from astropy.coordinates import SkyCoord

FINDER_DIR = ('/home/lordrick/Projects/chime-ffff-pz/chime_ffff_pz/data/'
              'Observing/Lick-2026B-02')
OUTFILE = ('/home/lordrick/Projects/night-planner/Night_plans/'
           'Lick-2026B-02/lick_nonfrb.starlist')

# Non-FRB spare/filler target names (must match the *_finder.json stems
# written by lick_2026b02_nonfrb_finders.py) -- kept explicit rather than
# globbing all of FINDER_DIR, since that directory also holds the 8 FRB
# finder.json files from 2026-09-14.
NONFRB_NAMES = ['2026yly', '2026sqf', '2026abgb', '2026yum', '2026zyg',
                '2025pht', 'DLA_J0210+1702']


def zpad(val, n):
    bits = val.split('.')
    return '%s.%s' % (bits[0].zfill(n), bits[1])


def build_row(name, suffix, finder):
    """One starlist row for a given target/prefix, Lick format (matches
    starlist_row() in make_lick_2026b02_night2_starlist.py -- correct
    for negative Dec, unlike the upstream chime_ffff_pz helper; see
    module docstring).
    """
    prefix = {'': 'primary', '_S': 'offset_star', '_C': 'slitcen'}[suffix]
    coord = SkyCoord(finder[f'{prefix}_ra'], finder[f'{prefix}_dec'], unit='deg')
    hour = f'{coord.ra.hms[0]:02.0f}'
    ra_min = f'{coord.ra.hms[1]:02.0f}'
    ra_sec = zpad(f'{coord.ra.hms[2]:.2f}', 2)
    deg = f'{coord.dec.dms[0]:+03.0f}'
    dec_min = f'{abs(coord.dec.dms[1]):02.0f}'
    dec_sec = zpad(f'{abs(coord.dec.dms[2]):.1f}', 2)
    return (f'{f"{name}{suffix}".ljust(16)} {hour} {ra_min} {ra_sec} '
            f'{deg} {dec_min} {dec_sec} 2000.0')


def main():
    rows = []
    missing = []
    for name in NONFRB_NAMES:
        jsonfile = os.path.join(FINDER_DIR, f'{name}_finder.json')
        if not os.path.exists(jsonfile):
            missing.append(name)
            continue
        with open(jsonfile) as f:
            finder = json.load(f)
        for suffix in ['', '_S', '_C']:
            rows.append(build_row(name, suffix, finder))

    if missing:
        print(f'WARNING: no finder.json for: {missing} -- run '
              f'lick_2026b02_nonfrb_finders.py first')

    with open(OUTFILE, 'w') as f:
        f.write('\n'.join(rows) + '\n')

    print(f'Wrote: {OUTFILE}')
    for row in rows:
        print(row)


if __name__ == '__main__':
    main()
