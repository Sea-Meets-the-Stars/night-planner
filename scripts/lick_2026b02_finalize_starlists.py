"""
Finalize the Lick-2026B-02 starlists from chime_ffff_pz_starlist output.

Created by JXP and Claude

chime_ffff_pz_starlist globs *finder.json in the current directory, so the
main (5 scheduled science targets) and extras (3 gap-fill targets) groups
were staged into separate directories and run separately (see
claude_prompts/night_plans/lick_2026sep14.md, Prompt 6) to keep them on
separate starlists, matching every other main/extras separation this run
(Excel sheets, markdown tables). This script just appends the standard
star (not an FRB, so it has no *finder.json/FFFF-PZ entry) to the main
list and copies both staged outputs to their final names.
"""

import shutil

OUT_DIR = '/home/lordrick/Projects/night-planner/Night_plans/Lick-2026B-02'
STAGING_MAIN = f'{OUT_DIR}/.starlist_main/lick.starlist'
STAGING_EXTRAS = f'{OUT_DIR}/.starlist_extras/lick.starlist'

# chime_ffff_pz_starlist globs *finder.json (filesystem order, not
# observing order) -- reorder each group's 3-line blocks (primary/_S/_C)
# to match the actual schedule sequence.
MAIN_ORDER = ['FRB20260627D', 'FRB20260623C', 'FRB20260507D',
              'FRB20230805A', 'FRB20260418B']
EXTRAS_ORDER = ['FRB20230905A', 'FRB20231111A', 'FRB20250524A']

# Feige_110, same format convention as the tool's own rows (name padded to
# 16 chars, HH MM SS.ss DD MM SS.s epoch) -- see build_lick_2026b02_night_plan.py's
# STD_STAR dict for the source coordinates.
STD_STAR_ROW = 'Feige_110        23 19 58.40 -05 09 56.0 2000.0'


def reorder(path, tns_order):
    with open(path) as f:
        lines = [l for l in f.read().splitlines() if l.strip()]
    by_tns = {}
    for line in lines:
        by_tns.setdefault(line.split()[0].split('_')[0], []).append(line)
    ordered = []
    for tns in tns_order:
        ordered.extend(by_tns.pop(tns))
    for leftover in by_tns.values():  # anything unrecognized, keep at the end
        ordered.extend(leftover)
    return ordered


def main():
    main_rows = reorder(STAGING_MAIN, MAIN_ORDER)
    extras_rows = reorder(STAGING_EXTRAS, EXTRAS_ORDER)

    with open(f'{OUT_DIR}/lick.starlist', 'w') as f:
        f.write('\n'.join(main_rows) + '\n' + STD_STAR_ROW + '\n')
    with open(f'{OUT_DIR}/lick_extras.starlist', 'w') as f:
        f.write('\n'.join(extras_rows) + '\n')

    print(f'Wrote: {OUT_DIR}/lick.starlist')
    print(f'Wrote: {OUT_DIR}/lick_extras.starlist')


if __name__ == '__main__':
    main()
