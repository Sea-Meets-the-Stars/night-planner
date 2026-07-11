# Claude's Brain — night-planner

This file is Claude's persistent memory for the **night-planner** project. As I
learn about night planning, the telescope, the author's preferences, and how this
repository is organized, I record the durable, reusable knowledge here — the
things a fresh session would want to know. A dated **Version History** at the
bottom tracks every update.

## Project purpose

- Teach Claude to generate a **night plan for a modern, professional telescope**,
  learning from two professional astronomers (J. Xavier Prochaska, `jxp@ucsc.edu`,
  and a colleague).
- Longer-term goal: a **GitHub-hosted webpage dashboard** monitoring all of the
  author's Claude-assisted projects.

## Working conventions (from CLAUDE.md)

- **Git:** the author runs all git commands; I use only read-only git.
- **Calculations:** always write them as a Python script to disk (reproducible),
  never inline-only.
- **Logging:** same approach as the ClimateIntelligence repo — a daily narrative
  log I write at `Logs/YYYY/MM/YYYY-MM-DD.md`, plus `Logs/log_summary.csv` written
  automatically by the `Stop` hook (`.claude/hooks/log_usage.py`). CO2 ≈ 0.076 g
  per 1,000 tokens. See [`../Logs/logging.md`](../Logs/logging.md).
- **Coding:** Python; methods not classes; imports at top; docstrings with
  inputs/outputs; matplotlib/seaborn/Bokeh for plots; `"Created by JXP and Claude"`
  header on every file and docstring.

## Repository layout (as of 2026-07-11)

- `CLAUDE.md` — guidance for Claude (this project's rules).
- `claude_prompts/start_up.md` — ordered start-up prompts driving initial setup.
- `context/` — durable context; `claudes_brain.md` (this file).
- `Logs/` — daily narrative logs, `log_summary.csv`, `logging.md`.
- `.claude/` — `settings.json` (Stop hook wiring), `hooks/log_usage.py`,
  `skills/` (`grill-me`, `critical-partner`; copied from ClimateIntelligence).
- `setup.py` / `setup.cfg` / `pyproject.toml` — packaging. Author's convention
  (from `python/linetools` and `Projects/XAI`): metadata + deps in **setup.cfg**,
  `pyproject.toml` limited to `[build-system]`, `setup.py` a minimal `setup()` shim.
- `requirements.txt` — mirror of `setup.cfg` install_requires.
- `night_planner/` — the Python package (`__init__.py`, `__version__`).
- `tests/` — pytest suite (`test_import.py` smoke test passes).

## Author's Python-repo conventions (learned from linetools & XAI)

- Package layout: `<pkg>/` for source, `tests/` for `test_*.py`, metadata in
  `setup.cfg` under `[metadata]`/`[options]`, `pyproject.toml` build-system only.
- BSD-3 license; author `J. Xavier Prochaska`. Plotting via matplotlib.
- **Reference project:** `Projects/XAI` is the closest sibling — a Claude-driven
  *webpage dashboard to monitor all Claude-based projects* (matches night-planner's
  stated dashboard goal). Its `.claude/settings.json` (WebSearch/WebFetch allow +
  the `log_usage.py` Stop hook) is identical to ClimateIntelligence's and is the
  one to copy here (already in place from start-up prompt 1).
- Note: the prompt referenced `Oceanography/python`, which does not exist on disk;
  `papers/Oceanography/*` holds paper *analysis* dirs, not packaged repos. Used the
  author's actual Python repos (linetools, XAI, ClimateIntelligence) instead.

## Astronomy / night-planning knowledge

- _(To be filled in as I learn the telescope, instruments, targets, and the
  astronomers' night-planning workflow.)_

## Version History

- **v0.1 — 2026-07-11:** Created during start-up prompt 1. Seeded project purpose,
  working conventions, and repository layout. Astronomy/night-planning knowledge
  section is a placeholder pending the astronomers' input.
- **v0.2 — 2026-07-11:** Start-up prompt 2 ("Basic start up"). Added Python
  packaging scaffolding (setup.py/setup.cfg/pyproject.toml, requirements.txt,
  `night_planner/` package, `tests/`) following the author's linetools/XAI
  convention. Recorded those conventions and the settings.json recommendation
  (copy XAI's — already in place). Chose astronomy deps: numpy, astropy,
  **astroplan** (observability/scheduling), matplotlib, pyyaml.
- **v0.3 — 2026-07-11:** Start-up prompt 3 (1st task under "Skills"). Copied the
  `grill-me` and `critical-partner` skills verbatim from ClimateIntelligence into
  `.claude/skills/` (both single-file SKILL.md, project-agnostic, no edits needed).
