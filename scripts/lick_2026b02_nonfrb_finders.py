"""
Created by JXP and Claude

Generate finder charts (PNG + JSON) for the Lick-2026B-02 non-FRB
spare/filler targets -- the author-supplied transients with RA/Dec/mag
given directly (2026yly, 2026sqf, 2026abgb, 2026yum, 2026zyg, 2025pht,
DLA_J0210+1702) -- none of which have a finder chart yet, since
`chime_ffff_pz_finder` (used for the 8 FRB targets on 2026-09-14) only
works through the FFFF-PZ database (`ffff_pz_utils.grab_frb`), and these
targets have no FFFF-PZ entry at all.

This is a standalone driver around the SAME core chime-ffff-pz machinery
`chime_ffff_pz_finder` uses internally (single-target branch: no slit,
no secondary/instrument, matching the len(gal_coords)==1 case in
`chime_ffff_pz/scripts/finder_chart.py`'s `set_coords()`), just skipping
the FFFF-PZ-database lookup (`grab_frb`/`grab_resource_instrument`) that
these targets don't have. Output JSON schema and file layout are kept
identical (same `TNS`/`primary_ra`/`primary_dec`/`slitcen_ra`/
`slitcen_dec`/`offset_star_*`/`offset_ra`/`offset_dec` keys) so
`chime_ffff_pz_starlist` (and this project's own starlist builder) can
read them exactly like an FRB finder.json, no special-casing needed.

Run in the `frb_env` conda environment (has chime_ffff_pz/frb/astropath).
"""

import os
import json

import numpy as np
from astropy.coordinates import SkyCoord
from astropy import units

from chime_ffff_pz.utils import coords as coord_utils
from chime_ffff_pz.path import plotting, catalogs
from chime_ffff_pz import finder, io

import sys
from pathlib import Path

# Repo-relative, so this runs wherever the checkout lives.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from night_planner.paths import ffffpz_data, plans_dir

_PLANS = plans_dir()

OUT_DIR = str(ffffpz_data('Observing', 'Lick-2026B-02'))
COPY_DIR = f'{_PLANS}/Lick-2026B-02/finder_charts'

MAX_STAR_SEP_ARCMIN = 2.
MIN_STAR_MAG = 12.
FINDER_SIZE_ARCMIN = 2.

# Non-FRB spare/filler targets, author-supplied RA/Dec (J2000). Same
# coordinates as SPARE_TARGETS in lick_2026b02_night2_calculations.py /
# DLA_TARGET in lick_2026b02_sep15_revision.py -- kept independent here
# since this script has no other dependency on those modules.
NONFRB_TARGETS = [
    dict(name='2026yly',        ra_str='09:13:38.17', dec_str='+76:28:18.1'),
    dict(name='2026sqf',        ra_str='10:38:47.96', dec_str='+53:30:34.1'),
    dict(name='2026abgb',       ra_str='23:27:42.00', dec_str='+23:35:17.0'),
    dict(name='2026yum',        ra_str='00:25:27.12', dec_str='+20:14:05.9'),
    dict(name='2026zyg',        ra_str='20:35:30.29', dec_str='+51:35:24.1'),
    dict(name='2025pht',        ra_str='04:41:28.86', dec_str='-02:51:55.6'),
    dict(name='DLA_J0210+1702', ra_str='02:10:11.00', dec_str='+17:02:45.0'),
]


