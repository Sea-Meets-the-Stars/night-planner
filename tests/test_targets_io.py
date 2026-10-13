"""Tests for reading arbitrary target tables into the canonical schema.

The cases that matter most here are the refusals: silently guessing a
coordinate's units, or silently substituting an FRB's burst position for
its host galaxy, would both point the telescope somewhere else while
producing an output that looks perfectly normal.

Created by JXP and Claude.
"""

import pandas as pd
import pytest

from night_planner.targets_io import (
    TargetTableError, detect_mapping, load_targets,
)


def test_ffffpz_columns_map_to_host_not_burst():
    """Pri_RA/Pri_Dec (host) win over FRB_RA/FRB_Dec (burst position).

    Inputs: none.
    Outputs: none (asserts on success).
    """
    df = pd.DataFrame({'TNS': ['FRB1'], 'FRB_RA': [1.0], 'FRB_Dec': [2.0],
                       'Pri_RA': [278.49], 'Pri_Dec': [46.86],
                       'Pri_mag': [22.4], 'Pri_POx': [0.99],
                       'FRB_tags': ['CHIME'], 'FRB_DM': [800.0]})
    out = load_targets(df)
    assert out.loc[0, 'ra_deg'] == 278.49
    assert out.loc[0, 'dec_deg'] == 46.86
    assert out.loc[0, 'name'] == 'FRB1'
    assert out.loc[0, 'tags'] == 'CHIME'


def test_burst_position_alone_is_refused():
    """A table carrying only FRB_RA/FRB_Dec must not be read as pointings.

    Inputs: none.
    Outputs: none (asserts on success).
    """
    df = pd.DataFrame({'TNS': ['FRB1'], 'FRB_RA': [278.4], 'FRB_Dec': [46.8],
                       'Pri_mag': [22.4]})
    with pytest.raises(TargetTableError):
        load_targets(df)


def test_sexagesimal_coordinates():
    """'09:13:38.17' is read as hours of RA, '+76:28:18.1' as degrees of Dec.

    Inputs: none.
    Outputs: none (asserts on success).
    """
    df = pd.DataFrame({'Name': ['A'], 'RA': ['09:13:38.17'],
                       'Dec': ['+76:28:18.1'], 'magnitude': [15.9]})
    out = load_targets(df)
    assert out.loc[0, 'ra_deg'] == pytest.approx(138.409042, abs=1e-5)
    assert out.loc[0, 'dec_deg'] == pytest.approx(76.471694, abs=1e-5)


def test_ra_in_hours_when_named_so():
    """A column called ra_hours is multiplied up to degrees.

    Inputs: none.
    Outputs: none (asserts on success).
    """
    df = pd.DataFrame({'id': ['Y'], 'ra_hours': [18.57], 'dec': [46.86],
                       'mag': [22.4]})
    assert load_targets(df).loc[0, 'ra_deg'] == pytest.approx(278.55)


def test_ambiguous_numeric_ra_is_refused():
    """A bare numeric RA with every value <= 24 could be hours or degrees.

    Inputs: none.
    Outputs: none (asserts on success).
    """
    df = pd.DataFrame({'name': ['Z'], 'ra': [18.57], 'dec': [46.86],
                       'mag': [22.4]})
    with pytest.raises(TargetTableError) as excinfo:
        load_targets(df)
    assert 'hours or degrees' in str(excinfo.value)
    # The partial mapping rides along so a caller can ask just this one thing.
    assert excinfo.value.mapping.columns['ra'] == 'ra'


def test_explicit_mapping_resolves_ambiguity():
    """Supplying ra_unit lets an otherwise-ambiguous table through.

    Inputs: none.
    Outputs: none (asserts on success).
    """
    df = pd.DataFrame({'name': ['Z'], 'ra': [18.57], 'dec': [46.86],
                       'mag': [22.4]})
    mapping = detect_mapping(df)
    mapping.ra_unit = 'hour'
    mapping.issues.clear()
    assert load_targets(df, mapping=mapping).loc[0, 'ra_deg'] == pytest.approx(278.55)


def test_optional_columns_always_exist():
    """pox/tags/dm are created empty when the source table lacks them.

    Inputs: none.
    Outputs: none (asserts on success).
    """
    df = pd.DataFrame({'object': ['A'], 'RA_deg': [10.0], 'DEC': [20.0],
                       'Rmag': [19.5]})
    out = load_targets(df)
    for column in ('pox', 'tags', 'dm'):
        assert column in out.columns


def test_source_columns_are_preserved():
    """Unmapped source columns survive into the canonical frame.

    Inputs: none.
    Outputs: none (asserts on success).
    """
    df = pd.DataFrame({'object': ['A'], 'RA_deg': [10.0], 'DEC': [20.0],
                       'Rmag': [19.5], 'notes': ['from my spreadsheet']})
    assert load_targets(df).loc[0, 'notes'] == 'from my spreadsheet'


def test_unreadable_coordinates_are_reported_with_names():
    """Bad coordinate rows fail loudly, naming the offending targets.

    Inputs: none.
    Outputs: none (asserts on success).
    """
    df = pd.DataFrame({'name': ['GOOD', 'BAD'], 'RA_deg': [10.0, None],
                       'dec': [20.0, 20.0], 'mag': [19.5, 19.5]})
    with pytest.raises(TargetTableError) as excinfo:
        load_targets(df)
    assert 'BAD' in str(excinfo.value)
