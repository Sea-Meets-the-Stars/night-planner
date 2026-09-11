"""
Calculate LST, twilight, airmass for Keck/LRIS Oct 2, 2026 night
and select targets for observation.

Created by JXP and Claude
"""

import pandas as pd
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_sun
from astropy.time import Time
from datetime import datetime, timedelta, timezone
import os

from lris_etc import estimate_lris_exposure_real

# Keck Observatory coordinates (Maunakea summit)
# Verified against astropy's EarthLocation.of_site('keck') (IRAF Observatory
# Database), 2026-09-11: lat 19.828333 deg, lon -155.478333 deg, height 4160 m.
KECK = EarthLocation(lat=19.828333*u.deg, lon=-155.478333*u.deg, height=4160*u.m)

# Hawaii Standard Time (UTC-10, no DST)
HST = timezone(timedelta(hours=-10))


def utc_to_hst(utc_time):
    """Convert UTC time to HST (fixed UTC-10)."""
    return utc_time.astimezone(HST)


def hst_to_utc(hst_dt):
    """Convert HST datetime to UTC."""
    if hst_dt.tzinfo is None:
        hst_dt = hst_dt.replace(tzinfo=HST)
    return hst_dt.astimezone(timezone.utc)


def calculate_lst(utc_time, location=KECK):
    """Calculate LST for given UTC time at location."""
    t = Time(utc_time)
    lst = t.sidereal_time('apparent', longitude=location.lon)
    return lst


def find_twilight(date_str, location=KECK, twilight_alt=-18*u.deg):
    """
    Find evening and morning twilight times for given date at Keck.

    Parameters
    ----------
    date_str : str
        Date in format 'YYYY-MM-DD' (HST local date)
    location : EarthLocation
        Observatory location
    twilight_alt : Quantity
        Sun altitude for twilight definition (default -18° for astronomical)

    Returns
    -------
    dict with twilight info
    """
    # Start search at local noon HST
    local_date = datetime.strptime(date_str, '%Y-%m-%d')
    noon_hst = datetime(local_date.year, local_date.month,
                        local_date.day, 12, 0, 0, tzinfo=HST)

    # Search for evening twilight (sun going down)
    search_time = noon_hst
    evening_utc = None
    evening_hst = None
    evening_lst = None

    for i in range(600):  # search up to 10 hours
        utc_time = search_time.astimezone(timezone.utc)
        t = Time(utc_time)
        sun = get_sun(t)
        sun_altaz = sun.transform_to(AltAz(obstime=t, location=location))

        if sun_altaz.alt < twilight_alt:
            evening_utc = utc_time
            evening_hst = search_time
            evening_lst = calculate_lst(utc_time, location)
            break
        search_time += timedelta(minutes=1)

    if evening_hst is None:
        raise ValueError(f"Could not find evening twilight for {date_str}")

    # Search for morning twilight (sun coming up)
    search_time = evening_hst + timedelta(hours=8)  # Oct nights ~11h dark at Keck
    morning_utc = None
    morning_hst = None
    morning_lst = None

    for i in range(600):
        utc_time = search_time.astimezone(timezone.utc)
        t = Time(utc_time)
        sun = get_sun(t)
        sun_altaz = sun.transform_to(AltAz(obstime=t, location=location))

        if sun_altaz.alt > twilight_alt:
            morning_utc = utc_time
            morning_hst = search_time
            morning_lst = calculate_lst(utc_time, location)
            break
        search_time += timedelta(minutes=1)

    if morning_hst is None:
        raise ValueError(f"Could not find morning twilight for {date_str}")

    # Calculate dark time duration
    dark_hours = (morning_utc - evening_utc).total_seconds() / 3600

    return {
        'evening_hst': evening_hst,
        'evening_utc': evening_utc,
        'evening_lst': evening_lst,
        'morning_hst': morning_hst,
        'morning_utc': morning_utc,
        'morning_lst': morning_lst,
        'dark_hours': dark_hours
    }