def make_finder(name, ra_str, dec_str, out_dir):
    """Build one finder chart + JSON for a single-coordinate (no
    instrument/slit/secondary) target, mirroring
    chime_ffff_pz/scripts/finder_chart.py's main() single-target branch.

    Inputs
    ------
    name : str
        Target name (used as TNS/output-file stem).
    ra_str, dec_str : str
        Sexagesimal RA/Dec (J2000).
    out_dir : str
        Directory to write `{name}_finder.png` / `{name}_finder.json`.

    Returns
    -------
    str
        Path to the written PNG.
    """
    out_dict = {'TNS': name}

    gal_coords = coord_utils.radec_to_coord([(ra_str, dec_str)])
    center_coord = gal_coords[0]
    out_dict['primary_ra'] = center_coord.ra.deg
    out_dict['primary_dec'] = center_coord.dec.deg
    out_dict['slitcen_ra'] = center_coord.ra.deg
    out_dict['slitcen_dec'] = center_coord.dec.deg

    # Offset star in Pan-STARRS
    catalog, mag_key, stars = catalogs.query_catalog(
        'Pan-STARRS', center_coord, MAX_STAR_SEP_ARCMIN, skip_NGC=True,
        dust_correct=True)
    cut_size = stars['ang_size'] > 0.
    cut_mag = (stars[mag_key] < 18.5) & (stars[mag_key] > MIN_STAR_MAG)
    stars = stars[cut_size & cut_mag]
    if len(stars) == 0:
        raise ValueError(f"{name}: no offset star found in Pan-STARRS "
                          f"within {MAX_STAR_SEP_ARCMIN} arcmin")
    star = stars[0]
    offset_coord = SkyCoord(ra=star['ra'], dec=star['dec'], unit='deg')

    sep = center_coord.separation(offset_coord).to('arcsec')
    PA_off = center_coord.position_angle(offset_coord)
    dec_off = -1 * np.cos(PA_off) * sep
    ra_off = -1 * np.sin(PA_off) * sep  # East = higher RA

    out_dict['offset_star_ra'] = offset_coord.ra.deg
    out_dict['offset_star_dec'] = offset_coord.dec.deg
    out_dict['offset_star_offset'] = sep.value
    out_dict['offset_ra'] = ra_off.value
    out_dict['offset_dec'] = dec_off.value

    # Image cutout
    finder_ras = np.append(gal_coords.ra.deg, offset_coord.ra.deg)
    finder_decs = np.append(gal_coords.dec.deg, offset_coord.dec.deg)
    array, wcs_out, im_fits, footprint = plotting.grab_image_wcs(
        center_coord, finder_ras, finder_decs,
        size_arcmins=FINDER_SIZE_ARCMIN, filt='r', survey_str='Pan-STARRS')

    os.makedirs(out_dir, exist_ok=True)
    outfile = os.path.join(out_dir, f'{name}_finder.png')
    jsonfile = outfile.replace('.png', '.json')

    finder.generate(array, wcs_out, name, center_coord,
                     primary_coord=gal_coords[0],
                     offset_star_coord=offset_coord,
                     slit=None, second_coord=None, outfile=outfile)

    with open(jsonfile, 'w') as f:
        json.dump(out_dict, f, indent=4, sort_keys=True)

    return outfile


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(COPY_DIR, exist_ok=True)

    written = []
    for t in NONFRB_TARGETS:
        jsonfile = os.path.join(OUT_DIR, f"{t['name']}_finder.json")
        if os.path.exists(jsonfile):
            print(f"SKIP {t['name']}: finder already exists at {jsonfile}")
            continue
        print(f"Building finder for {t['name']}...")
        outfile = make_finder(t['name'], t['ra_str'], t['dec_str'], OUT_DIR)
        print(f'  Wrote: {outfile}')
        print(f"  Wrote: {outfile.replace('.png', '.json')}")

        # Convenience copy of the PNG into night-planner (same convention
        # as the FRB finders -- see Logs 2026-09-15 "move ... to
        # Lick-2026B-02" entry: chime-ffff-pz is the canonical location,
        # night-planner's finder_charts/ is a copy for easy viewing).
        import shutil
        copy_path = os.path.join(COPY_DIR, os.path.basename(outfile))
        shutil.copy(outfile, copy_path)
        written.append(t['name'])

    print(f"\n{len(written)} new finder chart(s) written: {written}")


if __name__ == '__main__':
    main()
