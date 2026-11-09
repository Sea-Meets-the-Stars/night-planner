"""
Parallactic angle: the position angle of the zenith at a target, i.e. the
direction atmospheric dispersion smears the light.

A longslit set to the parallactic angle keeps the dispersed image inside
the slit, so no blue light is lost relative to red. That matters more for
a faint host spectrum than aligning the slit through a second candidate.

The catch is that it changes through the night -- fastest near transit --
so a fixed slit can only match it on average. average_parallactic() gives
that average and, as importantly, the spread, which is what tells you
whether a single fixed angle is good enough for the exposure or whether
the block should be split.

Created by JXP and Claude
"""

from datetime import timedelta

import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time


def parallactic_angle(ra_deg, dec_deg, when, location):
    """
    Parallactic angle in degrees at one instant.

    q = atan2( sin(HA), tan(lat) cos(dec) - sin(dec) cos(HA) )

    Parameters
    ----------
    ra_deg, dec_deg : float
    when : datetime (tz-aware)
    location : astropy EarthLocation

    Returns
    -------
    float : degrees, wrapped to [0, 180) -- a slit has no head or tail, so
    an angle and its opposite describe the same orientation.
    """
    time = Time(when)
    lst = time.sidereal_time('apparent', longitude=location.lon)
    hour_angle = (lst.hour - ra_deg / 15.0) % 24
    if hour_angle > 12:
        hour_angle -= 24

    ha = np.radians(hour_angle * 15.0)
    dec = np.radians(dec_deg)
    lat = np.radians(location.lat.deg)

    q = np.degrees(np.arctan2(
        np.sin(ha),
        np.tan(lat) * np.cos(dec) - np.sin(dec) * np.cos(ha)))
    return q % 180.0


def parallactic_track(ra_deg, dec_deg, start, end, location, step_minutes=5):
    """
    Parallactic angle sampled across an exposure, with dispersion weight.

    Atmospheric dispersion grows as tan(zenith angle), so a sample taken
    at airmass 1.0 carries almost no penalty for a misaligned slit while
    one at airmass 2 carries a lot. `weight` captures that, and is what
    makes the weighted mean below meaningful.

    Returns
    -------
    list of dict with 'time', 'pa', 'alt', 'weight'
    """
    from astropy.coordinates import AltAz

    coord = SkyCoord(ra=ra_deg * u.deg, dec=dec_deg * u.deg)
    points, when = [], start
    while when <= end:
        alt = float(coord.transform_to(
            AltAz(obstime=Time(when), location=location)).alt.deg)
        points.append({
            'time': when,
            'pa': parallactic_angle(ra_deg, dec_deg, when, location),
            'alt': alt,
            'weight': float(np.tan(np.radians(max(90.0 - alt, 0.0)))),
        })
        when += timedelta(minutes=step_minutes)
    return points


def average_parallactic(ra_deg, dec_deg, start, end, location, step_minutes=5):
    """
    Mean parallactic angle over an exposure, with its spread.

    Averaged as unit vectors on a 180-degree axis rather than as plain
    numbers: a slit crossing the 0/180 boundary (which happens whenever a
    target transits) would otherwise average to something perpendicular to
    the truth.

    Parameters
    ----------
    ra_deg, dec_deg : float
    start, end : datetime (tz-aware)
    location : astropy EarthLocation

    Returns
    -------
    dict with
        mean_pa   : the angle to set a fixed slit to
        spread    : half-range of the swing, degrees
        start_pa, end_pa
        max_offset: worst-case angle between the slit and the true
                    parallactic angle during the exposure
    """
    track = parallactic_track(ra_deg, dec_deg, start, end, location, step_minutes)
    angles = np.array([p['pa'] for p in track])
    weights = np.array([p['weight'] for p in track])
    if weights.sum() <= 0:
        weights = np.ones_like(weights)

    # Double the angles to map the 180-degree axis onto a full circle,
    # average there, then halve back.
    doubled = np.radians(angles * 2)
    plain = np.degrees(np.arctan2(np.sin(doubled).mean(),
                                   np.cos(doubled).mean())) / 2 % 180
    weighted = np.degrees(np.arctan2(
        (np.sin(doubled) * weights).sum() / weights.sum(),
        (np.cos(doubled) * weights).sum() / weights.sum())) / 2 % 180

    offsets = np.abs((angles - weighted + 90) % 180 - 90)
    # The penalty that actually matters: how badly the slit is misaligned
    # at the moments when there is real dispersion to misalign against.
    weighted_offset = float((offsets * weights).sum() / weights.sum())

    return {
        'mean_pa': float(weighted),
        'unweighted_mean_pa': float(plain),
        'spread': float(offsets.max()),
        'start_pa': float(angles[0]),
        'end_pa': float(angles[-1]),
        'max_offset': float(offsets.max()),
        'weighted_offset': weighted_offset,
        'min_alt': float(min(p['alt'] for p in track)),
        'n_samples': len(angles),
    }
