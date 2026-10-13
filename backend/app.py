"""
FastAPI backend for the night-plan viewer.

Serves one normalized plan (night_planner.plan_result.PlanResult) however
it was produced, so the frontend never has to know whether Keck's or
Lick's scheduler ran, or whether the targets came from FFFF-PZ or a
spreadsheet.

Generating a plan is slow (the Keck path makes live ETC calls per
target), so it's split in two: POST /api/generate does the work once and
writes plan_result.json, and every viewer endpoint reads that file back.

Run it with `night-planner serve`.

Created by JXP and Claude
"""

import contextlib
import io
import os
import shutil
import tempfile
import zipfile
from datetime import timedelta
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from night_planner.cli import INSTRUMENTS, generate_plan
from night_planner.plan_store import load_plan
from night_planner.targets_io import (
    TargetTableError, detect_mapping, load_targets,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = REPO_ROOT / 'frontend'
PLANS_ROOT = REPO_ROOT / 'Night_plans'
UPLOAD_DIR = Path(tempfile.gettempdir()) / 'night-planner-uploads'

app = FastAPI(title='night-planner')


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------

def _safe_dir(output_dir):
    """
    Resolve a caller-supplied plan directory, refusing anything outside
    Night_plans/ or the upload scratch area.

    Every endpoint takes the plan directory from the query string, so this
    is the one place that stops a crafted path from reading the rest of
    the filesystem.
    """
    path = Path(output_dir).expanduser().resolve()
    allowed = (PLANS_ROOT.resolve(), UPLOAD_DIR.resolve(),
               Path(tempfile.gettempdir()).resolve())
    if not any(path == root or path.is_relative_to(root) for root in allowed):
        raise HTTPException(400, f'plan directory outside allowed roots: {path}')
    if not path.is_dir():
        raise HTTPException(404, f'no such plan directory: {path}')
    return path


def _require_plan(output_dir):
    """Load a saved plan or 404 with a useful message."""
    plan = load_plan(str(_safe_dir(output_dir)))
    if plan is None:
        raise HTTPException(
            404, 'no plan_result.json here yet -- generate the plan first')
    return plan


# --------------------------------------------------------------------
# Instruments and target tables
# --------------------------------------------------------------------

@app.get('/api/instruments')
def list_instruments():
    """Instruments the planner can run, for the home page."""
    from night_planner.adapters import SITES
    return [{'instrument': name,
             'telescope': SITES.get(name, {}).get('telescope', ''),
             'can_build_excel': bool(spec.get('build')),
             'supports_own_targets': 'targets_csv' in spec.get('supports', set()),
             'supports': sorted(spec.get('supports', set()))}
            for name, spec in sorted(INSTRUMENTS.items())]


@app.get('/api/plans')
def list_plans():
    """Existing plan directories under Night_plans/, newest first."""
    out = []
    for path in sorted(PLANS_ROOT.glob('*')):
        if not path.is_dir():
            continue
        saved = path / 'plan_result.json'
        out.append({'name': path.name, 'output_dir': str(path),
                    'has_plan': saved.exists(),
                    'modified': saved.stat().st_mtime if saved.exists() else None})
    return sorted(out, key=lambda p: (p['modified'] or 0), reverse=True)


@app.post('/api/targets/inspect')
def inspect_targets(file: UploadFile = File(None), path: str = Query(None)):
    """
    Report how a target table's columns map to the canonical schema.

    Returns the detected mapping plus `candidates` so the frontend can ask
    the user only about what's genuinely ambiguous -- and a short preview
    so they can see they uploaded what they meant to.
    """
    if file is not None:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        saved = UPLOAD_DIR / file.filename
        with open(saved, 'wb') as f:
            shutil.copyfileobj(file.file, f)
        source = str(saved)
    elif path:
        source = str(Path(path).expanduser().resolve())
        if not os.path.exists(source):
            raise HTTPException(404, f'no such file: {source}')
    else:
        raise HTTPException(400, 'supply either an uploaded file or a path')

    import pandas as pd
    frame = pd.read_csv(source)
    mapping = detect_mapping(frame)

    preview = []
    if mapping.ok:
        try:
            canonical = load_targets(frame, mapping=mapping)
            preview = canonical[['name', 'ra_deg', 'dec_deg', 'mag']].head(10) \
                .to_dict('records')
        except TargetTableError as err:
            mapping.issues.append(str(err))

    return {'path': source, 'n_rows': len(frame),
            'columns': list(frame.columns),
            'mapping': mapping.to_dict(), 'preview': preview}


# --------------------------------------------------------------------
# Generating and reading plans
# --------------------------------------------------------------------

class GenerateRequest(BaseModel):
    """
    Everything the setup page can send.

    The optional fields are genuinely Optional rather than `str = None`:
    under Pydantic v2 the latter types the field as `str` and rejects an
    explicit null, which is exactly what a blank form field sends.
    """
    instrument: str
    targets_csv: Optional[str] = None
    output_dir: Optional[str] = None
    date: Optional[str] = None
    start: Optional[str] = None        # 'HH:MM' local, manual/ToO start
    blocks: list = []                  # [{'start','end','reason'}]
    forced: list = []                  # [{'target','minutes'}]
    max_targets: Optional[int] = None
    assume_masks: bool = False         # schedule mask-needing targets anyway


@app.post('/api/generate')
def generate(req: GenerateRequest):
    """
    Run the instrument's pipeline and return the normalized plan.

    Defined with `def` rather than `async def` on purpose: the scheduler is
    blocking, CPU- and network-bound, so FastAPI runs it in a worker thread
    instead of stalling the event loop.
    """
    if req.instrument not in INSTRUMENTS:
        raise HTTPException(400, f'unknown instrument: {req.instrument}')

    # The instrument scripts carry hardcoded fallback paths from the run
    # they were written for. That's a convenience on the command line and a
    # hazard here: a blank form field would otherwise silently read another
    # run's targets and overwrite that run's plan directory. Require both.
    if not req.targets_csv:
        raise HTTPException(400, 'choose a target table -- the planner will '
                                 'not fall back to another run\'s targets')
    if not req.output_dir:
        raise HTTPException(400, 'choose an output directory -- the planner '
                                 'will not write into another run\'s plan')

    # A bare name means a plan directory, not a path relative to wherever
    # the server happens to have been started. Typing "Keck-2026B-04"
    # otherwise silently creates it beside the repo root, where the viewer
    # will never list it.
    output_dir = Path(req.output_dir).expanduser()
    if not output_dir.is_absolute():
        output_dir = PLANS_ROOT / output_dir
    output_dir = output_dir.resolve()
    if not output_dir.is_relative_to(PLANS_ROOT.resolve()):
        raise HTTPException(400, f'plans are written under {PLANS_ROOT}; '
                                 f'{output_dir} is outside it')

    # Catch an instrument/option mismatch here, where it can be explained.
    # Letting it through means argparse rejects the flags somewhere inside
    # the instrument module and the only thing that reaches the browser is
    # an exit code.
    supports = INSTRUMENTS[req.instrument].get('supports', set())
    asked = {name for name in ('targets_csv', 'output_dir', 'date',
                                'max_targets', 'assume_masks')
             if getattr(req, name)}
    asked |= {'forced'} if req.forced else set()
    unsupported = sorted(asked - supports)
    if unsupported:
        raise HTTPException(
            400, f"the {req.instrument} pipeline does not accept "
                 f"{', '.join(unsupported)} -- it is still tied to its own "
                 f"run's targets and output directory. Use lris for a plan "
                 f"built from your own target table.")

    argv = []
    for flag, value in (('--targets-csv', req.targets_csv),
                         ('--output-dir', str(output_dir)),
                         ('--date', req.date),
                         ('--start', req.start)):
        if value:
            argv += [flag, str(value)]
    if req.max_targets:
        argv += ['--max-targets', str(req.max_targets)]
    for block in req.blocks:
        reason = block.get('reason') or 'blocked'
        argv += ['--block', f"{block['start']}-{block['end']}@{reason}"]
    for forced in req.forced:
        argv += ['--force', f"{forced['target']}@{forced['minutes']}"]
    if req.assume_masks:
        argv.append('--assume-masks')

    try:
        # argparse writes its complaint to stderr and then raises SystemExit
        # carrying only an exit code, so capture the text or the browser gets
        # a bare number.
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            plan = generate_plan(req.instrument, argv)
    except TargetTableError as err:
        # The table needs a column mapping -- hand back what was detected
        # so the frontend can ask rather than just failing.
        raise HTTPException(
            422, {'error': str(err), 'mapping': err.mapping.to_dict()})
    except SystemExit as err:
        detail = stderr.getvalue().strip().splitlines()
        message = detail[-1] if detail else f'exit code {err}'
        raise HTTPException(400, f'the {req.instrument} planner rejected this '
                                 f'request: {message}')
    return plan.to_dict()


@app.get('/api/plan')
def get_plan(output_dir: str):
    """The saved normalized plan for a directory."""
    return _require_plan(output_dir).to_dict()


class RegenerateRequest(BaseModel):
    output_dir: str
    forced: list = []    # [{'target','minutes'}] -- replaces any previous set


@app.post('/api/regenerate')
def regenerate(req: RegenerateRequest):
    """
    Re-run an existing plan with a different set of forced targets.

    Reuses the exact inputs the plan was generated from, so nothing else
    shifts underneath the comparison -- only the --force flags are
    replaced. Which is the point: the observer decides to rescue a
    rejected target *after* seeing why it was dropped.
    """
    plan = _require_plan(req.output_dir)
    request = plan.request or {}
    if not request.get('argv'):
        raise HTTPException(
            409, 'this plan predates recorded inputs, so it cannot be '
                 're-run automatically -- generate it again from Setup')

    # Drop any previous --force pairs; the incoming list is authoritative.
    argv, skip = [], False
    for token in request['argv']:
        if skip:
            skip = False
            continue
        if token == '--force':
            skip = True
            continue
        if token.startswith('--force='):
            continue
        argv.append(token)

    for forced in req.forced:
        argv += ['--force', f"{forced['target']}@{forced['minutes']}"]

    try:
        return generate_plan(request.get('instrument', plan.instrument), argv).to_dict()
    except SystemExit as err:
        raise HTTPException(400, f'planner exited: {err}')


@app.get('/api/airmass')
def airmass(output_dir: str, target: str, step_min: int = 5):
    """
    Airmass/alt/az track for one target across its night.

    Computed on demand rather than stored: it's a dense curve that would
    bloat every plan file, and it's cheap to recompute for one target.
    """
    plan = _require_plan(output_dir)
    match = [t for t in plan.schedule if t.name == target]
    decision = [d for d in plan.decisions if d.name == target]
    if match:
        ra_deg, dec_deg = match[0].ra_deg, match[0].dec_deg
    elif decision and decision[0].ra_deg is not None:
        ra_deg, dec_deg = decision[0].ra_deg, decision[0].dec_deg
    else:
        raise HTTPException(404, f'{target} is not in this plan')

    from night_planner.cli import _load_module
    calc = _load_module(INSTRUMENTS[plan.instrument]['calc'])

    points, time = [], plan.sun.sunset
    while time <= plan.sun.sunrise:
        am, alt, az, ha = calc.calculate_airmass(
            ra_deg, dec_deg, time.astimezone(__import__('datetime').timezone.utc))
        # calculate_airmass() returns a 99.9 sentinel below the horizon.
        # Emit null instead so a chart draws a gap rather than a spike.
        points.append({'time': time.isoformat(),
                       'airmass': round(am, 3) if alt > 0 else None,
                       'alt': round(alt, 2), 'az': round(az, 2),
                       'ha': round(ha, 3)})
        time += timedelta(minutes=step_min)

    scheduled = ({'start': match[0].science_start.isoformat(),
                  'end': match[0].end.isoformat()} if match else None)
    return {'target': target, 'ra_deg': ra_deg, 'dec_deg': dec_deg,
            'points': points, 'scheduled': scheduled,
            'sun': plan.sun.to_dict()}


# --------------------------------------------------------------------
# Files: finders, starlist, export
# --------------------------------------------------------------------

@app.get('/api/image')
def image(output_dir: str, name: str):
    """Serve a finder chart from the plan's finders/ directory."""
    base = _safe_dir(output_dir) / 'finders'
    path = (base / name).resolve()
    if not path.is_relative_to(base.resolve()) or not path.is_file():
        raise HTTPException(404, f'no such finder: {name}')
    return FileResponse(path, media_type='image/png',
                        headers={'Cache-Control': 'public, max-age=86400'})


@app.get('/api/finders')
def finders(output_dir: str):
    """List the finder charts available for a plan."""
    base = _safe_dir(output_dir) / 'finders'
    if not base.is_dir():
        return []
    return sorted(p.name for p in base.glob('*.png'))


@app.get('/api/starlist', response_class=PlainTextResponse)
def starlist(output_dir: str, name: str = None):
    """
    Raw starlist text.

    Defaults to the richest starlist present: the one with offset stars and
    PA, rather than the coordinates-only list the scheduler writes.
    """
    base = _safe_dir(output_dir)
    if name:
        path = (base / name).resolve()
        if not path.is_relative_to(base.resolve()) or not path.is_file():
            raise HTTPException(404, f'no such starlist: {name}')
    else:
        candidates = sorted(base.glob('*.starlist'),
                            key=lambda p: p.stat().st_size, reverse=True)
        if not candidates:
            raise HTTPException(404, 'no starlist in this plan directory')
        path = candidates[0]
    return path.read_text()


class FinderRequest(BaseModel):
    output_dir: str
    targets: list = []            # empty = every scheduled target
    use_ffffpz: bool = False      # fit the slit through two host candidates
    resource: Optional[str] = None  # FFFF-PZ Resource name, for that path
    overwrite: bool = False


@app.post('/api/finders/generate')
def generate_finders(req: FinderRequest):
    """
    Build finder charts for a plan's targets.

    Default path is self-contained: an image cutout, an offset star from
    Gaia, and the slit drawn at the target's own dispersion-weighted
    parallactic angle. Nothing is asked of FFFF-PZ, because for an
    arbitrary target table the given coordinates are the target.

    With use_ffffpz the chart comes from chime_ffff_pz_finder instead,
    which fits the slit through the two best host candidates -- the right
    choice when both are worth catching in one slit.
    """
    from night_planner.adapters import SITES
    from night_planner.finder import generate_for_plan

    base = _safe_dir(req.output_dir)
    plan = _require_plan(req.output_dir)
    site = SITES.get(plan.instrument)
    if site is None:
        raise HTTPException(400, f'no site known for {plan.instrument}')

    finder_dir = base / 'finders'

    if req.use_ffffpz:
        return _ffffpz_finders(req, plan, finder_dir)

    results = generate_for_plan(plan, site['location'], finder_dir,
                                 targets=req.targets or None,
                                 overwrite=req.overwrite)
    return {'mode': 'parallactic', 'finder_dir': str(finder_dir),
            'results': results}


def _ffffpz_finders(req, plan, finder_dir):
    """
    Run chime_ffff_pz_finder for each target and collect its output.

    That CLI lives in another environment and talks to the FFFF-PZ server,
    so it is run as a subprocess rather than imported.
    """
    import subprocess

    frb_python = Path('/home/lordrick/miniconda3/envs/frb_env/bin/'
                      'chime_ffff_pz_finder')
    if not frb_python.exists():
        raise HTTPException(503, f'chime_ffff_pz_finder not found at {frb_python}')
    resource = req.resource or Path(plan.output_dir).name
    obs_dir = Path('/home/lordrick/Projects/chime-ffff-pz/chime_ffff_pz/data/'
                   'Observing') / resource
    if not obs_dir.is_dir():
        raise HTTPException(400, f'no FFFF-PZ Observing directory for '
                                 f'{resource} at {obs_dir}')

    env = {**os.environ, 'FFFF_PZ_URL': os.environ.get(
        'FFFF_PZ_GLOBAL_URL', 'https://frb.chimenet.ca/f4pz/')}
    names = req.targets or [t.name for t in plan.schedule]
    results = []
    for name in names:
        proc = subprocess.run([str(frb_python), name, resource],
                               cwd=str(obs_dir), env=env,
                               capture_output=True, text=True, timeout=300)
        entry = {'name': name, 'returncode': proc.returncode}
        if proc.returncode != 0:
            entry['error'] = (proc.stderr.strip().splitlines() or ['failed'])[-1]
        else:
            finder_dir.mkdir(parents=True, exist_ok=True)
            for suffix in ('png', 'json'):
                src = obs_dir / f'{name}_finder.{suffix}'
                if src.exists():
                    shutil.copy(src, finder_dir / src.name)
            entry['png'] = str(finder_dir / f'{name}_finder.png')
        results.append(entry)
    return {'mode': 'ffffpz', 'finder_dir': str(finder_dir), 'results': results}


class StarlistRequest(BaseModel):
    output_dir: str
    include_standards: bool = True
    max_airmass: float = 2.0
    filename: Optional[str] = None
    allow_missing_finders: bool = False


@app.post('/api/starlist/generate')
def generate_starlist(req: StarlistRequest):
    """
    Write a starlist for a plan, optionally bracketed by flux standards.

    Standards are chosen from the PypeIt library at the times they'd
    actually be taken, so they match the science frames in airmass as well
    as in time.
    """
    from night_planner.adapters import SITES
    from night_planner.standards import load_library
    from night_planner.starlist import build_starlist

    base = _safe_dir(req.output_dir)
    plan = _require_plan(req.output_dir)

    site = SITES.get(plan.instrument)
    if site is None:
        raise HTTPException(400, f'no site known for {plan.instrument}')

    # A starlist without offset stars is close to useless at the telescope
    # for faint hosts, and the offsets come from the finder step. Refuse
    # rather than quietly emitting coordinate-only rows.
    finder_dir = base / 'finders'
    scheduled = {t.name for t in plan.schedule}
    have = {p.stem.replace('_finder', '')
            for p in finder_dir.glob('*_finder.json')} if finder_dir.is_dir() else set()
    missing = sorted(scheduled - have)
    if missing and not req.allow_missing_finders:
        raise HTTPException(
            409, {'error': 'generate finder charts first -- the starlist needs '
                           'their offset stars and slit angles',
                  'missing': missing,
                  'hint': 'use the Finders page, or re-send with '
                          'allow_missing_finders to get coordinate-only rows'})

    try:
        library = load_library() if req.include_standards else None
    except FileNotFoundError as err:
        raise HTTPException(503, str(err))

    text, notes = build_starlist(
        plan, include_standards=req.include_standards,
        location=site['location'], library=library,
        finder_dir=base / 'finders', max_airmass=req.max_airmass)

    name = req.filename or f'{base.name}_generated.starlist'
    path = (base / name).resolve()
    if not path.is_relative_to(base.resolve()):
        raise HTTPException(400, 'starlist name escapes the plan directory')
    path.write_text(text)

    return {'path': str(path), 'name': name, 'text': text, 'notes': notes}


@app.get('/api/export')
def export(output_dir: str, name: str = None):
    """Zip the whole plan directory for download."""
    base = _safe_dir(output_dir)
    stem = name or base.name
    archive = Path(tempfile.gettempdir()) / f'{stem}.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(base.rglob('*')):
            if path.is_file():
                zf.write(path, path.relative_to(base))
    return FileResponse(archive, media_type='application/zip',
                        filename=f'{stem}.zip')


# Mounted last so it never shadows the API routes above.
if FRONTEND_DIR.is_dir():
    app.mount('/', StaticFiles(directory=str(FRONTEND_DIR), html=True),
              name='frontend')
