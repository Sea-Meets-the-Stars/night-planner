"""Tests that nothing in this repo is pinned to one person's home directory.

Created by JXP and Claude.

The failure these guard against is silent: a hardcoded
/home/<someone>/Projects/... keeps working perfectly for whoever wrote it
and breaks for everyone else, which is how make_lick_night_plan.py carried
a broken /home/xavier/... default for months without anyone noticing.
"""

import os
import re
from pathlib import Path

import pytest

from night_planner.paths import (
    REPO_ROOT, ffffpz_root, lick_template, plan_dir, plans_dir,
)

# Directories whose contents are generated or vendored, not authored here.
SKIP_DIRS = {'__pycache__', '.git', '.pytest_cache', 'Night_plans',
             'node_modules'}

# An absolute path under a user's home or observatory scratch space.
HARDCODED = re.compile(r'''['"(]\s*(/home/[a-z]+/|/Users/|/mnt/scratch/)''')


def _source_files():
    """Every authored source file in the repo.

    Inputs: none.
    Outputs: iterator of Path.
    """
    for path in REPO_ROOT.rglob('*'):
        if not path.is_file() or path.suffix not in {'.py', '.js', '.html'}:
            continue
        if SKIP_DIRS & set(path.relative_to(REPO_ROOT).parts):
            continue
        yield path


def test_no_source_file_hardcodes_a_home_directory():
    """No code path is pinned to one machine's layout.

    Comments and docstrings may still mention such a path by way of
    explanation; only string literals that code actually uses are caught,
    which is why the pattern requires a quote or an open paren.

    Inputs: none.
    Outputs: none (asserts on success).
    """
    offenders = []
    for path in _source_files():
        for n, line in enumerate(path.read_text().splitlines(), 1):
            stripped = line.lstrip()
            if stripped.startswith('#') or stripped.startswith('*'):
                continue
            if HARDCODED.search(line):
                offenders.append(f'{path.relative_to(REPO_ROOT)}:{n}: {stripped}')
    assert not offenders, (
        'hardcoded machine-specific paths found; use night_planner.paths:\n'
        + '\n'.join(offenders))


def test_repo_root_is_this_checkout():
    """REPO_ROOT is derived from the file's location, not configured.

    Inputs: none.
    Outputs: none (asserts on success).
    """
    assert (REPO_ROOT / 'night_planner' / 'paths.py').exists()
    assert (REPO_ROOT / 'setup.cfg').exists()


def test_plans_dir_defaults_inside_the_repo_and_can_be_overridden(monkeypatch):
    """Plans land in <repo>/Night_plans unless NIGHT_PLANNER_PLANS says otherwise.

    Inputs: none.
    Outputs: none (asserts on success).
    """
    monkeypatch.delenv('NIGHT_PLANNER_PLANS', raising=False)
    assert plans_dir() == REPO_ROOT / 'Night_plans'
    assert plan_dir('Lick-2026B-02') == REPO_ROOT / 'Night_plans' / 'Lick-2026B-02'

    monkeypatch.setenv('NIGHT_PLANNER_PLANS', '/tmp/elsewhere')
    assert plans_dir() == Path('/tmp/elsewhere')
    assert plan_dir('Keck-2026B-02') == Path('/tmp/elsewhere/Keck-2026B-02')


def test_missing_external_checkout_names_the_variable_to_set(monkeypatch):
    """A missing FFFF-PZ checkout fails with instructions, not a stray path.

    Inputs: none.
    Outputs: none (asserts on success).
    """
    monkeypatch.setenv('FFFF_PZ_REPO', '/tmp/definitely-not-a-checkout')
    with pytest.raises(FileNotFoundError, match='FFFF_PZ_REPO'):
        ffffpz_root()
    assert ffffpz_root(required=False) is None


def test_lick_template_has_no_default(monkeypatch):
    """The template must be pointed at; guessing it would confuse the error.

    Inputs: none.
    Outputs: none (asserts on success).
    """
    monkeypatch.delenv('LICK_NIGHT_PLAN_TEMPLATE', raising=False)
    assert lick_template(required=False) is None
    with pytest.raises(FileNotFoundError, match='LICK_NIGHT_PLAN_TEMPLATE'):
        lick_template()

    monkeypatch.setenv('LICK_NIGHT_PLAN_TEMPLATE', '/tmp/template.xlsx')
    assert lick_template() == Path('/tmp/template.xlsx')
