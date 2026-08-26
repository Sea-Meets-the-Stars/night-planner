"""
Analyze Lick-2026B-01 timeline for deadtime gaps.

Created by JXP and Claude
"""

from datetime import datetime, timedelta, timezone
import pandas as pd

# PST fixed offset
PST = timezone(timedelta(hours=-8))

# Sidereal rate
SIDEREAL_RATE = 1.00273790935

# Evening twilight
EVE_PST = datetime(2026, 8, 13, 20, 38, 0, tzinfo=PST)
EVE_LST = 18.03  # hours

def pst_to_lst(pst_time):
    """Convert PST to LST."""
    hours_since_eve = (pst_time - EVE_PST).total_seconds() / 3600
    lst = EVE_LST + hours_since_eve * SIDEREAL_RATE
    while lst >= 24:
        lst -= 24
    return lst

# Read selected targets
df = pd.read_csv('/home/lordrick/Projects/night-planner/Night_plans/Lick-2026B-01/selected_targets_night1.csv')

print("="*80)
print("LICK-2026B-01 DEADTIME ANALYSIS (Aug 13-14, 2026)")
print("="*80)

# Sort by RA
df = df.sort_values('RA_hours')

# Exposure times (from HOWTO)
exp_times = {
    'FRB20230729A': 80,
    'FRB20200621B': 60,
    'FRB20200702C': 60,
    'FRB20250902A': 80,
    'FRB20230805A': 80,
    'FRB20231223B': 60,
}

print("\nSELECTED TARGETS (by RA):")
print("-"*80)
print(f"{'TNS':<20s} {'RA (h)':<8s} {'HA_eve':<8s} {'HA_morn':<8s} {'Dur':<8s} {'Observable':<15s}")
print("-"*80)

for idx, row in df.iterrows():
    tns = row['TNS']
    ra = row['RA_hours']
    ha_eve = row['ha_evening']
    ha_morn = row['ha_morning']
    dur = exp_times.get(tns, 0)

    # When observable
    if ha_eve >= -5 and ha_eve <= 3.75:
        obs = "Evening"
    elif ha_morn >= -5 and ha_morn <= 3.75:
        obs = "Morning"
    else:
        obs = "Never?"

    print(f"{tns:<20s} {ra:6.2f}   {ha_eve:+6.2f}h  {ha_morn:+6.2f}h  {dur:3d}min  {obs:<15s}")

print("\n" + "="*80)
print("TIMELINE SIMULATION")
print("="*80)

# Build timeline
current_pst = datetime(2026, 8, 13, 20, 30, 0, tzinfo=PST)  # Start

events = []

def add_event(desc, start, duration_min):
    """Add event to timeline."""
    end = start + timedelta(minutes=duration_min)
    lst_start = pst_to_lst(start)
    lst_end = pst_to_lst(end)
    events.append({
        'event': desc,
        'start_pst': start,
        'end_pst': end,
        'lst_start': lst_start,
        'lst_end': lst_end,
        'duration_min': duration_min,
    })
    return end

# Standard + focus
current_pst = add_event("Standard HZ_44", current_pst, 5)
current_pst = add_event("Focus", current_pst, 5)

# Evening targets (RA 15-16h)
evening = df[df['RA_hours'] > 14].sort_values('RA_hours', ascending=False)  # Highest RA first
for idx, row in evening.iterrows():
    tns = row['TNS']
    dur = exp_times.get(tns, 60)
    current_pst = add_event(f"Slew to {tns}", current_pst, 2)
    current_pst = add_event(f"Science {tns}", current_pst, dur)

eve_end_pst = current_pst
eve_end_lst = pst_to_lst(eve_end_pst)

print(f"\n{'Time (PST)':<12s} {'LST':<8s} {'Event':<40s} {'Duration':<10s}")
print("-"*80)

for evt in events:
    print(f"{evt['start_pst'].strftime('%H:%M'):<12s} "
          f"{evt['lst_start']:5.2f}h  "
          f"{evt['event']:<40s} "
          f"{evt['duration_min']:3d} min")

print(f"\nEvening block ends: {eve_end_pst.strftime('%H:%M PST')} (LST {eve_end_lst:.2f}h)")

# Check when morning targets become observable (HA = -5h)
print("\n" + "="*80)
print("MORNING TARGET OBSERVABILITY")
print("="*80)

morning = df[df['RA_hours'] < 14].sort_values('RA_hours')

print(f"\n{'Target':<20s} {'RA':<8s} {'Observable from':<20s} {'LST':<10s}")
print("-"*80)

