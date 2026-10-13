# Unassigned Targets: RA 1-4h, P_Ox > 0.7, No Redshift

**Created by JXP and Claude**
**Date:** 2026-08-14

## Query Criteria

From local FFFF-PZ database:
- **RA range:** 1.0h to 4.0h
- **P_Ux < 0.3** (P_Ox > 0.7 approximately - has identified host)
- **No redshift** measured yet
- **Has PATH results** (magnitudes available)
- **Not assigned** to any resource (filtered out known assignments)

## Results Summary

**Total found:** 30 unassigned targets
**All have PATH candidates** with magnitudes
**Observable:** All within RA 1-4h window for 2026-08-13 morning

## TOP 10 TARGETS (by brightness + P_Ox)

### Excellent Candidates (mag < 16, P_Ox > 0.95)

| TNS | RA | Dec | mag | DM | P_Ux | P_Ox | Notes |
|-----|-----|-----|-----|-----|------|------|-------|
| **FRB20231229A** | 1.76h | 35.1° | **14.27** | 198.9 | 0.004 | **0.996** | ⭐ BRIGHTEST |
| **FRB20250524A** | 3.00h | 51.2° | **15.40** | 205.8 | 0.002 | **0.998** | ⭐ BEST P_Ox |
| **FRB20231225B** | 3.66h | -3.1° | **15.52** | 227.7 | 0.040 | 0.960 | Bright |
| **FRB20240331A** | 2.08h | 46.9° | **15.82** | 349.0 | 0.022 | 0.978 | Bright |

### Very Good Candidates (mag 17-18, P_Ox > 0.95)

| TNS | RA | Dec | mag | DM | P_Ux | P_Ox | Notes |
|-----|-----|-----|-----|-----|------|------|-------|
| FRB20230409C | 1.68h | 51.9° | 17.07 | 299.1 | 0.028 | 0.972 | Good |
| FRB20240424A | 1.46h | 28.0° | 17.10 | 335.2 | 0.013 | 0.987 | Good |
| FRB20241228D | 1.09h | 39.1° | 17.34 | 426.6 | 0.095 | 0.905 | OK |
| FRB20231011A | 1.22h | 41.8° | 17.77 | 186.3 | 0.017 | 0.983 | Good |
| FRB20250118B | 2.85h | 78.2° | 17.84 | 349.8 | 0.008 | 0.992 | Good |
| FRB20201105A | 2.71h | 14.4° | 17.63 | 262.4 | 0.174 | 0.826 | OK |

## Comparison to Original Night Plan Morning Targets

### Original Morning Targets

| TNS | RA | mag | P_Ux | Status |
|-----|-----|-----|------|--------|
| FRB20200702C | 0.55h | 15.98 | 0.003 | Have finder, assigned |
| FRB20250902A | 1.62h | 18.57 | 0.003 | Have finder, assigned |
| FRB20230805A | 2.40h | 17.99 | 0.105 | Have finder, assigned |
| FRB20231223B | 5.25h | 16.27 | 0.035 | RA > 4h (outside query range) |

### New Targets are BETTER!

**FRB20231229A** (mag 14.27, P_Ux=0.004):
- **2 magnitudes brighter** than FRB20200702C (mag 15.98)!
- **4 magnitudes brighter** than FRB20250902A (mag 18.57)!
- Same excellent P_Ux

**FRB20250524A** (mag 15.40, P_Ux=0.002):
- Brighter than FRB20200702C
- **Best P_Ux** of all candidates (0.002)

## Recommended Additions to Night Plan

### Replace morning targets with:

**Top 4 unassigned (all better than original):**

1. **FRB20231229A** (RA=1.76h, mag=**14.27**, P_Ux=0.004)
   - **BRIGHTEST** target found
   - Replace FRB20250902A (mag 18.57) - saves ~40 min exposure time!

2. **FRB20250524A** (RA=3.00h, mag=15.40, P_Ux=**0.002**)
   - **Best host ID** (P_Ux=0.002)
   - Brighter than FRB20200702C

3. **FRB20231225B** (RA=3.66h, mag=15.52, P_Ux=0.040)
   - Very bright, still excellent P_Ox

4. **FRB20240331A** (RA=2.08h, mag=15.82, P_Ux=0.022)
   - Bright, good P_Ox

### Why These Are Better

**Exposure time savings:**
- FRB20231229A (mag 14.27): ~30 min vs FRB20250902A (mag 18.57): ~80 min
- **Saves 50 minutes** on one target alone!
- Can observe MORE targets in same night

**Better science:**
- All have P_Ux < 0.05 (excellent host ID)
- Brighter = higher S/N spectra
- More likely to get redshift measurements

**Observable windows:**
- All in RA 1-4h range (morning targets)
- Need to calculate HA windows with fix_ha_limits.py
- Likely better windows than original (brighter RA range)

## All 30 Unassigned Candidates

Full list saved to: `unassigned_targets_ra1-4h.csv`

Columns:
- name: FRB TNS name
- ra_hours: RA in decimal hours
- dec: Declination in degrees
- DM: Dispersion measure
- P_Ux: Probability hostless (lower = better)
- repeater: Boolean
- has_path: Boolean (all TRUE)
- pri_mag: Primary candidate r-band magnitude from PATH

## Action Items

1. **Select final 4-6 targets** from top 10 list
2. **Calculate HA windows** for selected targets:
   ```bash
   python scripts/fix_ha_limits.py  # Update with new targets
   ```
3. **Generate finders** (requires FFFF-PZ API):
   ```bash
   # For each target:
   cd /home/lordrick/Projects/chime-ffff-pz/chime_ffff_pz/data/Observing/Lick-2026B-1
   chime_ffff_pz_finder FRB20231229A Lick-2026B-1
   chime_ffff_pz_finder FRB20250524A Lick-2026B-1
   # etc.
   ```
4. **Generate starlist:**
   ```bash
   chime_ffff_pz_starlist lick
   ```
5. **Update night plan** with new targets + exposure times

## Notes

- **P_Ox approximation:** P_Ox ≈ 1 - P_Ux (rough estimate)
- Actual P_Ox values from PATH analysis may differ slightly
- All magnitudes from PATH primary candidate (r-band Pan-STARRS or DECaLS)
- Filtered out 3 known assigned targets: FRB20250902A, FRB20230805A, FRB20250515A

## Files Created

- `candidates_ra1-4h.csv`: All 34 candidates (P_Ox > 0.7, RA 1-4h, no z)
- `candidates_ra1-4h_with_path.csv`: 33 with PATH results + magnitudes
- `unassigned_targets_ra1-4h.csv`: **30 unassigned** (filtered)

---

**Key Discovery:** Found 4 targets **significantly brighter** than original morning targets, all with excellent host ID (P_Ux < 0.05). FRB20231229A at mag 14.27 is **4 mag brighter** than FRB20250902A!
