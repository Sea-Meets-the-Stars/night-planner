"""
Build a Keck-format starlist from a plan.

Targets come out in observing order, annotated with when and how they're
observed. Flux standards are optional and, when asked for, are chosen at
the times they'd actually be taken rather than from a fixed pair -- see
night_planner.standards.

Offset-star rows and slit PA are not invented here: those come from the
finder-chart step, and a row without them says so rather than carrying a
plausible-looking guess.

Created by JXP and Claude
"""

import json
from pathlib import Path

from astropy import units as u
from astropy.coordinates import SkyCoord

from .standards import pick_bracketing_standards, starlist_row


def _finder_data(finder_dir, name):
    """Offset-star/PA JSON for one target, if the finder step produced it."""
    if not finder_dir:
        return None
    path = Path(finder_dir) / f'{name}_finder.json'
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def build_starlist(plan, include_standards=True, location=None,
                    library=None, finder_dir=None, max_airmass=2.0):
    """
    Render a starlist for a plan.

    Parameters
    ----------
    plan : PlanResult
    include_standards : bool
        Add a flux standard before the first target and after the last.
    location : astropy EarthLocation
        Required when include_standards is set.
    finder_dir : str or Path, optional
        Directory of `<target>_finder.json` files. When present, each
        target gains an `_S` offset-star row and a rotdest.
    max_airmass : float
        Ceiling when choosing standards.

    Returns
    -------
    (text, notes) -- the starlist, and any caveats worth showing the user.
    """
    notes = []
    lines = [
        f'# {plan.telescope} starlist for {plan.date} '
        f'({Path(plan.output_dir).name})',
        '# Created by JXP and Claude -- night-planner, schedule order',
    ]

    standards = None
    if include_standards:
        if location is None:
            raise ValueError('include_standards needs a site location')
        standards = pick_bracketing_standards(plan, location, library,
                                               max_airmass=max_airmass)
        lines.append('# _S rows = offset star; raoffset/decoffset = star -> '
                     'target (arcsec)')

    lines.append('')

    if standards and standards.get('evening'):
        s = standards['evening']
        lines.append(starlist_row(
            s['name'], s['coord'],
            f"Evening flux standard, {s['when']:%H:%M} (AM {s['airmass']:.2f})"))
        lines.append('')
    elif include_standards:
        notes.append('No standard was observable at the start of the night '
                     f'below airmass {max_airmass}.')

    missing_finders, no_star = [], []
    for target in plan.schedule:
        coord = SkyCoord(ra=target.ra_deg * u.deg, dec=target.dec_deg * u.deg)
        when = (f'{target.science_start:%H:%M}-{target.end:%H:%M}, '
                f'{target.exposure_red or target.mode}')
        finder = _finder_data(finder_dir, target.name)

        has_pa = finder and finder.get('slit_pa') is not None
        # A finder can yield a slit angle but no offset star -- the angle is
        # computed, the star has to exist in the catalogue. Treat them
        # separately so one missing piece doesn't discard the other.
        has_star = finder and finder.get('offset_star_ra') is not None

        if not has_pa:
            missing_finders.append(target.name)
            lines.append(f'{starlist_row(target.name, coord)}  # {when} | '
                         f'{target.mode} | NO FINDER: no offset star/PA')
            continue

        row = starlist_row(target.name, coord).rstrip()
        row += f" rotdest={finder['slit_pa']:.2f} rotmode=pa"
        # rotdest is the parallactic longslit angle on every row. For a mask
        # target that's just the acquisition pointing -- the mask setup is
        # done at the telescope -- so say which it is rather than letting the
        # number read as a mask PA.
        suffix = ' | mask set at the telescope' if target.mode.startswith('MOS') else ''
        if not has_star:
            suffix += ' | NO OFFSET STAR: acquire on the target'
        lines.append(f'{row}  # {when} | {target.mode}{suffix}')

        if has_star:
            star = SkyCoord(ra=finder['offset_star_ra'] * u.deg,
                            dec=finder['offset_star_dec'] * u.deg)
            offset = starlist_row(f'{target.name}_S', star).rstrip()
            offset += (f" raoffset={finder['offset_ra']:.2f} "
                       f"decoffset={finder['offset_dec']:.2f} "
                       f"rotdest={finder['slit_pa']:.2f} rotmode=pa")
            lines.append(offset)
        else:
            no_star.append(target.name)

    if standards and standards.get('morning'):
        s = standards['morning']
        lines += ['', starlist_row(
            s['name'], s['coord'],
            f"Morning flux standard, {s['when']:%H:%M} (AM {s['airmass']:.2f})")]
    elif include_standards:
        notes.append('No standard was observable at the end of the night '
                     f'below airmass {max_airmass}.')

    if no_star:
        notes.append('No offset star found within range for '
                     + ', '.join(no_star)
                     + ' -- the slit angle is set, but acquisition has to be '
                       'on the target itself.')
    if missing_finders:
        notes.append('No finder output for ' + ', '.join(missing_finders)
                     + ' -- those rows carry coordinates only, with no offset '
                       'star or slit PA.')

    return '\n'.join(lines) + '\n', notes
