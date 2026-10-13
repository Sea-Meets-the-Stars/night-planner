# hco_batch_jul26.csv Targets vs. Original Night Plan

**Created by JXP and Claude**
**Date:** 2026-08-14

## Query Results

Checked 19 FRBs from `hco_batch_jul26.csv` in local FFFF-PZ DB:
- **All 19 in DB** ✓
- **13 observable** on 2026-08-13 (RA: 13.28h-6.80h)
- **7 have PATH results**
- **3 with P_Ux = 0.000** (perfect host ID!)

## Top New Candidates (with PATH results, P_Ux < 0.1)

### Evening Targets (RA 13-20h)

| TNS | RA | Dec | Pri_mag | P_Ux | POx | Priority |
|-----|-----|-----|---------|------|-----|----------|
| **FRB20260405B** | 13.87h | 48.1° | **15.36** | **0.000** | 1.000 | **⭐ BEST** |
| **FRB20260404D** | 13.59h | 49.6° | 16.93 | **0.000** | 1.000 | **⭐ EXCELLENT** |
| FRB20260330B | 19.51h | 7.1° | 17.63 | 0.078 | 0.546 | Good |
| FRB20260427A | 17.71h | 74.5° | 21.27 | 0.002 | 0.998 | Too faint |

### Morning Target (RA 22-7h)

| TNS | RA | Dec | Pri_mag | P_Ux | POx | Priority |
|-----|-----|-----|---------|------|-----|----------|
| FRB20260406J | 22.11h | 17.4° | 20.72 | **0.000** | 1.000 | Too faint |

## Comparison to Original Night Plan

### Original Evening Targets

| TNS | RA | Mag | P_Ux | Status |
|-----|-----|-----|------|--------|
| FRB20230729A | 15.74h | 18.44 | 0.016 | Have finder |
| FRB20200621B | 15.45h | 16.87 | 0.067 | Have finder |

### Original Morning Targets

| TNS | RA | Mag | P_Ux | Status |
|-----|-----|-----|------|--------|
| FRB20200702C | 0.55h | 15.98 | 0.003 | Have finder |
| FRB20230805A | 2.40h | 17.99 | 0.105 | Have finder |
| FRB20250902A | 1.62h | 18.57 | 0.003 | Have finder |
| FRB20231223B | 5.25h | 16.27 | 0.035 | No finder |

## Recommended Target List (Mix of Original + New)

### Evening (Choose 1-2, 130-147 min each after HA clipping)

**REPLACE with new targets:**
1. **FRB20260405B** (RA=13.87h, mag=**15.36**, P_Ux=**0.000**) ← **BEST NEW**
   - Brighter than both original evening targets
   - Perfect host ID (P_Ux=0.000)
   - Observable 20:38-? (need HA calculation)

2. **FRB20260404D** (RA=13.59h, mag=16.93, P_Ux=**0.000**) ← **EXCELLENT NEW**
   - Better than FRB20230729A (mag 18.44)
   - Perfect host ID

**OR keep original:**
- FRB20200621B (mag=16.87, have finder already)

### Morning (Choose 3-4)

**Keep original morning targets** - all excellent:
1. FRB20200702C (mag=15.98, P_Ux=0.003) - 374 min window
2. FRB20250902A (mag=18.57, P_Ux=0.003) - 310 min window
3. FRB20230805A (mag=17.99, P_Ux=0.105) - 263 min window
4. FRB20231223B (mag=16.27, P_Ux=0.035) - 93 min window

## Action Items

If using new evening targets:

1. **Generate finders** for:
   - FRB20260405B (need to add to resource in FFFF-PZ)
   - FRB20260404D (need to add to resource in FFFF-PZ)

2. **Calculate HA windows** using `fix_ha_limits.py`

3. **Regenerate starlist** with new targets

4. **Update night plan** with final selection

## Summary

**hco_batch_jul26.csv provides 2 BETTER evening targets:**
- Both P_Ux = 0.000 (perfect host ID)
- FRB20260405B mag=15.36 (brightest of all candidates!)
- FRB20260404D mag=16.93 (better than FRB20230729A mag=18.44)

**Original morning targets remain best** - all have excellent P_Ux and PATH results.

**Recommendation:**
- Replace 1-2 original evening targets with FRB20260405B + FRB20260404D
- Keep all 4 original morning targets
- **Final list: 2 new + 4 original = 6 total**
