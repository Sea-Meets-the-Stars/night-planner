"""
Finder charts for targets that aren't in FFFF-PZ.

For an arbitrary target table the given coordinates *are* the thing to
point at, so there is no host-candidate question to resolve and no need
for the FFFF-PZ record. That leaves: fetch an image, find an offset star,
and draw the slit.

The slit is drawn at the parallactic angle for the target's own scheduled
exposure (night_planner.parallactic), not fitted through a second
candidate -- so it holds the dispersed spectrum in the slit rather than
chasing a companion. The FFFF-PZ path, which does fit two candidates,
stays available behind its own switch.

Created by JXP and Claude
"""

from pathlib import Path

import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS

# Longslit length actually drawn on the chart. LRIS's is ~2.9', matching
# what chime_ffff_pz_finder draws, so the two charts are comparable.
DEFAULT_SLIT_LENGTH_ARCMIN = 2.9
DEFAULT_SLIT_WIDTH_ARCSEC = 1.0
DEFAULT_FOV_ARCMIN = 4.0

# An offset star wants to be close enough to stay in the guider's reach,
# bright enough to acquire quickly, and not so bright it saturates.
OFFSET_MIN_MAG = 13.0
OFFSET_MAX_MAG = 19.0
OFFSET_MAX_SEP_ARCSEC = 100.0


def fetch_image(coord, fov_arcmin=DEFAULT_FOV_ARCMIN, pixels=600,
                 survey='CDS/P/PanSTARRS/DR1/r'):
    """
    Grab an image cutout around a position.

    Parameters
    ----------
    coord : SkyCoord
    fov_arcmin : float
    pixels : int
    survey : str
        HiPS identifier. Pan-STARRS r covers Dec > -30; DSS2 is the
        all-sky fallback.

    Returns
    -------
    (data, wcs)
    """
    from astroquery.hips2fits import hips2fits

    result = hips2fits.query(
        hips=survey, width=pixels, height=pixels,
        ra=coord.ra, dec=coord.dec, fov=fov_arcmin * u.arcmin,
        projection='TAN', format='fits')
    return result[0].data, WCS(result[0].header)


def find_offset_star(coord, max_sep_arcsec=OFFSET_MAX_SEP_ARCSEC,
                      min_mag=OFFSET_MIN_MAG, max_mag=OFFSET_MAX_MAG):
    """
    Nearest usable offset star from Gaia DR3.

    Returns
    -------
    dict with 'coord', 'mag', 'sep_arcsec', 'offset_ra', 'offset_dec'
    (offsets run star -> target, in arcsec, matching the starlist
    convention), or None if nothing suitable is in range.
    """
    from astroquery.vizier import Vizier

    vizier = Vizier(columns=['RA_ICRS', 'DE_ICRS', 'Gmag'],
                    column_filters={'Gmag': f'>{min_mag} && <{max_mag}'})
    vizier.ROW_LIMIT = 200
    tables = vizier.query_region(coord, radius=max_sep_arcsec * u.arcsec,
                                  catalog='I/355/gaiadr3')
    if not tables:
        return None

    table = tables[0]
    stars = SkyCoord(table['RA_ICRS'], table['DE_ICRS'], unit='deg')
    seps = coord.separation(stars).arcsec

    # Nearest first: a short offset is easier to trust than a bright one.
    order = np.argsort(seps)
    for i in order:
        if seps[i] < 1.0:        # that's the target itself
            continue
        star = stars[i]
        d_ra, d_dec = star.spherical_offsets_to(coord)
        return {
            'coord': star,
            'mag': float(table['Gmag'][i]),
            'sep_arcsec': float(seps[i]),
            'offset_ra': float(d_ra.arcsec),
            'offset_dec': float(d_dec.arcsec),
        }
    return None


