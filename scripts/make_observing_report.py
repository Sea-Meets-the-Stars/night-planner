"""
Turn a night plan into an observing report row per target.

Columns match the FFFF-PZ observing log:
    TNS, FRB_Survey, Resource, mode, date, texp, Conditions, success

The plan records what was *scheduled*. Two fields it cannot know are the
conditions and whether each target actually yielded a redshift, so both
are passed in and default conservatively rather than being invented.

    python scripts/make_observing_report.py --plan-dir Night_plans/Keck-2026B-02 \
        --conditions Fair --extra FRB20260708D

Created by JXP and Claude
"""

import argparse
import csv
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))
from night_planner.plan_store import load_plan

COLUMNS = ['TNS', 'FRB_Survey', 'Resource', 'mode', 'date', 'texp',
           'Conditions', 'success']

# The plan's internal mode strings -> the log's vocabulary.
MODE_MAP = {
    'longslit': 'longslit',
    'longslit (forced, no mask)': 'longslit',
    'MOS (mask required)': 'mask',
}


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan-dir', required=True)
    p.add_argument('--conditions', required=True,
                   help='Observing conditions for the night, e.g. Fair.')
    p.add_argument('--resource', help='FFFF-PZ Resource name [plan directory].')
    p.add_argument('--survey', default='CHIME/FRB')
    p.add_argument('--out', help='Output CSV [<plan-dir>/<resource>_report.csv].')
    p.add_argument('--extra', action='append', default=[],
                   help='Target observed but not in the plan, as NAME or '
                        'NAME:texp_seconds. Repeatable.')
    p.add_argument('--drop', action='append', default=[],
                   help='Planned target that was not observed. Repeatable.')
    p.add_argument('--failed', action='append', default=[],
                   help='Target to mark success=False. Repeatable.')
    return p.parse_args(argv)


def exposure_seconds(target):
    """
    On-target integration time in seconds.

    Prefers the real exposure string ("3 x 1060" -> 3180 s) because the
    scheduled block can include overhead the detector never saw: a MOS
    allocation carries a mask-alignment buffer, so using the block length
    would overstate the integration.

    Returns
    -------
    (seconds, note)
    """
    match = re.match(r'\s*(\d+)\s*[xX]\s*(\d+)', str(target.exposure_red or ''))
    if match:
        n_sub, sub_len = int(match.group(1)), int(match.group(2))
        return n_sub * sub_len, ''
    # No parseable exposure (MOS blocks are an allocation, not a recipe).
    return int(round(target.on_target_min * 60)), 'from allocated block'


def build_rows(plan, args):
    """One report row per observed target, in observing order."""
    dropped = set(args.drop)
    failed = set(args.failed)
    resource = args.resource or Path(plan.output_dir).name

    rows, notes = [], []
    for target in plan.schedule:
        if target.name in dropped:
            continue
        texp, note = exposure_seconds(target)
        if note:
            notes.append(f'{target.name}: texp {texp} s {note} '
                         f'({target.mode})')
        rows.append({
            'TNS': target.name,
            'FRB_Survey': args.survey,
            'Resource': resource,
            'mode': MODE_MAP.get(target.mode, target.mode),
            'date': plan.date,
            'texp': texp,
            'Conditions': args.conditions,
            'success': target.name not in failed,
        })

    for spec in args.extra:
        name, _, texp = spec.partition(':')
        rows.append({
            'TNS': name,
            'FRB_Survey': args.survey,
            'Resource': resource,
            'mode': 'longslit',
            'date': plan.date,
            'texp': int(texp) if texp else '',
            'Conditions': args.conditions,
            'success': name not in failed,
        })
        if not texp:
            notes.append(f'{name}: observed but not in the plan -- texp left '
                         f'blank, fill it in from the night log')
    return rows, notes


def main(argv=None):
    args = parse_args(argv)
    plan = load_plan(args.plan_dir)
    if plan is None:
        raise SystemExit(f'no plan_result.json in {args.plan_dir}')

    rows, notes = build_rows(plan, args)
    resource = args.resource or Path(plan.output_dir).name
    out = args.out or f'{args.plan_dir}/{resource}_report.csv'

    with open(out, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f'Wrote {out}  ({len(rows)} targets, {plan.date}, '
          f'{args.conditions})')
    for note in notes:
        print(f'  NOTE: {note}')
    print('  success defaults to True -- pass --failed NAME for any target '
          'that did not yield a usable spectrum.')
    return out


if __name__ == '__main__':
    main()
