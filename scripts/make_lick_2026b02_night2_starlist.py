"""
Build the Lick/Shane starlist for Lick-2026B-02, night 2 (2026-09-15/16).

Created by JXP and Claude

Repeats reuse the exact target/_S (offset star)/_C (slit center) 3-line
blocks already generated for night 1 (lick.starlist, lick_extras.starlist)
via chime_ffff_pz_starlist -- coordinates don't change for a repeat, and
regenerating them would require re-running the finder-chart pipeline for
no benefit. Reordered into tonight's actual schedule
(night2_frb_repeat_schedule.csv). Spare/filler targets now have real
finder charts too (lick_2026b02_nonfrb_finders.py + make_lick_2026b02_
nonfrb_starlist.py, since 2026-09-16), so they get the same 3-line
target/_S/_C blocks as the FRBs, read from lick_nonfrb.starlist, instead
of the single-coordinate-only row this script used before that existed.
"""

import pandas as pd

OUT_DIR = '/home/lordrick/Projects/night-planner/Night_plans/Lick-2026B-02'
NIGHT1_MAIN = f'{OUT_DIR}/lick.starlist'
NIGHT1_EXTRAS = f'{OUT_DIR}/lick_extras.starlist'
NONFRB_BLOCKS = f'{OUT_DIR}/lick_nonfrb.starlist'
FRB_SCHED_CSV = f'{OUT_DIR}/night2_frb_repeat_schedule.csv'
SPARE_SCHED_CSV = f'{OUT_DIR}/night2_spare_schedule.csv'
OUTFILE = f'{OUT_DIR}/lick_night2.starlist'

STD_STAR_ROW = 'Feige_110        23 19 58.40 -05 09 56.0 2000.0'

# Targets whose primary-row starlist entry carries a fixed exptime tag
# (author-given directly, 2026-09-15/16 -- not derived from the Kast
# mag-based heuristic, since no magnitude was supplied for this one).
FIXED_EXPTIME_S = {'DLA_J0210+1702': 3600}


def blocks_by_tns(path):
    """Group a starlist file's lines into 1-3 line blocks keyed by TNS.

    Strips a trailing '_S'/'_C' suffix to find the TNS, rather than
    splitting on the first underscore -- a name can itself contain an
    underscore (e.g. `DLA_J0210+1702`), which would otherwise be sliced
    in half and silently merged under the wrong key.
    """
    with open(path) as f:
        lines = [l for l in f.read().splitlines() if l.strip()]
    by_tns = {}
    for line in lines:
        name = line.split()[0]
        tns = name[:-2] if name.endswith(('_S', '_C')) else name
        by_tns.setdefault(tns, []).append(line)
    return by_tns


def main():
    main_blocks = blocks_by_tns(NIGHT1_MAIN)
    extra_blocks = blocks_by_tns(NIGHT1_EXTRAS)
    nonfrb_blocks = blocks_by_tns(NONFRB_BLOCKS)
    all_blocks = {**main_blocks, **extra_blocks}

    frb_order = (pd.read_csv(FRB_SCHED_CSV)
                 .query('scheduled == True')
                 .sort_values('start_pst')['TNS'].tolist())

    rows = []
    for tns in frb_order:
        if tns not in all_blocks:
            raise ValueError(f'No night-1 starlist block found for repeat target {tns}')
        rows.extend(all_blocks[tns])

    spare_order = (pd.read_csv(SPARE_SCHED_CSV)
                   .query('scheduled == True')
                   .sort_values('start_pst')['TNS'].tolist())
    for tns in spare_order:
        if tns not in nonfrb_blocks:
            raise ValueError(f'No non-FRB starlist block found for spare target {tns} '
                              f'-- run lick_2026b02_nonfrb_finders.py + '
                              f'make_lick_2026b02_nonfrb_starlist.py first')
        block = list(nonfrb_blocks[tns])
        if tns in FIXED_EXPTIME_S:
            block[0] += f'  exptime={FIXED_EXPTIME_S[tns]}'
        rows.extend(block)

    rows.append(STD_STAR_ROW)

    with open(OUTFILE, 'w') as f:
        f.write('\n'.join(rows) + '\n')

    print(f'Wrote: {OUTFILE}')
    for row in rows:
        print(row)


if __name__ == '__main__':
    main()
