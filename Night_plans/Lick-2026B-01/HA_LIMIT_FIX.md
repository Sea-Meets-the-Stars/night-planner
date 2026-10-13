# HA Limit Fix for Lick-2026B-01

**Created by JXP and Claude**

## Problem

Original night plan violated Shane telescope HA pointing limits:
- **Limit**: -5.0h ≤ HA ≤ +3.75h
- **Violations**: All 6 targets had start/end HA values beyond limits

## Corrected Observable Windows

Night: 2026-08-13/14, 20:38 PDT to 05:23 PDT (525 min = 8.8 hours)

### Evening Targets (Setting in West)

| Target | Original Window | HA-Corrected Window | Duration | HA Range |
|--------|----------------|---------------------|----------|----------|
| FRB20230729A | 20:38-05:23* | **20:38-23:05** | 147 min | 1.29h → 3.75h |
| FRB20200621B | 20:38-05:23* | **20:38-22:48** | 130 min | 1.58h → 3.75h |

*Original end HA = +9.4h to +9.7h (beyond +3.75h limit)

### Morning Targets (Rising in East)

| Target | Original Window | HA-Corrected Window | Duration | HA Range |
|--------|----------------|---------------------|----------|----------|
| FRB20200702C | 20:38*-05:23 | **23:08-05:23** | 374 min | -5.0h → +1.25h |
| FRB20250902A | 20:38*-05:23 | **00:12-05:23** | 310 min | -5.0h → +0.18h |
| FRB20230805A | 20:38*-05:23 | **00:59-05:23** | 263 min | -5.0h → -0.60h |
| FRB20231223B | 20:38*-05:23 | **03:49-05:23** | 93 min | -5.0h → -3.44h |

*Original start HA = -6.5h to -12.2h (beyond -5.0h limit)

## Key Findings

1. **Evening targets**: Must end by 22:48-23:05 (when HA reaches +3.75h)
   - Both targets overlap → **can only observe ONE**
   - FRB20230729A has longer window (147 min)

2. **Morning targets**: Start times staggered as HA crosses -5.0h
   - FRB20200702C available first (23:08)
   - FRB20231223B available last (03:49)
   - Total window time (1041 min) >> night duration (525 min)
   - Targets overlap heavily → **cannot observe all 4 fully**

3. **Original plan assumption**: All targets observable 20:38-05:23
   - **Violated HA limits** for all targets
   - Evening targets set beyond +3.75h
   - Morning targets rose before -5.0h

## Recommended Schedule (70 min/target)

**Evening** (choose ONE):
- 20:38-21:48: FRB20230729A (mag 18.4) OR
- 20:38-21:48: FRB20200621B (mag 16.9, brighter)

**Late evening → Morning** (choose ~3):
- 23:08-00:18: FRB20200702C (mag 16.0, brightest)
- 00:59-02:09: FRB20230805A (mag 18.0)
- 03:49-05:00: FRB20231223B (mag 16.3) - only 70 min available!

**Alternative**: Split time among all 4 morning targets (shorter exposures)

## Files

- `selected_targets_ha_corrected.csv`: Corrected observable windows
- `scripts/fix_ha_limits.py`: Python script that calculated corrections
- `lick.starlist`: Lick telescope starlist (5 targets, missing FRB20231223B)
- `finder_charts/`: Finder charts (5 targets, missing FRB20231223B)

## Next Steps

1. **Decide target priority**: Cannot observe all 6 targets for 70 min each
2. **Update night plan**: Use corrected start/end times from CSV
3. **Generate missing finder**: FRB20231223B (requires FFFF-PZ API)
4. **Regenerate starlist**: After FRB20231223B finder created
