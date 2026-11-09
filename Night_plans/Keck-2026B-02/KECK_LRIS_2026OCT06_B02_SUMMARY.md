# Keck/LRIS Oct 6, 2026 — plan from the Keck-2026B-02 pull

_Updated 2026-10-01: FRB20260603D moved from MOS to longslit; finders and target list added._

Created by JXP and Claude

This replaces the plan in `Night_plans/Keck-2026B-01/`, which is kept as the
earlier record. See `../Keck-2026B-01/KECK_LRIS_2026OCT06_SUMMARY.md` for the
full history up to Prompt 14.

## Why a new pull

The B-01 plan had a 152-min gap (22:37-01:09 HST) because it ran out of
targets. B-01 exists only on the local docker FFFF-PZ, and the author says
that name is taken on global. So a new Resource, **Keck-2026B-02**, was added
to the global FFFF-PZ server (`https://frb.chimenet.ca/f4pz/`) on 2026-09-30.
Its settings: LRIS, 10 mask + 20 longslit, min_mag 19, max AM 2.0, window
2026-10-07T05:00:01Z-15:45:38Z (the Oct 6 HST night). It returned 20
targets, 9 of them shared with B-01.

## Rules used

| Rule | Value | Where |
|------|-------|-------|
| Keck base slew | 10 min | `scripts/keck_overheads.py` |
| Slew from Dec < +20 to Dec > +20 | 20 min | `scripts/keck_overheads.py` |
| MOS block | 60/90/120 min (incl. mask alignment) + 5 min buffer | `estimate_mos_exposure()` |
| Masks allowed | 5 B-01 MOS candidates (3 scheduled) | `MOS_MASKS_AVAILABLE` |
| FRB20260603D | no mask will be milled → **longslit 3×1200 s** (S/N/exp blue 5.7, red 2.8) | `LONGSLIT_FORCED` |
| Longslit exposure | real LRIS ETC, S/N 10 per exposure, 3 exposures | `scripts/lris_etc.py` |

## Timeline (HST)

```
19:10  Flux standard (BD28d4211)                 5
19:15  Focus check                               5
19:29  slew -> FRB20260518B  longslit           10 + 14
19:53  slew -> FRB20260611G  longslit           10 + 30
20:33  slew -> FRB20260502A  MOS (existing)     10 + 65
21:48  slew -> FRB20260708D  longslit           10 + 24
22:22  slew -> FRB20260603D  LONGSLIT 3x1200    10 + 60   (no mask; low S/N)
23:32  slew -> FRB20260831H  longslit           10 + 18
00:00  slew -> FRB20260102A  MOS (existing)     10 + 65
01:15  slew -> FRB20260418B  longslit           20 + 19   (Dec +13.9 -> +39.4)
01:54  [idle]                                   15
02:09  slew -> FRB20240106A  MOS (existing)     10 + 65
03:24  slew -> Feige110                         10
03:34  Flux standard (Feige110)                  5
03:39  Arcs + flats                             20
03:59  END   (18° dawn 05:02)
```

## Utilization

| Metric | Value |
|--------|-------|
| Targets | 9 (3 MOS, 6 longslit) |
| On target | 6.0 h |
| Slews | 100 min |
| Idle between targets | 15 min |
| On target / dark time | 62% |

## Open items

- **FRB20260603D (mag 22.6) is observed in longslit** because no mask will
  be milled (author, 2026-10-01). S/N=10 per exposure would need more than
  3×7200 s, so it keeps a 1 h block as 3×1200 s: per-exposure S/N is about
  5.7 blue / 2.8 red, or about 9.9 / 4.9 combined. That is enough for an
  emission-line redshift, not for absorption lines. Align the slit on its
  offset star (see its finder).
- **The CHIME repeater FRB20250408A is not scheduled.** The earlier
  longslit targets use up its window, leaving 7 min when it needs 53 + 10.
  The scheduler takes targets in order of window start and has no priority
  input.
- New MOS targets excluded for lack of a mask: FRB20230702A, FRB20260427A,
  FRB20260702A, FRB20260829B.
- 03:59-05:02 before dawn is unused.

Per-target reasons: `target_rejection_analysis.md`.

## Observing files (2026-10-01)

| File | What |
|------|------|
| `Keck-2026B-02.starlist` | **Use this one.** Rows from `chime_ffff_pz_finder` + `chime_ffff_pz_starlist keck`, in schedule order, with offset stars (`_S`, raoffset/decoffset), slit PA (`rotdest`) and both flux standards |
| `Keck-2026B-02_target_list.md` | One row per target: time, coordinates, mode, exposure, PA, offset star, finder link |
| `finders/*.png` | Finder charts (copies; originals in `chime-ffff-pz/.../Observing/Keck-2026B-02/`) |
| `keck_lris_oct06.starlist` | Coordinates-only list written by the scheduler; no offsets or PA. Superseded by the one above |
| `Keck_LRIS_2026Oct06_Night_plan.xlsx` | Timeline |
| `target_rejection_analysis.md`, `filler_candidates.csv` | Why each target is in or out, and the filler search |

For the 3 MOS targets, `rotdest` is the longslit default from the finder
script. The mask design sets the real PA.