def calculate_airmass(ra, dec, time_utc, location=KECK):
    """
    Calculate airmass for target at given time.

    Returns
    -------
    airmass : float
    alt : float (degrees)
    az : float (degrees)
    ha : float (hours)
    """
    coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
    t = Time(time_utc)
    altaz = coord.transform_to(AltAz(obstime=t, location=location))

    # Calculate hour angle
    lst = calculate_lst(time_utc, location)
    ha = (lst.hour - ra/15.0) % 24
    if ha > 12:
        ha -= 24

    # Calculate airmass (simple sec(z) formula)
    if altaz.alt.deg > 0:
        airmass = 1.0 / np.sin(np.radians(altaz.alt.deg))
    else:
        airmass = 99.9

    return airmass, altaz.alt.deg, altaz.az.deg, ha


# Keck I Nasmyth-deck vignetting window (fixed in azimuth, independent of target).
# Source: Keck Telescope Pointing Limits,
# www2.keck.hawaii.edu/inst/common/TelLimits.html --
# Keck I: az 5.3-146.2 deg needs alt >= 33.3 deg (deck hit is N/E for Keck I;
# it's S/W for Keck II -- opposite side). Elsewhere the normal unvignetted
# floor is ~18 deg.
KECK1_NASMYTH_AZ_MIN = 5.3
KECK1_NASMYTH_AZ_MAX = 146.2
KECK1_NASMYTH_ALT_MIN = 33.3
KECK1_ALT_MIN = 18.0


def check_keck1_nasmyth_vignetting(az, alt):
    """
    Check whether (az, alt) is clear of the Keck I Nasmyth deck.

    LRIS sits on Keck I, whose enclosure/Nasmyth deck blocks the beam in a
    fixed azimuth band (~5.3-146.2 deg, i.e. N through E to SE) unless the
    telescope is above ~33.3 deg altitude. A target rising in the NE/E sits
    in this band at low altitude and must climb to 33.3 deg before it clears
    the deck -- "wait for the target to rise". A target setting in the W/SW
    passes through the unobstructed side and can be tracked down to the
    normal ~18 deg floor, so setting targets are easier to catch.

    Parameters
    ----------
    az : float (degrees)
    alt : float (degrees)

    Returns
    -------
    clear : bool
    """
    if KECK1_NASMYTH_AZ_MIN <= az <= KECK1_NASMYTH_AZ_MAX:
        return alt >= KECK1_NASMYTH_ALT_MIN
    return alt >= KECK1_ALT_MIN


def check_keck_limits(ra, dec, ha, alt, az):
    """
    Check if target violates Keck I pointing/vignetting limits.

    Keck constraints:
    - Dec > -37° (horizon limit at low dec)
    - HA limits: -5.5h to +5.5h (roughly)
    - Keck I Nasmyth-deck vignetting (see check_keck1_nasmyth_vignetting)

    Parameters
    ----------
    ra : float (degrees)
    dec : float (degrees)
    ha : float (hours)
    alt : float (degrees)
    az : float (degrees)

    Returns
    -------
    valid : bool
    reason : str (if invalid)
    """
    # Dec limit (Keck can see down to about -37° depending on HA)
    if dec < -37:
        return False, f"Dec {dec:.1f}° < -37° limit"

    # HA limits (Keck is more permissive than Shane)
    if ha < -5.5:
        return False, f"HA {ha:.2f}h < -5.5h limit (too far east)"

    if ha > 5.5:
        return False, f"HA {ha:.2f}h > +5.5h limit (too far west)"

    # Keck I Nasmyth deck vignetting
    if not check_keck1_nasmyth_vignetting(az, alt):
        return False, (f"Vignetted by Keck I Nasmyth deck (az {az:.0f}°, "
                        f"alt {alt:.0f}° - needs {KECK1_NASMYTH_ALT_MIN:.0f}° "
                        f"in az {KECK1_NASMYTH_AZ_MIN:.0f}-{KECK1_NASMYTH_AZ_MAX:.0f}°)")

    return True, ""


"""
LRIS Mode Summary:
------------------
1. LONGSLIT: mag ≤ 21 (practical limit for reasonable S/N in ~1h)
2. MOS (slitmask): mag > 21, requires pre-milled masks (weeks lead time)
3. IMAGING: Available for acquisition, photometry, or when no longslit targets

For this run: longslit mode, mag ≤ 21 targets only.
"""

