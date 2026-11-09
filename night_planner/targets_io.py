"""
Read a table of targets -- from FFFF-PZ or from anywhere else -- into one
canonical schema.

The night plan should not care where its targets came from. Everything
downstream reads the canonical columns below; this module is the single
place that knows FFFF-PZ calls a host position `Pri_RA` and someone
else's spreadsheet calls it `RA`.

Canonical columns
-----------------
Required: name, ra_deg, dec_deg, mag
Optional: pox, tags, dm   (created empty when the source lacks them)

Source columns that don't map are passed through untouched, so nothing
is lost.

Column detection is automatic for the common spellings and only asks for
help when it would otherwise have to guess -- see detect_mapping().

Created by JXP and Claude
"""

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd
from astropy.coordinates import Angle
from astropy import units as u

REQUIRED_FIELDS = ('name', 'ra', 'dec', 'mag')
OPTIONAL_FIELDS = ('pox', 'tags', 'dm')

# Candidate source-column spellings per field, highest priority first.
#
# FRB_RA/FRB_Dec are deliberately absent: in an FFFF-PZ table those are the
# *burst* position, while Pri_RA/Pri_Dec are the host galaxy -- the thing
# the telescope actually points at. Auto-matching the burst position would
# silently observe the wrong place, so a table that only carries FRB_RA has
# to be mapped by hand.
ALIASES = {
    'name': ['tns', 'name', 'target', 'target_name', 'objname', 'object', 'id'],
    'ra': ['pri_ra', 'ra_deg', 'radeg', 'ra_hours', 'ra', 'rightascension',
           'right_ascension', 'ra_j2000'],
    'dec': ['pri_dec', 'dec_deg', 'decdeg', 'dec', 'de', 'declination',
            'dec_j2000'],
    'mag': ['pri_mag', 'mag_r', 'rmag', 'r_mag', 'mag', 'magnitude'],
    'pox': ['pri_pox', 'pox', 'p_ox'],
    'tags': ['frb_tags', 'tags', 'tag'],
    'dm': ['frb_dm', 'dm'],
}

# Source columns whose name already settles the unit question. Anything
# outside these two sets is "bare" (e.g. plain 'ra') and gets the
# all-values-<=24 ambiguity check below.
_HOUR_NAMES = ('ra_hours', 'rahours', 'ra_h', 'rah')
_DEG_NAMES = ('ra_deg', 'radeg', 'pri_ra')  # pri_ra: FFFF-PZ, always degrees


class TargetTableError(ValueError):
    """Raised when a table can't be read without guessing.

    Carries the partial `mapping` so a caller (the GUI) can show the user
    what was detected and ask only about what's genuinely unclear.
    """

    def __init__(self, message, mapping):
        super().__init__(message)
        self.mapping = mapping


@dataclass
class ColumnMapping:
    """Which source column feeds each canonical field."""
    columns: dict = field(default_factory=dict)    # field -> source column
    ra_unit: str = 'deg'                            # 'deg' or 'hour'
    issues: list = field(default_factory=list)      # why it isn't usable as-is
    candidates: dict = field(default_factory=dict)  # field -> plausible columns

    @property
    def ok(self):
        return not self.issues

    def to_dict(self):
        return {'columns': dict(self.columns), 'ra_unit': self.ra_unit,
                'issues': list(self.issues),
                'candidates': {k: list(v) for k, v in self.candidates.items()},
                'ok': self.ok}


def _norm(header):
    """Normalize a header for matching: lowercase, strip punctuation/space."""
    return ''.join(ch for ch in str(header).lower() if ch.isalnum() or ch == '_')


def _looks_sexagesimal(series):
    """True if the values look like '01:56:29' / '+13 51 58' rather than numbers."""
    sample = series.dropna().astype(str).head(20)
    if sample.empty:
        return False
    return bool((sample.str.contains(':') | sample.str.contains(r'\s')).mean() > 0.5)


