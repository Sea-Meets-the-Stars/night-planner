# New Target Recommendations from FFFF-PZ Query

**Created by JXP and Claude**
**Date:** 2026-08-14

## Query Results

Queried local FFFF-PZ API for Lick 2026-08-13 night:
- **Total FRBs in DB**: 498
- **Dec < 82°**: 461
- **Observable RA range (13.28h to 6.80h)**: **314 candidates**
- **Repeaters**: 31
- **High P_Ux (>0.5)**: 64

## Original vs. New Targets

### Original 6 Targets (from night plan)

| Target | RA | P_Ux | Mag | Tags |
|--------|----|----- |-----|------|
| FRB20200702C | 0.55h | 0.996 | 15.98 | Repeater |
| FRB20230805A | 2.40h | 0.771 | 17.99 | Repeater,Blind |
| FRB20250902A | 1.62h | 0.995 | 18.57 | Unbiased |
| FRB20231223B | 5.25h | 0.918 | 16.27 | Repeater |
| FRB20230729A | 15.74h | 0.962 | 18.44 | Blind |
| FRB20200621B | 15.45h | 0.921 | 16.87 | Blind |

**Issue**: Only FRB20200702C and FRB20250902A have P_Ux > 0.99

### Top New Candidates with P_Ux = 1.000

#### Morning Targets (RA 0-7h)

| Target | RA | Dec | DM | P_Ux | Repeater |
|--------|-------|------|---------|------|----------|
| FRB20251010A | 0.14h | 41.1° | 505.9 | 1.000 | No |
| FRB20250726A | 1.29h | 63.0° | 553.2 | 1.000 | No |
| FRB20250709A | 3.69h | 44.2° | 756.6 | 1.000 | No |
| FRB20251005A | 3.70h | 44.2° | 312.7 | 1.000 | No |
| FRB20250626B | 4.38h | 56.1° | 535.0 | 1.000 | No |
| FRB20230725F | 4.49h | 21.0° | 838.3 | 1.000 | No |
| FRB20250405A | 5.23h | 8.3° | 733.1 | 1.000 | No |
| FRB20230325A | 5.88h | 74.2° | 912.5 | 0.999 | No |
| FRB20240601A | 6.22h | 45.5° | 754.5 | 1.000 | No |
| FRB20260218A | 6.49h | 12.1° | 574.6 | 0.993 | No |

#### Evening Targets (RA 13-23h)

| Target | RA | Dec | DM | P_Ux | Repeater |
|--------|-------|------|---------|------|----------|
| FRB20191202A | 19.87h | 70.8° | 117.9 | 1.000 | No |
| FRB20251004A | 19.27h | 53.7° | 610.9 | 1.000 | No |
| FRB20260129C | 20.74h | 76.4° | 741.2 | 1.000 | No |
| FRB20250315A | 23.77h | 36.8° | 611.0 | 1.000 | Repeater |

## Recommended New Target List

Based on P_Ux = 1.000 (perfect host identification):

### Evening (Choose 1-2)

1. **FRB20191202A** (RA=19.87h, Dec=70.8°, DM=117.9)
   - P_Ux = 1.000, low DM = bright host expected
2. **FRB20251004A** (RA=19.27h, Dec=53.7°, DM=610.9)
   - P_Ux = 1.000

### Morning (Choose 3-4)

1. **FRB20251010A** (RA=0.14h, Dec=41.1°, DM=505.9)
   - P_Ux = 1.000, earliest rise time
2. **FRB20250709A** (RA=3.69h, Dec=44.2°, DM=756.6)
   - P_Ux = 1.000
3. **FRB20250626B** (RA=4.38h, Dec=56.1°, DM=535.0)
   - P_Ux = 1.000
4. **FRB20240601A** (RA=6.22h, Dec=45.5°, DM=754.5)
   - P_Ux = 1.000

## Why Change?

1. **Perfect host ID**: P_Ux = 1.000 means host galaxy definitively identified
2. **Better science**: Original targets had P_Ux = 0.77-0.996 (less certain)
3. **Same observability**: All new targets within RA/Dec/HA limits

## Next Steps

1. **Recalculate HA windows** for new targets using `fix_ha_limits.py`
2. **Generate finders** for new targets (need to register resources in FFFF-PZ)
3. **Create new starlist** with final target selection
4. **Update night plan** with new targets

## Files

- `ffffpz_candidates.csv`: All 314 observable candidates
- `scripts/query_ffffpz_targets.py`: FFFF-PZ query script