LRIS_LONGSLIT_MAG_LIMIT = 21.0  # Fainter needs MOS mask

# MOS on-target time once a mask exists (per the author, 2026-09-10): a mag
# <=23 masked target needs about 1 hour; fainter needs 1.5-2 hours. Bucketed
# at 24 mag to split that 1.5-2h range (not independently specified by the
# author -- flagged as an assumption).
MOS_MAG_BRIGHT_LIMIT = 23.0
MOS_MAG_MID_LIMIT = 24.0


def estimate_mos_exposure(mag_r):
    """
    Estimate on-target time for a mag>21 target once a MOS mask exists.

    Not a physical S/N calculation (no real ETC support for MOS mode) --
    an operational time budget per the author's stated practice.

    Returns
    -------
    dict with 'red_exp', 'blue_exp', 'science_min', 'total_min', 'mode'
    """
    if mag_r <= MOS_MAG_BRIGHT_LIMIT:
        total_min = 60
    elif mag_r < MOS_MAG_MID_LIMIT:
        total_min = 90
    else:
        total_min = 120
    return {
        'red_exp': 'MOS mask required',
        'blue_exp': 'MOS mask required',
        'science_min': total_min,
        'total_min': total_min,
        'mode': 'mos_required'
    }


def estimate_lris_exposure(mag_r, mode='longslit', airmass=1.2):
    """
    Estimate LRIS exposure times.

    Longslit exposures are computed with the real UCO/Lick LRIS S/N
    calculator (etc.ucolick.org -- see lris_etc.py), targeting median
    per-pixel continuum S/N = 10 *per single sub-exposure* in each arm
    (grism 600/4000 blue, grating 600/7500 red), taking the longer arm as
    the per-sub-exposure length, and always using >=3 sub-exposures (a
    cosmic-ray-rejection floor, not derived from S/N). This replaced a
    magnitude-bucket heuristic that had no basis in throughput/sky/read-noise
    physics (see KECK_LRIS_2026OCT02_SUMMARY.md, Prompt 7), and then a
    combined-S/N version that under-delivered S/N per individual frame
    (Prompt 8).

    Modes:
    - longslit: mag ≤ 21 (practical limit), real-ETC exposure time
    - imaging: 5 min per filter typically (unchanged, out of scope here)
    - mos: requires pre-milled masks (mask design, not an exposure-time
      question -- placeholder retained)

    Parameters
    ----------
    mag_r : float
    mode : str
    airmass : float
        Use the target's actual airmass at observation time.

    Returns
    -------
    dict with 'red_exp', 'blue_exp', 'total_min', 'mode'
    """
    if mode == 'imaging':
        return {
            'red_exp': '3 x 120',
            'blue_exp': '3 x 120',
            'science_min': 6,
            'total_min': 11,
            'mode': 'imaging'
        }

    # Longslit mode - check mag limit. This is *our own* mag-based check,
    # independent of whatever "mode" FFFF-PZ itself tags a target with --
    # FFFF-PZ tags everything pulled via num_targ_longslit as "longslit"
    # even when Pri_mag > 21 (verified 2026-09-10), so its mode column is
    # never read/trusted here.
    if mag_r > LRIS_LONGSLIT_MAG_LIMIT:
        return estimate_mos_exposure(mag_r)

    return estimate_lris_exposure_real(mag_r, airmass=airmass)


# Keck target-selection rule (10m aperture is wasted on targets Lick's 3m
# already covers): only take targets fainter than mag 19, unless the target
# is at Dec above the Lick/Shane pointing limit (82 deg) and so unreachable
# from Lick at any magnitude.
KECK_MAG_FAINT_LIMIT = 19.0
LICK_DEC_LIMIT = 82.0


def passes_keck_target_selection(mag, dec):
    """
    Keck target-selection rule: mag > 19, unless Dec > Lick's 82° limit.

    Returns
    -------
    keep : bool
    """
    return mag > KECK_MAG_FAINT_LIMIT or dec > LICK_DEC_LIMIT