def detect_mapping(df):
    """
    Work out which columns hold name/RA/Dec/mag (and the optional extras).

    Only flags an issue when it would otherwise have to guess: a missing
    required field, two equally-good candidates, or a bare numeric RA
    column whose values are all <= 24 (hours or degrees? getting that
    wrong silently points the telescope somewhere else entirely).

    Parameters
    ----------
    df : DataFrame

    Returns
    -------
    ColumnMapping
    """
    normalized = {_norm(c): c for c in df.columns}
    mapping = ColumnMapping()

    for fieldname in REQUIRED_FIELDS + OPTIONAL_FIELDS:
        hits = [normalized[a] for a in ALIASES[fieldname] if a in normalized]
        mapping.candidates[fieldname] = hits
        if hits:
            mapping.columns[fieldname] = hits[0]
        elif fieldname in REQUIRED_FIELDS:
            mapping.issues.append(
                f"no column found for '{fieldname}' "
                f"(looked for: {', '.join(ALIASES[fieldname])})")

    ra_col = mapping.columns.get('ra')
    if ra_col is not None:
        if _norm(ra_col) in _HOUR_NAMES:
            mapping.ra_unit = 'hour'
        elif _looks_sexagesimal(df[ra_col]):
            # Sexagesimal RA is conventionally hours; Dec is always degrees.
            mapping.ra_unit = 'hour'
        elif _norm(ra_col) in _DEG_NAMES:
            mapping.ra_unit = 'deg'
        else:
            values = pd.to_numeric(df[ra_col], errors='coerce').dropna()
            if len(values) and values.abs().max() <= 24:
                mapping.issues.append(
                    f"'{ra_col}' is numeric and every value is <= 24, so it "
                    f"could be hours or degrees -- say which (ra_unit)")
    return mapping


def _angle_to_deg(series, unit, is_ra):
    """Convert a coordinate column to degrees, sexagesimal or numeric."""
    if _looks_sexagesimal(series):
        default = u.hourangle if is_ra else u.deg
        return np.array([
            Angle(str(v), unit=default).to(u.deg).value if pd.notna(v) else np.nan
            for v in series])
    values = pd.to_numeric(series, errors='coerce')
    return values * 15.0 if (is_ra and unit == 'hour') else values


def load_targets(source, mapping=None):
    """
    Load any target table into the canonical schema.

    Parameters
    ----------
    source : str or DataFrame
        CSV path, or an already-loaded frame.
    mapping : ColumnMapping, optional
        Supply this to override/complete auto-detection (what the GUI
        sends back after asking the user). When omitted, detection must
        succeed on its own or TargetTableError is raised.

    Returns
    -------
    DataFrame
        The source columns, plus canonical `name`, `ra_deg`, `dec_deg`,
        `mag` and the optional `pox`, `tags`, `dm`.

    Raises
    ------
    TargetTableError
        If the table can't be read without guessing. The partial mapping
        is attached to the exception.
    """
    df = pd.read_csv(source) if isinstance(source, str) else source.copy()

    if mapping is None:
        mapping = detect_mapping(df)
    if not mapping.ok:
        raise TargetTableError(
            'cannot read this target table unambiguously: '
            + '; '.join(mapping.issues), mapping)

    out = df.copy()
    out['name'] = df[mapping.columns['name']].astype(str)
    out['ra_deg'] = _angle_to_deg(df[mapping.columns['ra']], mapping.ra_unit,
                                   is_ra=True)
    out['dec_deg'] = _angle_to_deg(df[mapping.columns['dec']], 'deg', is_ra=False)
    out['mag'] = pd.to_numeric(df[mapping.columns['mag']], errors='coerce')

    # Optional fields always exist downstream, empty if the source lacked them.
    for fieldname, empty in (('pox', np.nan), ('tags', ''), ('dm', np.nan)):
        source_col = mapping.columns.get(fieldname)
        out[fieldname] = df[source_col] if source_col else empty

    bad = out['ra_deg'].isna() | out['dec_deg'].isna()
    if bad.any():
        names = ', '.join(out.loc[bad, 'name'].head(5))
        raise TargetTableError(
            f'{int(bad.sum())} row(s) have unreadable coordinates: {names}',
            mapping)
    return out
