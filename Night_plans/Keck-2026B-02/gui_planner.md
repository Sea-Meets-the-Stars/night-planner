### This doc we will describe the instructions for the night plan viewer

We need a home page where we can choose the instrument slash/telescope and the date of Observetion

This should take us to a page where we can then load our table of of targets and other params and constraints as it pertains to the instrument. In this page we can then have a generate plan button which will take us to the plan viewing page

The plan viewer page should show us the night plan in full as well as highlighting the our idle time, our sunset,12 degree and 18 degree dusk and dawns, sunrise blocke out times If any. It should also have an export button which makes a zip file with all of the files we need as in this Resource directory and we could name it anything.

Other pages 

- showing the reasoning for which we accepted and or rejected each targets from the original target list

- individual Finder charts

- The starlist

- Airmass through out the night for individual targets


#### Important note for the night plan in general, Yes we use FFFF-PZ most of the time, but I want to be able to start from any table of targets to make a night plan

---

## Implementation plan (Claude's recommendations, 2026-10-06)

Researched how the author's two sibling web UIs are actually built before
proposing a stack, rather than guessing:

- **chime-reduce-ui** (Flask): exists to launch/stream long-running PypeIt
  subprocess jobs — `JobManager` + Server-Sent Events, plots are externally
  generated PNGs served via `send_file()`.
- **frb-viewer** (FastAPI): a pure *viewer* over pre-built JSON/CSV data,
  Plotly.js for interactive charts, a path-traversal-guarded `/api/image`
  endpoint for static PNGs, HTTP Basic auth, paginated APIs.

Both avoid any frontend framework or CSS framework entirely — plain
HTML/CSS/vanilla JS in both cases.

### Stack: FastAPI + vanilla JS/HTML + Plotly.js (frb-viewer's shape, not chime-reduce-ui's)

night-planner's GUI is a viewer-with-one-action (pick inputs -> generate ->
view) — `calc`+`build` finish in seconds, not minutes — so it matches
frb-viewer, not chime-reduce-ui's job-manager/SSE machinery. `calc`/`build`
run synchronously, in-process, directly from the request handler.

**Layout:** `backend/app.py` (FastAPI) + `frontend/` (HTML/CSS/vanilla JS,
Plotly.js via CDN) as repo-root siblings, exactly like frb-viewer — not
nested under the `night_planner/` package. Launched via a new
**`night-planner serve`** subcommand on the CLI already built (one binary
name, rather than a second console-script like frb-viewer's own).

### Pages -> routes

| Spec'd page | Route | Notes |
|---|---|---|
| Home (instrument + date) | `GET /` | Instrument choices come from the existing `INSTRUMENTS` registry in `night_planner/cli.py` — no new source of truth |
| Setup (load targets + params, Generate) | `GET /setup` | Upload a CSV or point at one already on disk; edit a `NightPlanConfig` form (max_targets, start_override, blocks) |
| Plan viewer | `GET /plan` | Timeline + idle time + sunset/12deg/18deg twilight + sunrise + blocked windows; Export button |
| Rejection reasoning | `GET /rejections` | Table view of accept/reject per target, per stage |
| Finder charts | `GET /finders` | Grid, served via a path-traversal-guarded `/api/image` endpoint (frb-viewer already has this exact pattern) |
| Starlist | `GET /starlist` | Raw text + download |
| Airmass through the night | `GET /airmass?target=TNS` | Plotly line chart, computed on demand, not pre-stored |

`POST /api/generate` runs calc+build in-process and returns the output
directory; the frontend redirects to `/plan?output_dir=...`.
`GET /api/export?output_dir=...&name=...` zips that whole directory and
streams it back under whatever filename the user types.

### Two decisions made (2026-10-06)

1. **Column mapping for "any table of targets":** auto-detect common
   column-name variants (RA/ra/RA_deg/Pri_RA, Dec/DEC/Pri_Dec,
   mag/Pri_mag/mag_r, TNS/Name/ID) and only prompt for manual mapping when
   detection is ambiguous or a required column is missing — not a mapping
   step on every upload.
2. **Common per-instrument adapter built first**, before any GUI code.
   Keck and Lick's scheduling code don't share a function shape today
   (`analyze_targets`/`select_targets_for_night` vs. `analyze`/
   `schedule_greedy`'s two-tier FRB/spare split) — the GUI should never
   special-case instruments, so the adapter lands before Phase 2.

### Phased build

- **Phase 0 - common adapter.** New `night_planner/plan_result.py`
  (`PlanResult`: targets w/ accept-reject-reason, schedule, twilight
  [extended to sunset/sunrise, nautical +-12deg, astronomical +-18deg, not
  just +-18deg], blocks, meta). Each instrument module gets a
  `to_plan_result(...)` adapter — no rewrite of either scheduler's actual
  logic. Lick gets a structured (CSV/JSON) rejection output to match
  Keck's `keck_2026oct06_rejection_analysis.py`. `night_planner/cli.py`'s
  `INSTRUMENTS` registry gains a `plan_result` entry per instrument.
- **Phase 1 - target-table ingestion.** New `night_planner/targets_io.py`:
  auto-detect + normalize to one canonical schema at ingestion, so
  instrument code only ever sees canonical columns from then on (not two
  schemas threaded through every function). Ambiguous/missing columns
  return a structured "needs mapping" result instead of guessing.
- **Phase 2 - backend.** `backend/app.py` with the routes above, plus
  `/api/generate`, `/api/export`, `/api/image`, `/api/airmass/{tns}`
  (on-demand sampled curve via the existing `calculate_airmass()`). New
  `night-planner serve` subcommand launches uvicorn.
- **Phase 3 - frontend.** `frontend/` vanilla HTML/JS + Plotly.js via CDN.
  Home -> Setup (upload/pick targets + edit config + Generate) -> Plan
  viewer (timeline, twilight/idle/block shading, Export) -> Rejections /
  Finders / Starlist / Airmass as linked sub-views.
- **Phase 4 - zip export + polish.** Name-your-own-download export,
  minimal CSS pass.



### Notes
1. Can you take in weather forecast and make different version
2. Night is photometric, emphasize brighter targets or changes
3. Make it into a assistance instead of a tool. Connect into agentic mode
4. Interact with telescope software like uploading starlists e.t.c