def analyze_targets(targets_csv, date_str='2026-10-02'):
    """
    Analyze all targets for observability on given date at Keck.
    """
    # Read targets
    df = pd.read_csv(targets_csv)

    # Apply Keck target-selection rule (mag > 19, unless Dec > Lick limit)
    n_before = len(df)
    df = df[df.apply(lambda r: passes_keck_target_selection(r['Pri_mag'], r['Pri_Dec']),
                      axis=1)].copy()
    print(f"\nKeck target selection: {len(df)}/{n_before} pass "
          f"(mag > {KECK_MAG_FAINT_LIMIT}, unless Dec > {LICK_DEC_LIMIT}° Lick limit)")

    # Calculate twilight
    twilight = find_twilight(date_str)

    print(f"\n=== TWILIGHT TIMES FOR {date_str} (KECK) ===")
    print(f"Evening 18° twilight: {twilight['evening_hst'].strftime('%H:%M HST')} "
          f"(LST {twilight['evening_lst'].to_string(precision=0)})")
    print(f"Morning 18° twilight: {twilight['morning_hst'].strftime('%H:%M HST')} "
          f"(LST {twilight['morning_lst'].to_string(precision=0)})")
    print(f"Dark time: {twilight['dark_hours']:.1f} hours")

    # Determine timeline start (round down to nearest 10 min before evening twilight)
    eve_minute = twilight['evening_hst'].minute
    start_minute = (eve_minute // 10) * 10
    start_hst = twilight['evening_hst'].replace(minute=start_minute, second=0)

    print(f"Timeline start: {start_hst.strftime('%H:%M HST')}")

    # Calculate observable RA range
    eve_lst = twilight['evening_lst'].hour
    mor_lst = twilight['morning_lst'].hour
    print(f"\nObservable RA range (HA ±5.5h):")
    print(f"  Evening: RA {(eve_lst - 5.5) % 24:.1f}h to {(eve_lst + 5.5) % 24:.1f}h")
    print(f"  Morning: RA {(mor_lst - 5.5) % 24:.1f}h to {(mor_lst + 5.5) % 24:.1f}h")

    # Calculate observability for each target
    results = []

    for idx, row in df.iterrows():
        tns = row['TNS']
        ra = row['Pri_RA']
        dec = row['Pri_Dec']
        mag = row['Pri_mag']
        pox = row['Pri_POx']
        tags = row['FRB_tags'] if pd.notna(row['FRB_tags']) else ''
        dm = row['FRB_DM']

        # Calculate airmass at evening twilight
        am_eve, alt_eve, az_eve, ha_eve = calculate_airmass(
            ra, dec, twilight['evening_utc'])

        # Calculate airmass at morning twilight
        am_mor, alt_mor, az_mor, ha_mor = calculate_airmass(
            ra, dec, twilight['morning_utc'])

        # Find minimum airmass time during night
        # Sample every 15 minutes
        night_duration = twilight['dark_hours']
        n_samples = int(night_duration * 4)
        min_am = 99.9
        min_am_time = None
        min_am_ha = None
        min_am_alt = None
        min_am_az = None

        observable_hours = 0
        for i in range(n_samples):
            sample_time = twilight['evening_utc'] + timedelta(hours=i*0.25)
            am, alt, az, ha = calculate_airmass(ra, dec, sample_time)
            if am < min_am:
                min_am = am
                min_am_time = sample_time
                min_am_ha = ha
                min_am_az = az
                min_am_alt = alt
            # Count hours with airmass < 2.0 (or < 2.5 for bright targets)
            am_limit = 2.5 if mag < 17 else 2.0
            if am < am_limit:
                observable_hours += 0.25

        # Check pointing limits at minimum airmass time
        valid, reason = check_keck_limits(ra, dec, min_am_ha, min_am_alt, min_am_az)

        # Also check if observable at some point during the night
        # Bright targets (mag < 17) can tolerate higher airmass
        night_observable = observable_hours > 0.5  # At least 30 min

        # Determine LRIS mode from OUR OWN mag cut -- never from FFFF-PZ's
        # own "mode" column, which tags everything requested via
        # num_targ_longslit as "longslit" even when mag > 21 (verified
        # 2026-09-10). Always ask for masked targets (num_targ_mask > 0)
        # when building the FFFF-PZ Resource, but still re-derive mode here.
        if mag > LRIS_LONGSLIT_MAG_LIMIT:
            lris_mode = 'MOS (mask required)'
            mos_est = estimate_mos_exposure(mag)
            info = (f"Mag {mag:.1f} > {LRIS_LONGSLIT_MAG_LIMIT:.0f}: MOS mask "
                    f"required (~{mos_est['total_min']/60:.1f}h once milled)")
        else:
            lris_mode = 'longslit'
            info = ''

        results.append({
            'TNS': tns,
            'RA_deg': ra,
            'Dec_deg': dec,
            'RA_hours': ra/15.0,
            'mag_r': mag,
            'POx': pox,
            'tags': tags,
            'DM': dm,
            'lris_mode': lris_mode,
            'info': info,
            'min_airmass': min_am,
            'min_am_time_hst': utc_to_hst(min_am_time) if min_am_time else None,
            'min_am_ha': min_am_ha,
            'min_am_alt': min_am_alt,
            'am_evening': am_eve,
            'ha_evening': ha_eve,
            'alt_evening': alt_eve,
            'am_morning': am_mor,
            'ha_morning': ha_mor,
            'alt_morning': alt_mor,
            'observable_hours': observable_hours,
            'observable': night_observable and valid,
            'limit_reason': reason if not valid else (
                'Below horizon all night' if not night_observable else '')
        })

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('RA_hours')

    return results_df, twilight, start_hst


def find_observable_window(ra, dec, twilight, mag=20.0):
    """
    Find the time window when target is observable.

    Airmass limit: < 2.0 for faint targets, < 2.5 for bright (mag < 17).

    Returns
    -------
    start_hst, end_hst, duration_hours
    """
    window_start = None
    window_end = None
    am_limit = 2.5 if mag < 17 else 2.0

    # Sample every 10 minutes
    n_samples = int(twilight['dark_hours'] * 6)

    for i in range(n_samples):
        sample_utc = twilight['evening_utc'] + timedelta(minutes=i*10)
        am, alt, az, ha = calculate_airmass(ra, dec, sample_utc)

        if am < am_limit and check_keck_limits(ra, dec, ha, alt, az)[0]:
            if window_start is None:
                window_start = sample_utc
            window_end = sample_utc
        elif window_start is not None and window_end is not None:
            # Gap in observability - take first window
            break

    if window_start and window_end:
        duration = (window_end - window_start).total_seconds() / 3600
        return utc_to_hst(window_start), utc_to_hst(window_end), duration
    return None, None, 0


def select_targets_for_night(results_df, twilight, max_targets=8):
    """
    Select targets for observation based on priority rules.

    Priority:
    1. Must be observable (airmass < 2.0 for >30 min)
    2. Schedule within observable window
    3. If target is setting early, observe first
    4. Cover RA range efficiently

    Returns
    -------
    selected : DataFrame with observing order and scheduled times
    """
    # Filter to observable targets. Per the author (2026-09-11): include
    # MOS-mask-required targets (mag > 21) in the night plan too, scheduled
    # with their real allocated time (estimate_mos_exposure(), ~1-2h --
    # estimate_lris_exposure() already dispatches to it below), on the
    # assumption a mask can be milled before the run (~3 weeks out from
    # 2026-10-02). Submitting mask designs promptly is still required --
    # this schedules the *time*, not a guarantee the mask exists yet.
    observable = results_df[results_df['observable']].copy()
    n_mos_included = int((observable['lris_mode'] == 'MOS (mask required)').sum())

    print(f"\n=== TARGET SELECTION ===")
    print(f"Sky-observable targets: {len(observable)} / {len(results_df)} "
          f"({n_mos_included} need a MOS mask, included below with allocated time)")

    if len(observable) == 0:
        print("No observable targets!")
        return pd.DataFrame()

    # Calculate observable windows
    windows = []
    for idx, row in observable.iterrows():
        start, end, duration = find_observable_window(
            row['RA_deg'], row['Dec_deg'], twilight, row['mag_r'])
        windows.append({
            'window_start': start,
            'window_end': end,
            'window_hours': duration
        })

    window_df = pd.DataFrame(windows, index=observable.index)
    observable = pd.concat([observable, window_df], axis=1)

    # Sort by window end time (observe setting targets first)
    # This ensures targets about to set are prioritized
    observable = observable.sort_values('window_end')

    # Two-pass scheduling:
    # Pass 1: Schedule targets observable now or soon (setting targets)
    # Pass 2: Schedule targets that rise later (wait for window)
    selected = []
    current_time = twilight['evening_hst'] + timedelta(minutes=10)  # After standard + focus
    available_time = twilight['dark_hours'] * 60 - 30  # Reserve 30 min for calibrations
    total_time = 0
    scheduled_targets = set()

    # Sort by window start for proper ordering
    observable = observable.sort_values('window_start')

    # Schedule targets in window order
    for idx, row in observable.iterrows():
        if row['TNS'] in scheduled_targets:
            continue

        exp = estimate_lris_exposure(row['mag_r'], airmass=row['min_airmass'])
        window_start = row['window_start']
        window_end = row['window_end']

        if window_start is None or window_end is None:
            print(f"  Skipped {row['TNS']}: no observable window")
            continue

        # Skip if window already completely passed
        if current_time > window_end:
            print(f"  Skipped {row['TNS']}: window already passed "
                  f"(ended {window_end.strftime('%H:%M')}, now {current_time.strftime('%H:%M')})")
            continue

        # Determine optimal start time
        if current_time >= window_start:
            # Already in window, start now
            obs_start = current_time
        else:
            # Need to wait for window - schedule at window start
            obs_start = window_start

        obs_end = obs_start + timedelta(minutes=exp['total_min'])

        # Check if observation fits within window
        if obs_end > window_end + timedelta(minutes=10):
            # Doesn't fit, skip
            print(f"  Skipped {row['TNS']}: needs {exp['total_min']:.0f} min but only "
                  f"{(window_end - obs_start).total_seconds()/60:.0f} min left in its "
                  f"AM<2.0 window ({window_start.strftime('%H:%M')}-{window_end.strftime('%H:%M')})")
            continue

        # Check if we have time budget
        obs_duration = exp['total_min']
        if total_time + obs_duration > available_time:
            print(f"  Skipped {row['TNS']}: no time budget left "
                  f"({total_time:.0f}/{available_time:.0f} min used)")
            continue

        row_dict = row.to_dict()
        row_dict.update(exp)
        row_dict['scheduled_start'] = obs_start
        row_dict['scheduled_end'] = obs_end
        selected.append(row_dict)
        scheduled_targets.add(row['TNS'])
        total_time += obs_duration
        current_time = obs_end

        if len(selected) >= max_targets:
            break

    # Sort selected by scheduled start time
    selected_df = pd.DataFrame(selected)
    if len(selected_df) > 0:
        selected_df = selected_df.sort_values('scheduled_start')

    print(f"Selected {len(selected_df)} targets")
    print(f"Total observing time: {total_time:.0f} min ({total_time/60:.1f} h)")
    print(f"Available dark time: {available_time:.0f} min ({available_time/60:.1f} h)")

    return selected_df


def generate_starlist(selected_df, output_path):
    """
    Generate Keck starlist file.

    Format: name  HH MM SS.ss  ±DD MM SS.s  equinox  [keywords]
    """
    lines = []
    lines.append("# Keck/LRIS starlist for Oct 2, 2026")
    lines.append("# Created by JXP and Claude")
    lines.append("")
    lines.append("# === Standard Stars ===")
    # Add typical flux standards
    lines.append("BD28d4211  21 51 11.02 +28 51 50.4 2000.0 vmag=10.5 # Flux standard")
    lines.append("Feige110   23 19 58.40 -05 09 56.2 2000.0 vmag=11.8 # Flux standard")
    lines.append("")
    lines.append("# === Science Targets ===")

    for idx, row in selected_df.iterrows():
        # Parse RA/Dec to sexagesimal
        ra_deg = row['RA_deg']
        dec_deg = row['Dec_deg']

        ra_h = int(ra_deg / 15)
        ra_m = int((ra_deg / 15 - ra_h) * 60)
        ra_s = ((ra_deg / 15 - ra_h) * 60 - ra_m) * 60

        dec_sign = '+' if dec_deg >= 0 else '-'
        dec_abs = abs(dec_deg)
        dec_d = int(dec_abs)
        dec_m = int((dec_abs - dec_d) * 60)
        dec_s = ((dec_abs - dec_d) * 60 - dec_m) * 60

        # Format name (max 16 chars)
        name = row['TNS'][:16]

        # Format coordinates
        ra_str = f"{ra_h:02d} {ra_m:02d} {ra_s:05.2f}"
        dec_str = f"{dec_sign}{dec_d:02d} {dec_m:02d} {dec_s:04.1f}"

        # Keywords
        mag = row['mag_r']
        line = f"{name:<16}  {ra_str}  {dec_str}  2000.0  vmag={mag:.1f}"

        # Flag mask-required targets prominently -- these need a pre-milled
        # slitmask, not a plain longslit acquisition
        comment_bits = []
        if row.get('lris_mode') == 'MOS (mask required)':
            comment_bits.append('MASK REQUIRED')
        if row.get('tags'):
            comment_bits.append(str(row['tags']))
        if comment_bits:
            line += f"  # {' | '.join(comment_bits)}"

        lines.append(line)

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"\nStarlist written to: {output_path}")


