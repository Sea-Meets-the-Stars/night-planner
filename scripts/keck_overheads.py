"""
Keck telescope slew-time rules, shared by every Keck instrument plan
(LRIS, DEIMOS, ...), not LRIS-specific.

Created by JXP and Claude

Rules (per the author, 2026-09-29):
  - Base slew between any two pointings: 10 min (raised from 5,
    per the author 2026-09-30).
  - Moving from Dec below +20 deg to Dec above +20 deg: 20 min.

The reverse direction (above +20 -> below +20) is the base 10 min; only
the south-to-north crossing is penalized, as stated by the author.
"""

KECK_SLEW_BASE_MIN = 10
KECK_SLEW_DEC_CROSS_MIN = 20
KECK_SLEW_DEC_BOUNDARY = 20.0  # deg


def keck_slew_minutes(from_dec, to_dec):
    """
    Slew time (minutes) between two Keck pointings.

    Parameters
    ----------
    from_dec : float or None
        Dec (deg) of the previous pointing. None means no previous pointing
        is known, so the base slew is used.
    to_dec : float
        Dec (deg) of the next pointing.

    Returns
    -------
    int
    """
    if (from_dec is not None and from_dec < KECK_SLEW_DEC_BOUNDARY
            and to_dec > KECK_SLEW_DEC_BOUNDARY):
        return KECK_SLEW_DEC_CROSS_MIN
    return KECK_SLEW_BASE_MIN
