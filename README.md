# night-planner

Automated night plan generation for professional telescope observations.

Created by J. Xavier Prochaska and Claude

---

## Overview

**night-planner** generates optimized observing schedules for CHIME/FRB host galaxy spectroscopy at Lick Observatory (Shane 3m + Kast spectrograph). The system handles:

- **Ephemeris calculations** (twilight times, LST, airmass)
- **Telescope constraints** (Dec limits, hour angle limits)
- **Target selection** (observable window, magnitude-based priorities)
- **Timeline generation** (Excel night plans with slews, exposures, calibrations)
- **Seasonal RA windows** (time-dependent observability)

---

## Quick Start

### Generate a Night Plan

```bash
# 1. Create FFFF-PZ Resource and pull targets
chime_ffff_pz_add_furesource Night_plans/Lick-2026B-01/Lick-2026B-01.json
chime_ffff_pz_targets Lick-2026B-01

# 2. Calculate observability
python scripts/lick_2026b01_calculations.py

# 3. Build Excel night plan
python scripts/build_night_plan.py
```

Output: `Night_plans/Lick-2026B-01/Lick_2026B-01_Night_plan.xlsx`

### Run Tests

```bash
# Generate 17 edge case test datasets
python tests/test_data/generate_test_frbs.py

# Run full test suite
python tests/test_data/run_all_tests.py

# View results
cat tests/test_data/TEST_RESULTS_SUMMARY.md
```

---

## Documentation

### 📖 Getting Started

- **[Documentation Index](docs/README.md)** - Complete documentation overview
- **[Shane Telescope Constraints](docs/Shane_telescope_constraints.md)** - HA limits, observable RA windows
- **[Testing Guide](docs/Testing_guide.md)** - Edge case validation, bug reports

### 📝 Examples

- **[Lick-2026B-01 HOWTO](Night_plans/Lick-2026B-01/HOWTO_night_plan_creation.md)** - Complete worked example (Aug 13-14, 2026)
- **[Corrections Summary](Night_plans/Lick-2026B-01/CORRECTIONS_SUMMARY.md)** - Critical HA limit corrections

### 🧪 Testing

- **[Test Results Summary](tests/test_data/TEST_RESULTS_SUMMARY.md)** - 17 edge cases, bugs found, deadtime analysis
- **[Test Suite README](tests/README.md)** - How to run tests

---

## Key Features

### ✅ Accurate Ephemeris

- 18° astronomical twilight calculations
- LST verified to 10-20 sec precision against Lick calendar
- PST (UTC-8) year-round convention
- Airmass tracking throughout night

### ✅ Shane 3m Constraints

**Correctly implements:**
1. **Dec ≤ +82°** (polar limit)
2. **HA: -5h ≤ HA ≤ +3.75h** (symmetric limits)
3. **NO RA limits** (observable RAs depend on LST and season)

**Key insight:** Observable RA window shifts ~2h/month as Earth orbits sun.

### ✅ Deadtime Analysis

Detects gaps when no targets are observable:
```bash
python scripts/check_deadtime_lick_2026b01.py
```

**Lick-2026B-01 result:** NO deadtime - targets flow continuously 20:30→04:12 PST.

### ✅ Comprehensive Testing

17 synthetic test cases covering:
- Seasonal variations (Aug, Feb, Mar)
- HA limit boundaries
- Zero/one observable targets
- Dense vs sparse fields
- Extreme declinations

**Status:** 9/17 passing, 8/17 exposing known bugs (documented for fixing)

---

## Repository Structure

```
night-planner/
├── docs/                          # 📖 Documentation
│   ├── README.md                 # Documentation index
│   ├── Shane_telescope_constraints.md
│   └── Testing_guide.md
├── Night_plans/                   # 📅 Observing plans
│   └── Lick-2026B-01/            # Aug 13-14, 2026
│       ├── HOWTO_night_plan_creation.md
│       ├── CORRECTIONS_SUMMARY.md
│       ├── Lick_2026B-01_Night_plan.xlsx
│       └── [target CSVs, analysis]
├── scripts/                       # 🔧 Calculation scripts
│   ├── lick_2026b01_calculations.py    # Ephemeris & target selection
│   ├── build_night_plan.py             # Excel generation
│   ├── observable_ra_calculator.py     # RA windows by date
│   └── check_deadtime_lick_2026b01.py  # Timeline analysis
├── tests/                         # 🧪 Test suite
│   ├── README.md
│   └── test_data/
│       ├── generate_test_frbs.py       # Generate 17 test cases
│       ├── run_all_tests.py            # Run all tests
│       ├── TEST_RESULTS_SUMMARY.md     # Results analysis
│       ├── test_*.csv                  # 17 synthetic datasets
│       └── results/                    # Test outputs
├── context/                       # 🧠 Claude's memory
│   ├── claudes_brain.md          # Persistent knowledge
│   └── claudes_context.md        # Detailed reference
├── Logs/                          # 📔 Session logs
├── night_planner/                 # 📦 Python package
├── claude_prompts/               # Initial setup
└── README.md                      # This file
```