def draw_finder(coord, name, out_path, slit_pa, data=None, wcs=None,
                 offset_star=None, fov_arcmin=DEFAULT_FOV_ARCMIN,
                 slit_length_arcmin=DEFAULT_SLIT_LENGTH_ARCMIN,
                 slit_width_arcsec=DEFAULT_SLIT_WIDTH_ARCSEC,
                 subtitle=''):
    """
    Render the finder chart: image, target, offset star, slit.

    Parameters
    ----------
    coord : SkyCoord
    slit_pa : float
        Position angle east of north, degrees.
    out_path : str or Path

    Returns
    -------
    Path
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from astropy.visualization import ZScaleInterval

    if data is None:
        data, wcs = fetch_image(coord, fov_arcmin)

    vmin, vmax = ZScaleInterval().get_limits(np.nan_to_num(data))

    fig = plt.figure(figsize=(7.5, 8.2))
    ax = fig.add_subplot(111, projection=wcs)
    ax.imshow(data, cmap='gray_r', origin='lower', vmin=vmin, vmax=vmax)

    ax.scatter(coord.ra.deg, coord.dec.deg, transform=ax.get_transform('world'),
               s=260, edgecolor='red', facecolor='none', lw=1.6, label=name)

    if offset_star is not None:
        star = offset_star['coord']
        ax.scatter(star.ra.deg, star.dec.deg,
                   transform=ax.get_transform('world'),
                   s=260, edgecolor='tab:cyan', facecolor='none', lw=1.6,
                   label=f"offset star G={offset_star['mag']:.1f}")

    # The slit: a rectangle centred on the target, long axis at slit_pa
    # measured east of north.
    half = (slit_length_arcmin / 2) * u.arcmin
    width = (slit_width_arcsec / 2) * u.arcsec
    pa = slit_pa * u.deg
    ends = [coord.directional_offset_by(pa, half),
            coord.directional_offset_by(pa + 180 * u.deg, half)]
    corners = []
    for end, sign in ((ends[0], 1), (ends[1], -1)):
        for perp in (pa + 90 * u.deg, pa - 90 * u.deg)[::sign]:
            corners.append(end.directional_offset_by(perp, width))
    corners.append(corners[0])
    ax.plot([c.ra.deg for c in corners], [c.dec.deg for c in corners],
            transform=ax.get_transform('world'), color='tab:purple', lw=1.3)

    ax.set_xlabel('RA (J2000)')
    ax.set_ylabel('Dec (J2000)')
    ax.grid(color='0.8', ls=':', lw=0.6)
    ax.legend(loc='upper right', fontsize=8, framealpha=0.9)

    title = f'{name}\n{coord.to_string("hmsdms", sep=":", precision=2)}'
    if subtitle:
        title += f'\n{subtitle}'
    ax.set_title(title, fontsize=10)

    caption = (f'slit {slit_length_arcmin:.1f}\' x {slit_width_arcsec:.1f}" '
               f'at PA = {slit_pa:.1f} deg (parallactic)')
    if offset_star is not None:
        caption += (f'\noffset star -> target: '
                    f"{offset_star['offset_ra']:+.2f}\", "
                    f"{offset_star['offset_dec']:+.2f}\" "
                    f"({offset_star['sep_arcsec']:.1f}\" away)")
    fig.text(0.5, 0.02, caption, ha='center', fontsize=8.5, color='0.25')

    out_path = Path(out_path)
    fig.savefig(out_path, dpi=130, bbox_inches='tight')
    plt.close(fig)
    return out_path


def generate_for_plan(plan, location, out_dir, targets=None,
                       fov_arcmin=DEFAULT_FOV_ARCMIN,
                       slit_length_arcmin=DEFAULT_SLIT_LENGTH_ARCMIN,
                       overwrite=False):
    """
    Finder chart + offset star + parallactic slit for each scheduled target.

    The slit angle is the dispersion-weighted mean parallactic angle over
    that target's own exposure, so it is the single fixed angle that loses
    the least light across the block actually being taken.

    Parameters
    ----------
    plan : PlanResult
    location : astropy EarthLocation
    out_dir : str or Path
        Finder PNGs and JSON sidecars are written here.
    targets : list of str, optional
        Restrict to these names; default is every scheduled target.
    overwrite : bool
        Re-render charts that already exist.

    Returns
    -------
    list of dict, one per target: name, png, pa, offset star info, error
    """
    import json

    from .parallactic import average_parallactic

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    wanted = set(targets) if targets else None
    results = []

    for target in plan.schedule:
        if wanted and target.name not in wanted:
            continue

        png = out_dir / f'{target.name}_finder.png'
        sidecar = out_dir / f'{target.name}_finder.json'
        if png.exists() and not overwrite:
            results.append({'name': target.name, 'png': str(png),
                            'skipped': 'already exists'})
            continue

        coord = SkyCoord(ra=target.ra_deg * u.deg, dec=target.dec_deg * u.deg)
        pa = average_parallactic(target.ra_deg, target.dec_deg,
                                  target.science_start, target.end, location)

        entry = {'name': target.name, 'slit_pa': pa['mean_pa'],
                 'pa_swing': pa['max_offset'],
                 'pa_weighted_offset': pa['weighted_offset'],
                 'primary_ra': target.ra_deg, 'primary_dec': target.dec_deg}

        try:
            star = find_offset_star(coord)
        except Exception as err:               # catalogue unreachable
            star, entry['offset_star_error'] = None, str(err)[:200]

        if star is not None:
            entry.update({
                'offset_star_ra': float(star['coord'].ra.deg),
                'offset_star_dec': float(star['coord'].dec.deg),
                'offset_star_mag': star['mag'],
                'offset_star_offset': star['sep_arcsec'],
                'offset_ra': star['offset_ra'],
                'offset_dec': star['offset_dec'],
            })

        try:
            # Every chart shows the longslit at parallactic, mask targets
            # included: the mask itself is configured at the telescope, so a
            # finder's job here is just to get you onto the right object.
            mask_note = (' · mask configured at the telescope'
                         if target.mode.startswith('MOS') else '')
            subtitle = (f"{target.science_start:%H:%M}-{target.end:%H:%M} · "
                        f"longslit at parallactic, holds to "
                        f"{pa['weighted_offset']:.0f} deg{mask_note}")
            draw_finder(coord, target.name, png, pa['mean_pa'],
                        offset_star=star, fov_arcmin=fov_arcmin,
                        slit_length_arcmin=slit_length_arcmin,
                        subtitle=subtitle)
            entry['png'] = str(png)
        except Exception as err:               # image service unreachable
            entry['error'] = f'{type(err).__name__}: {str(err)[:200]}'

        with open(sidecar, 'w') as f:
            json.dump(entry, f, indent=2)
        results.append(entry)

    return results