obs_times = []
for idx, row in morning.iterrows():
    tns = row['TNS']
    ra = row['RA_hours']

    # HA = -5 means LST = RA - 5
    lst_obs = ra - 5
    if lst_obs < 0:
        lst_obs += 24

    # Convert LST to PST
    delta_lst = lst_obs - EVE_LST
    if delta_lst < 0:
        delta_lst += 24

    delta_hours = delta_lst / SIDEREAL_RATE
    pst_obs = EVE_PST + timedelta(hours=delta_hours)

    print(f"{tns:<20s} {ra:6.2f}h  {pst_obs.strftime('%H:%M PST'):<20s} LST {lst_obs:5.2f}h")

    obs_times.append((tns, pst_obs, lst_obs, ra))

# Find first morning target that becomes observable
first_morning_tns, first_morning_pst, first_morning_lst, first_morning_ra = obs_times[0]

print(f"\nFirst morning target observable: {first_morning_tns} at {first_morning_pst.strftime('%H:%M PST')}")
print(f"Evening block ends: {eve_end_pst.strftime('%H:%M PST')}")

# Calculate gap
if first_morning_pst > eve_end_pst:
    gap_hours = (first_morning_pst - eve_end_pst).total_seconds() / 3600
    gap_minutes = gap_hours * 60
    print(f"\n{'='*80}")
    print(f"DEADTIME: {gap_hours:.2f} hours ({gap_minutes:.0f} minutes)")
    print(f"From {eve_end_pst.strftime('%H:%M PST')} to {first_morning_pst.strftime('%H:%M PST')}")
    print(f"{'='*80}")
else:
    print(f"\n{'='*80}")
    print(f"NO DEADTIME!")
    print(f"First morning target already observable when evening ends.")
    print(f"{'='*80}")

# Continue timeline with morning targets
print("\n" + "="*80)
print("FULL NIGHT TIMELINE")
print("="*80)

current_pst = eve_end_pst

for tns, pst_obs, lst_obs, ra in obs_times:
    # Wait until observable if needed
    if current_pst < pst_obs:
        gap = (pst_obs - current_pst).total_seconds() / 60
        if gap > 5:  # More than 5 min gap
            add_event(f"WAIT (target not yet observable)", current_pst, int(gap))
            current_pst = pst_obs

    dur = exp_times.get(tns, 60)
    current_pst = add_event(f"Slew to {tns}", current_pst, 2)
    current_pst = add_event(f"Science {tns}", current_pst, dur)

# Standard at end
current_pst = add_event("Standard Feige_110", current_pst, 5)

# Calibrations
current_pst = add_event("Bias frames", current_pst, 5)
current_pst = add_event("Flat fields", current_pst, 10)

print(f"\n{'Time (PST)':<12s} {'LST':<8s} {'Event':<40s} {'Duration':<10s}")
print("-"*80)

for evt in events:
    style = ""
    if "WAIT" in evt['event']:
        style = " ← DEADTIME"

    print(f"{evt['start_pst'].strftime('%H:%M'):<12s} "
          f"{evt['lst_start']:5.2f}h  "
          f"{evt['event']:<40s} "
          f"{evt['duration_min']:3d} min{style}")

total_time = (events[-1]['end_pst'] - events[0]['start_pst']).total_seconds() / 3600
science_time = sum(e['duration_min'] for e in events if 'Science' in e['event']) / 60
overhead_time = total_time - science_time

print(f"\n{'='*80}")
print(f"SUMMARY")
print(f"{'='*80}")
print(f"Timeline: {events[0]['start_pst'].strftime('%H:%M PST')} → {events[-1]['end_pst'].strftime('%H:%M PST')}")
print(f"Total time: {total_time:.2f}h")
print(f"Science time: {science_time:.2f}h ({6} targets)")
print(f"Overhead time: {overhead_time:.2f}h (standards, slews, calibrations, focus)")

# Check for WAIT events
wait_events = [e for e in events if "WAIT" in e['event']]
if wait_events:
    total_wait = sum(e['duration_min'] for e in wait_events)
    print(f"\nDEADTIME TOTAL: {total_wait} minutes ({total_wait/60:.2f}h)")
    for e in wait_events:
        print(f"  {e['start_pst'].strftime('%H:%M')}-{e['end_pst'].strftime('%H:%M')} PST: {e['duration_min']} min")
else:
    print(f"\nNO DEADTIME - targets flow continuously!")

print(f"\n{'='*80}")
