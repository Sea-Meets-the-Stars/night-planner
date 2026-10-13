# FFFF-PZ Query Results for Lick-2026B-1

**Created by JXP and Claude**
**Date:** 2026-08-14

## Query Process

1. Created `Lick-2026B-1.json` resource file
2. Added to FFFF-PZ database: `chime_ffff_pz_add_furesource`
3. Queried targets: `chime_ffff_pz_targets Lick-2026B-1`

## FFFF-PZ Selected Targets (4 total)

| TNS | RA | Dec | Pri_mag | P_Ox | Tags | Observable? |
|-----|-----|-----|---------|------|------|------------|
| FRB20231223B | 5.25h | 48.8° | 16.27 | 0.918 | Repeater | ✓ Yes |
| FRB20250515A | 2.86h | 8.0° | 18.75 | 0.984 | Unbiased,Lowz | ✓ Yes |
| FRB20250102C | 6.93h | 84.1° | 13.32 | 0.971 | Blind | ✗ No (RA > 6.80h) |
| FRB20251003A | 10.07h | 84.7° | 16.37 | 0.946 | Unbiased,Lowz | ✗ No (RA 10h not in 13.28h-6.80h) |

**Observable RA range for 2026-08-13 night:** 13.28h to 6.80h (wraps around 0h)

## Problem: Only 2 of 4 targets observable!

FFFF-PZ selection criteria didn't account for:
1. **HA pointing limits** (-5.0h to +3.75h)
2. **Observable RA window** for specific night

**Result:** FRB20250102C and FRB20251003A NOT observable during 2026-08-13 night.

## Comparison to Original Night Plan

### Original 6 targets (from night plan):

| TNS | RA | P_Ux | Mag | In FFFF-PZ? |
|-----|-----|------|-----|-------------|
| FRB20200702C | 0.55h | 0.003 | 15.98 | ✗ No |
| FRB20230805A | 2.40h | 0.105 | 17.99 | ✗ No |
| FRB20250902A | 1.62h | 0.003 | 18.57 | ✗ No |
| FRB20231223B | 5.25h | 0.035 | 16.27 | ✓ Yes |
| FRB20230729A | 15.74h | 0.016 | 18.44 | ✗ No |
| FRB20200621B | 15.45h | 0.067 | 16.87 | ✗ No |

**Only 1 target overlaps** between original plan and FFFF-PZ query!

## Key Differences

### FFFF-PZ uses P_Ox (probability of association)
- All 4 targets have P_Ox > 0.9 (high confidence host ID)
- Focuses on well-identified hosts

### Original plan uses P_Ux (probability hostless)
- All 6 targets have P_Ux < 0.11 (low probability hostless = has host)
- 3 targets have P_Ux < 0.01 (excellent host ID)

**Both criteria select targets with identified hosts, just different metrics!**

## Recommendation

**Stick with original 6 targets:**

1. ✓ All 6 have identified hosts (low P_Ux)
2. ✓ All 6 within observable RA range for night
3. ✓ Already have 5 finder charts + starlist
4. ✓ HA-corrected windows calculated

**FFFF-PZ query issues:**
- Only 2 of 4 targets actually observable
- Doesn't filter by HA/RA constraints for specific night
- Missing 5 excellent targets from original plan

## Files

- `Lick-2026B-1_targets.csv`: FFFF-PZ query results (4 targets)
- `Lick-2026B-1.json`: Resource definition in FFFF-PZ database