def print_night_plan(selected_df, twilight, start_hst):
    """Print formatted night plan to console."""
    print("\n" + "="*70)
    print("KECK/LRIS NIGHT PLAN - October 2, 2026")
    print("="*70)

    print(f"\nEvening 18° twilight: {twilight['evening_hst'].strftime('%H:%M HST')}")
    print(f"Morning 18° twilight: {twilight['morning_hst'].strftime('%H:%M HST')}")
    print(f"Dark time: {twilight['dark_hours']:.1f} hours")
    print(f"Timeline start: {start_hst.strftime('%H:%M HST')}")

    print("\n--- TIMELINE ---")
    current_time = start_hst

    # Evening standard
    print(f"\n{current_time.strftime('%H:%M')} HST - Flux standard (BD28d4211) - 5 min")
    current_time += timedelta(minutes=5)

    # Focus
    print(f"{current_time.strftime('%H:%M')} HST - Focus check - 5 min")
    current_time += timedelta(minutes=5)

    # Science targets
    print("\n--- SCIENCE TARGETS ---")
    for idx, row in selected_df.iterrows():
        # Use scheduled times if available
        if 'scheduled_start' in row and pd.notna(row['scheduled_start']):
            obs_start = row['scheduled_start']
            obs_end = row['scheduled_end']
        else:
            obs_start = current_time
            obs_end = current_time + timedelta(minutes=row['total_min'])

        # Calculate HA at observation time
        obs_utc = obs_start.astimezone(timezone.utc)
        am, alt, _, ha = calculate_airmass(row['RA_deg'], row['Dec_deg'], obs_utc)

        mode_tag = " [MOS - MASK REQUIRED]" if row.get('lris_mode') == 'MOS (mask required)' else ""
        print(f"\n{obs_start.strftime('%H:%M')}-{obs_end.strftime('%H:%M')} HST: "
              f"{row['TNS']}{mode_tag}")
        print(f"  RA: {row['RA_hours']:.2f}h  Dec: {row['Dec_deg']:.1f}°  "
              f"mag_r: {row['mag_r']:.1f}")
        print(f"  HA: {ha:+.1f}h  Airmass: {am:.2f}  Alt: {alt:.0f}°")
        print(f"  Exposure: {row['red_exp']} (red), {row['blue_exp']} (blue)")
        print(f"  Duration: {row['total_min']} min (incl. slew/acquisition)")
        print(f"  Window: {row['window_start'].strftime('%H:%M')}-{row['window_end'].strftime('%H:%M')} HST")

        current_time = obs_end

    # Morning standard
    print(f"\n{current_time.strftime('%H:%M')} HST - Flux standard (Feige110) - 5 min")
    current_time += timedelta(minutes=5)

    # Calibrations
    print(f"{current_time.strftime('%H:%M')} HST - Calibrations (arcs, flats) - 20 min")

    print("\n" + "="*70)


