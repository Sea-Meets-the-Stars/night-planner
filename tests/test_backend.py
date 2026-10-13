"""Tests for the viewer backend API.

Uses FastAPI's TestClient against the real saved plan, so these also act
as a check that plan_result.json stays readable by the API.

Created by JXP and Claude.
"""

import json
from pathlib import Path

import pytest

pytest.importorskip('fastapi')
from fastapi.testclient import TestClient

from backend.app import app
from night_planner.plan_result import PlanResult

PLAN_DIR = str(Path(__file__).resolve().parent.parent
               / 'Night_plans' / 'Keck-2026B-02')

client = TestClient(app)


def _has_saved_plan():
    return Path(PLAN_DIR, 'plan_result.json').exists()


needs_plan = pytest.mark.skipif(not _has_saved_plan(),
                                reason='no generated plan on disk')


def test_instruments_lists_both_telescopes():
    """The registry is exposed with telescope names.

    Inputs: none.
    Outputs: none (asserts on success).
    """
    names = {i['instrument']: i for i in client.get('/api/instruments').json()}
    assert 'lris' in names and 'kast' in names
    assert names['lris']['telescope'] == 'Keck I'


@needs_plan
def test_plan_round_trips_through_the_api():
    """/api/plan returns something PlanResult.from_dict can rebuild.

    Inputs: none.
    Outputs: none (asserts on success).
    """
    data = client.get('/api/plan', params={'output_dir': PLAN_DIR}).json()
    plan = PlanResult.from_dict(data)
    assert plan.schedule
    assert plan.summary()['n_scheduled'] == len(plan.schedule)


@needs_plan
def test_airmass_is_null_below_the_horizon():
    """Below-horizon samples are null, not the 99.9 sentinel.

    Inputs: none.
    Outputs: none (asserts on success).
    """
    plan = client.get('/api/plan', params={'output_dir': PLAN_DIR}).json()
    target = plan['schedule'][0]['name']
    points = client.get('/api/airmass',
                        params={'output_dir': PLAN_DIR, 'target': target,
                                'step_min': 30}).json()['points']
    assert points
    for point in points:
        if point['alt'] <= 0:
            assert point['airmass'] is None
        else:
            assert 1.0 <= point['airmass'] < 99


def test_plan_directory_outside_night_plans_is_refused():
    """A crafted output_dir can't read arbitrary filesystem locations.

    Inputs: none.
    Outputs: none (asserts on success).
    """
    assert client.get('/api/plan', params={'output_dir': '/etc'}).status_code == 400


@needs_plan
def test_finder_name_cannot_escape_the_plan_directory():
    """Path traversal in a finder name is refused.

    Inputs: none.
    Outputs: none (asserts on success).
    """
    resp = client.get('/api/image', params={'output_dir': PLAN_DIR,
                                            'name': '../../../etc/passwd'})
    assert resp.status_code == 404


@needs_plan
def test_export_zip_contains_the_plan_files():
    """The export is a zip of the plan directory.

    Inputs: none.
    Outputs: none (asserts on success).
    """
    import io
    import zipfile

    resp = client.get('/api/export', params={'output_dir': PLAN_DIR,
                                             'name': 'test_export'})
    assert resp.status_code == 200
    names = zipfile.ZipFile(io.BytesIO(resp.content)).namelist()
    assert 'selected_targets.csv' in names


def test_inspect_refuses_to_guess_ambiguous_ra(tmp_path):
    """An ambiguous table comes back not-ok, with candidates to ask about.

    Inputs: none (writes a temp CSV).
    Outputs: none (asserts on success).
    """
    csv = tmp_path / 'ambiguous.csv'
    csv.write_text('name,ra,dec,mag\nZ,18.57,46.86,22.4\n')
    data = client.post('/api/targets/inspect',
                       params={'path': str(csv)}).json()
    assert data['mapping']['ok'] is False
    assert data['mapping']['candidates']['ra'] == ['ra']


def test_inspect_maps_a_foreign_spreadsheet(tmp_path):
    """Odd column names and sexagesimal coords are detected automatically.

    Inputs: none (writes a temp CSV).
    Outputs: none (asserts on success).
    """
    csv = tmp_path / 'mine.csv'
    csv.write_text('object,RA,DEC,Rmag\nHOST-A,17 46 48.45,+41 14 16.9,19.99\n')
    data = client.post('/api/targets/inspect', params={'path': str(csv)}).json()
    assert data['mapping']['ok'] is True
    assert data['mapping']['columns']['name'] == 'object'
    assert data['preview'][0]['ra_deg'] == pytest.approx(266.7018, abs=1e-3)