---

## Scripts

| Script | Purpose |
|--------|---------|
| `lick_2026b01_calculations.py` | Calculate ephemeris, apply constraints, select targets |
| `build_night_plan.py` | Generate Excel night plan with timeline |
| `observable_ra_calculator.py` | Show observable RAs for any date + year plot |
| `check_deadtime_lick_2026b01.py` | Analyze timeline for gaps |
| `generate_test_frbs.py` | Create 17 synthetic edge case datasets |
| `run_all_tests.py` | Run observability on all test cases |

---

## Known Issues

### Bugs Found by Testing (8 edge cases)

**Status:** Documented, awaiting fixes

1. **NoneType comparison** when targets never observable (6 tests)
   - Targets never enter HA window → `min_am_time = None` → sorting crashes
   - **Fix:** Set sentinel value or filter None before sorting

2. **Empty DataFrame** when all targets rejected (2 tests)
   - All Dec > 82° → empty result → code continues → KeyError
   - **Fix:** Early return when zero targets pass filters

See [`tests/test_data/TEST_RESULTS_SUMMARY.md`](tests/test_data/TEST_RESULTS_SUMMARY.md) for details.

---

## Important Lessons

### 1. Always Verify Telescope Limits

Initial implementation had **wrong constraints** (RA ≥ 5h, HA ≥ -3.75h west only). This led to selecting 4 targets that violated real limits!

**Correct Shane limits:**
- Dec ≤ 82°
- **Symmetric HA:** -5h ≤ HA ≤ +3.75h
- **NO RA limits**

### 2. Timezone Matters

Lick calendar uses **PST (UTC-8) year-round**, not DST-aware PDT. This affects LST calculations.

```python
PST = timezone(timedelta(hours=-8))  # Fixed offset ✓
# NOT: pytz.timezone('America/Los_Angeles')  # DST-aware ✗
```

### 3. Cross-Check Authoritative Sources

Verify against [Lick calendar](https://www.ucolick.org/calendar/lickcal2021-30/):
- Twilight times: ±2-3 min
- LST: ±10-20 sec

---

## Example: Lick-2026B-01 (Aug 13-14, 2026)

**Night:** Aug 13-14, 2026 (7.1h dark)
**Targets:** 6 CHIME/FRB hosts (2 evening RA 15-16h, 4 morning RA 0-5h)
**Timeline:** 20:30→04:12 PST (NO deadtime)
**Total observing:** 420 min (7.0h science + 0.7h overhead)

### Selected Targets

| Target | RA (h) | r-mag | Exposure | Window |
|--------|--------|-------|----------|--------|
| FRB20230729A | 15.74 | 18.44 | 80 min | Evening |
| FRB20200621B | 15.45 | 16.87 | 60 min | Evening |
| FRB20200702C | 0.55 | 15.98 | 60 min | Morning |
| FRB20250902A | 1.62 | 18.57 | 80 min | Morning |
| FRB20230805A | 2.40 | 17.99 | 80 min | Morning |
| FRB20231223B | 5.25 | 16.27 | 60 min | Morning |

**Rejected:** 6 targets at RA 9-13h (always HA > +3.75h, too far west)

See [`Night_plans/Lick-2026B-01/HOWTO_night_plan_creation.md`](Night_plans/Lick-2026B-01/HOWTO_night_plan_creation.md) for complete step-by-step guide.

---

## Installation

```bash
# Clone repo
cd /home/lordrick/Projects/night-planner

# Install dependencies (minimal - uses astropy)
pip install -r requirements.txt

# Or install as package
pip install -e .
```

**Dependencies:**
- numpy
- pandas
- astropy
- matplotlib
- openpyxl (for Excel generation)

---

## Development

### Adding a New Observatory

1. Update coordinates in calculation script
2. Update HA limits (telescope-specific)
3. Verify timezone convention
4. Cross-check against observatory calendar
5. Generate test cases for new site

### Adding a New Instrument

1. Update exposure time scaling rules
2. Add instrument setup notes
3. Update Excel template structure
4. Document in HOWTO

---

## References

- **Lick Observatory Calendar:** https://www.ucolick.org/calendar/
- **CHIME/FRB FFFF-PZ:** https://frb.chimenet.ca/f4pz/
- **Astropy Documentation:** https://docs.astropy.org/

---

## License

BSD-3-Clause

## Authors

- J. Xavier Prochaska (jxp@ucsc.edu)
- Claude (Anthropic)

---

## Getting Help

1. Read [`docs/README.md`](docs/README.md) for documentation index
2. Check [`Night_plans/Lick-2026B-01/HOWTO_night_plan_creation.md`](Night_plans/Lick-2026B-01/HOWTO_night_plan_creation.md) for worked example
3. Review [`tests/test_data/TEST_RESULTS_SUMMARY.md`](tests/test_data/TEST_RESULTS_SUMMARY.md) for edge cases
4. Consult [`context/claudes_brain.md`](context/claudes_brain.md) for accumulated knowledge