def print_recommendations(selected_df, twilight, n_mos=0):
    """Print LRIS recommendations and night summary."""
    total_science_min = sum(row['total_min'] for _, row in selected_df.iterrows())
    dark_min = twilight['dark_hours'] * 60

    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)
    print(f"""
LRIS Mode Summary:
  - LONGSLIT: mag ≤ 21 (all current targets OK)
  - MOS: mag > 21 requires pre-milled slitmasks (weeks lead time)
  - IMAGING: Available for acquisition, field verification, photometry

Night Utilization:
  - Science time: {total_science_min/60:.1f}h of {dark_min/60:.1f}h available ({100*total_science_min/dark_min:.0f}%)
  - Gaps in schedule: Could fill with imaging or backup targets

Target Recommendations:
  - Real LRIS exposures (S/N=10/exposure, 3x min) run ~19-58 min per target
    depending on magnitude -- request more targets from FFFF-PZ
    (num_targ_longslit above 20) to fill the remaining gap
  - Include imaging targets (status=NeedImage) for backup/gap filling
  - For mag > 21 targets: submit mask designs weeks before run ({n_mos}
    already in hand from this pull, sky-observable, just needing masks;
    ~1-2h on-target once milled, per magnitude)
""")


def main():
    """Main execution."""
    # Keck-native FFFF-PZ pull (Keck-2026B-01 Resource: LRIS, min_mag=19, no Dec cut)
    targets_csv = '/home/lordrick/Projects/night-planner/Night_plans/Keck-2026B-01/Keck-2026B-01_targets.csv'
    date = '2026-10-02'

    # Create output directory
    output_dir = '/home/lordrick/Projects/night-planner/Night_plans/Keck-2026B-01'
    os.makedirs(output_dir, exist_ok=True)

    # Analyze all targets
    results_df, twilight, start_hst = analyze_targets(targets_csv, date)

    # Print full analysis
    print("\n=== ALL TARGETS (sorted by RA) ===")
    display_cols = ['TNS', 'RA_hours', 'Dec_deg', 'mag_r', 'lris_mode',
                    'min_airmass', 'observable', 'limit_reason', 'info']
    print(results_df[display_cols].to_string(index=False))

    # Check for MOS-required targets (still included in the schedule below,
    # with their allocated ~1-2h time -- flagged here as a reminder that
    # each needs a slitmask milled before the run, not as an exclusion)
    mos_targets = results_df[results_df['lris_mode'] == 'MOS (mask required)']
    if len(mos_targets) > 0:
        print(f"\n*** NOTE: {len(mos_targets)} targets need MOS masks (mag > 21) ***")
        print("Included in the night plan below with allocated time -- submit mask designs now:")
        print(mos_targets[['TNS', 'mag_r', 'info']].to_string(index=False))

    # Select targets for night
    selected = select_targets_for_night(results_df, twilight, max_targets=10)

    if len(selected) > 0:
        # Print night plan
        print_night_plan(selected, twilight, start_hst)

        # Print recommendations
        print_recommendations(selected, twilight, n_mos=len(mos_targets))

        # Generate starlist
        starlist_path = f'{output_dir}/keck_lris_oct02.starlist'
        generate_starlist(selected, starlist_path)

        # Save results
        results_df.to_csv(f'{output_dir}/target_analysis.csv', index=False)
        selected.to_csv(f'{output_dir}/selected_targets.csv', index=False)

        print(f"\nResults saved to {output_dir}/")
        print(f"  - target_analysis.csv: all targets with observability")
        print(f"  - selected_targets.csv: selected targets")
        print(f"  - keck_lris_oct02.starlist: Keck starlist")

    return results_df, selected, twilight, start_hst


if __name__ == '__main__':
    results, selected, twilight, start_hst = main()
