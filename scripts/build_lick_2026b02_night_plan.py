"""
Build the Night-plan Excel workbook for Lick-2026B-02 (2026-09-14).

Created by JXP and Claude

Sheet structure follows the corrected Lick-2026B-01 template (date-named
sheet, not target-named; see that run's HOWTO_night_plan_creation.md):
Observing Checklist, then one sheet per night ("September 14th"), with a
15-column timeline (LST/UT/PST start, Duration, End, Action, target,
RA/DEC, HA start/end, mag, sec mag, red/blue side, Redshift, Comments)
plus a small PST->LST sidereal-time-calculator sidebar.

Unlike the original 2026B-01 workbook (fixed observing order, HA
violations found and patched after the fact by fix_ha_limits.py), every
timed row here is taken directly from
scripts/lick_2026b02_calculations.py's HA-window-aware schedule
(Night_plans/Lick-2026B-02/selected_targets_night1.csv), so start/end
times already respect the Shane HA/Dec limits by construction. The one
genuine dead-time gap the scheduler could not fill (no target has an
HA-legal window then) is written into the sheet explicitly rather than
silently skipped, per the "log the reason at every skip point" lesson
recorded in claudes_brain.md.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from astropy import units as u
from astropy.coordinates import SkyCoord

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))
from night_planner.paths import plans_dir

_PLANS = plans_dir()
from scripts.lick_2026b02_calculations import (
    LICK, PST, find_twilight, calculate_lst, ha_at, FORCED_FIRST_TNS,
)

DATE = '2026-09-14'
SHEET_NAME = 'September 14th'
OUT_DIR = f'{_PLANS}/Lick-2026B-02'

KAST_SETUP_NOTE = ('Kast setup: d57 dichroic | red 600/7500 | '
                    'blue 600/4310 | 2" slit')

# Standard star: only Feige_110 satisfies the Shane HA limits at BOTH the
# start of the night (HA=-4.10h, AM~3.1) and right after the last science
# target (HA=+3.35h, AM~2.2) among the project's 3-star option list
# (HZ_44, Feige_110, BD+28_4211) for this specific date/LST range -- see
# the report in claude_prompts/night_plans/lick_2026sep14.md for the
# HA/airmass table that ruled out the other two. Reused for both ends of
# the night rather than forcing an out-of-limits alternative.
STD_STAR = dict(name='Feige_110', ra='23:19:58.4', dec='-05:09:56',
                 ra_hours=23.333, mag='11.8')


def pst_to_lst(pst_dt):
    utc_dt = pst_dt.astimezone(timezone.utc)
    return calculate_lst(utc_dt).hour


def pst_to_ut(pst_dt):
    utc_dt = pst_dt.astimezone(timezone.utc)
    return utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0


def format_ra_dec(ra_deg, dec_deg):
    c = SkyCoord(ra=ra_deg * u.deg, dec=dec_deg * u.deg, frame='icrs')
    return (c.ra.to_string(unit=u.hour, sep=':', precision=2, pad=True),
            c.dec.to_string(unit=u.deg, sep=':', precision=1, pad=True))


def add_observing_checklist(ws):
    items = ['Dome open', 'Telescope tracking', 'Focus achieved',
              'Standard star (evening)', 'Science targets started',
              'Standard star (post-science)', 'Bias frames taken',
              'Flat fields taken', 'Dome closed', 'Data backed up']
    ws['A1'] = 'Lick 2026B-02 Observing Checklist'
    ws['A1'].font = Font(size=14, bold=True)
    ws['A3'] = 'Task'
    ws['B3'] = 'Done'
    ws['A3'].font = Font(bold=True)
    ws['B3'].font = Font(bold=True)
    for i, item in enumerate(items, start=4):
        ws[f'A{i}'] = item
        ws[f'B{i}'] = False
    ws.column_dimensions['A'].width = 30
    ws.column_dimensions['B'].width = 10


def build_sheet(wb, sched_df, twilight):
    ws = wb.create_sheet(SHEET_NAME)

    headers = ['Start (LST)', 'Start (UT)', 'Start (PST)', 'Duration', 'End (PST)',
               'Action', 'target', 'RA', 'DEC', 'HA start', 'HA end', 'mag(r)',
               'sec mag', 'red side', 'blue side', 'Redshift;', 'Comments']
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color='CCCCCC', end_color='CCCCCC', fill_type='solid')

    widths = [12, 12, 12, 12, 12, 26, 15, 12, 12, 10, 10, 8, 8, 15, 15, 10, 36]
    for col, w in zip('ABCDEFGHIJKLMNOPQ', widths):
        ws.column_dimensions[col].width = w

    current_row = 2

    def add_row(action, target='', ra='', dec='', mag_r='', sec_mag='',
                red_side='', blue_side='', redshift='', comments='',
                start=None, end=None, ra_hours=None):
        nonlocal current_row
        lst_start = pst_to_lst(start)
        ut = pst_to_ut(start)
        duration_min = (end - start).total_seconds() / 60.0
        ha_start_str = ha_end_str = ''
        if ra_hours is not None:
            ha_start_str = f'{ha_at(ra_hours, lst_start):.2f}'
            ha_end_str = f'{ha_at(ra_hours, pst_to_lst(end)):.2f}'

        row = [f'{lst_start:.2f}', f'{ut:.2f}', start.strftime('%H:%M'),
               f'{duration_min:.0f} min' if duration_min > 0 else '',
               end.strftime('%H:%M') if duration_min > 0 else '',
               action, target, ra, dec, ha_start_str, ha_end_str, mag_r,
               sec_mag, red_side, blue_side, redshift, comments]
        for col, val in enumerate(row, start=1):
            ws.cell(row=current_row, column=col, value=val)
        current_row += 1

    t = twilight['evening_pst']

    scheduled = sched_df[sched_df['scheduled']].copy()
    scheduled['start_pst'] = pd.to_datetime(scheduled['start_pst'], format='mixed')
    scheduled['end_pst'] = pd.to_datetime(scheduled['end_pst'], format='mixed')
    scheduled = scheduled.sort_values('start_pst').reset_index(drop=True)

    forced_row = None
    if len(scheduled) and scheduled.iloc[0]['TNS'] == FORCED_FIRST_TNS:
        forced_row = scheduled.iloc[0]
        scheduled = scheduled.iloc[1:].reset_index(drop=True)

    # Dome open / focus.
    add_row('Focus', start=t, end=t + timedelta(minutes=5))
    t += timedelta(minutes=5)

    if forced_row is not None:
        # Forced-first setting target (author's call -- see
        # lick_2026b02_calculations.py's FORCED_FIRST_TNS docstring):
        # observed immediately after focus, ahead of the evening
        # standard, so the standard doesn't eat into its already-thin
        # HA-legal window (the window's absolute close time is fixed by
        # the Shane HA_MAX mechanical limit, not by when the target
        # starts, so starting it as early as possible maximizes the
        # exposure obtained).
        # start_pst from the calculations script is the raw HA-window
        # entry (19:44, instant), ignoring the focus block just added;
        # end_pst is the fixed HA_MAX cutoff (an absolute clock time, not
        # relative to start) so it holds regardless -- the 5 min consumed
        # by focus comes straight out of this target's exposure, on top
        # of the truncation already noted in skip_reason.
        start = max(t, forced_row['start_pst'].to_pydatetime())
        end = forced_row['end_pst'].to_pydatetime()
        ra_str, dec_str = format_ra_dec(forced_row['RA_deg'], forced_row['Dec_deg'])
        add_row('Science + overhead (forced first)', target=forced_row['TNS'],
                 ra=ra_str, dec=dec_str, mag_r=f"{forced_row['mag_r']:.2f}",
                 red_side=forced_row['red_side'], blue_side=forced_row['blue_side'],
                 comments=(f"P(O|x)={forced_row['POx']:.3f}; tags={forced_row['tags']}; "
                           f"{forced_row['skip_reason']}"),
                 start=start, end=end, ra_hours=forced_row['RA_hours'])
        t = end

    # Evening standard (Feige_110, highest-AM option within HA limits at
    # dusk -- see module docstring)
    add_row('Standard Star', target=STD_STAR['name'], ra=STD_STAR['ra'],
             dec=STD_STAR['dec'], mag_r=STD_STAR['mag'],
             comments='Evening standard (highest AM within HA limits at dusk)',
             start=t + timedelta(minutes=5), end=t + timedelta(minutes=10),
             ra_hours=STD_STAR['ra_hours'])
    t += timedelta(minutes=10)

    for _, targ in scheduled.iterrows():
        start = targ['start_pst'].to_pydatetime()
        end = targ['end_pst'].to_pydatetime()

        slew_start = max(t, start - timedelta(minutes=5))
        if slew_start > t:
            add_row('Idle -- no target in HA-legal window',
                    comments='RA gap: no pulled target has -5.0h<=HA<=+3.75h '
                             'during this stretch (see target_analysis.csv)',
                    start=t, end=slew_start)

        add_row(f"slew to --> {targ['TNS']}", start=slew_start, end=start)

        ra_str, dec_str = format_ra_dec(targ['RA_deg'], targ['Dec_deg'])
        add_row('Science + overhead', target=targ['TNS'], ra=ra_str, dec=dec_str,
                mag_r=f"{targ['mag_r']:.2f}", red_side=targ['red_side'],
                blue_side=targ['blue_side'],
                comments=f"P(O|x)={targ['POx']:.3f}; tags={targ['tags']}",
                start=start, end=end, ra_hours=targ['RA_hours'])
        t = end

    # Post-science standard + calibrations
    add_row('Standard Star', target=STD_STAR['name'], ra=STD_STAR['ra'],
             dec=STD_STAR['dec'], mag_r=STD_STAR['mag'],
             comments='Post-science standard (same star; only cataloged '
                      'option within HA limits this late -- see report)',
             start=t + timedelta(minutes=5), end=t + timedelta(minutes=10),
             ra_hours=STD_STAR['ra_hours'])
    t += timedelta(minutes=10)
    add_row('Bias frames', start=t, end=t + timedelta(minutes=5))
    t += timedelta(minutes=5)
    add_row('Flat fields', start=t, end=t + timedelta(minutes=10))
    t += timedelta(minutes=10)

    margin_min = (twilight['morning_pst'] - t).total_seconds() / 60.0
    note_row = current_row + 1
    ws.cell(row=note_row, column=1,
            value=f'Done by {t.strftime("%H:%M")} PST, '
                  f'{margin_min:.0f} min before 18-deg morning twilight '
                  f'({twilight["morning_pst"].strftime("%H:%M")} PST).')
    ws.cell(row=note_row, column=1).font = Font(italic=True)

    # Sidereal time calculator sidebar
    ws.cell(row=1, column=19, value='Sidereal Time Calculator').font = Font(bold=True)
    ws.cell(row=2, column=19, value='PST').font = Font(bold=True)
    ws.cell(row=2, column=20, value='LST').font = Font(bold=True)
    sample_times = [twilight['evening_pst'] + timedelta(hours=h) for h in (0, 2, 4, 6, 8)]
    for i, st in enumerate(sample_times, start=3):
        ws.cell(row=i, column=19, value=st.strftime('%H:%M'))
        ws.cell(row=i, column=20, value=f'{pst_to_lst(st):.2f}')

    return ws


def add_extras_sheet(wb, extras_sched_df):
    """Separate sheet for gap-fill "extras" (lower tier than the primary
    science list -- see scripts/lick_2026b02_extras.py): FFFF-PZ targets
    with status AmbiguousHost/TooDusty and P(O|x) >= 0.6, not already in
    the primary pull, slotted into the primary schedule's idle intervals.
    Kept on its own sheet so it is never confused with the primary
    targets on the "September 14th" sheet.
    """
    ws = wb.create_sheet('Extras (Gap-Fill)')
    ws['A1'] = 'Lick 2026B-02 -- Gap-Fill Extras (lower tier; see extras_gap_fill_analysis.md)'
    ws['A1'].font = Font(size=13, bold=True)

    headers = ['Start (PST)', 'End (PST)', 'target', 'RA (h)', 'Dec (deg)',
               'HA start', 'HA end', 'mag(r)', 'P(O|x)', 'status',
               'red side', 'blue side']
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=3, column=col, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color='FFE4B5', end_color='FFE4B5', fill_type='solid')

    widths = [12, 12, 15, 10, 10, 9, 9, 8, 9, 14, 10, 10]
    for col, w in zip('ABCDEFGHIJKL', widths):
        ws.column_dimensions[col].width = w

    scheduled = extras_sched_df[extras_sched_df['scheduled'].astype(str) == 'True'].copy()
    scheduled['start_pst'] = pd.to_datetime(scheduled['start_pst'], format='mixed')
    scheduled['end_pst'] = pd.to_datetime(scheduled['end_pst'], format='mixed')
    scheduled = scheduled.sort_values('start_pst').reset_index(drop=True)

    row = 4
    for _, targ in scheduled.iterrows():
        ra_str, dec_str = format_ra_dec(targ['RA_deg'], targ['Dec_deg'])
        values = [targ['start_pst'].strftime('%H:%M'), targ['end_pst'].strftime('%H:%M'),
                  targ['TNS'], f"{targ['RA_hours']:.2f}", f"{targ['Dec_deg']:.2f}",
                  f"{targ['ha_entry']:.2f}", f"{targ['ha_exit']:.2f}",
                  f"{targ['mag_r']:.2f}", f"{targ['POx']:.3f}", targ['status'],
                  targ['red_side'], targ['blue_side']]
        for col, val in enumerate(values, start=1):
            ws.cell(row=row, column=col, value=val)
        row += 1

    if len(scheduled) == 0:
        ws.cell(row=row, column=1, value='No extras fit this night\'s idle intervals.')

    return ws


def main():
    sched_df = pd.read_csv(f'{OUT_DIR}/selected_targets_night1.csv')
    extras_sched_df = pd.read_csv(f'{OUT_DIR}/extras_schedule.csv')
    twilight = find_twilight(DATE)

    wb = Workbook()
    wb.remove(wb.active)
    add_observing_checklist(wb.create_sheet('Observing Checklist'))
    build_sheet(wb, sched_df, twilight)
    add_extras_sheet(wb, extras_sched_df)

    out_path = f'{OUT_DIR}/Lick_2026B-02_Night_plan.xlsx'
    wb.save(out_path)
    print(f'Night plan saved to: {out_path}')
    return out_path


if __name__ == '__main__':
    main()
