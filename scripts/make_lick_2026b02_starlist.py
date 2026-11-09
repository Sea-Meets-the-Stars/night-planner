"""
Build a Lick/Shane starlist for the Lick-2026B-02 night of 2026-09-14/15.

Created by JXP and Claude

Format matches the chime-ffff-pz `chime_ffff_pz_starlist lick` convention
(chime_ffff_pz/scripts/starlist.py, per the Lick starlist spec:
https://mthamilton.ucolick.org/techdocs/telescopes/starlistFormat.html):

    <name padded to 16 chars> HH MM SS.ss +DD MM SS.s epoch

This run has no `*finder.json` files (no finder-chart/offset-star step has
been run for Lick-2026B-02 yet -- see "What this pass did not do" in
claude_prompts/night_plans/lick_2026sep14.md), so each science target uses
its PATH primary-host coordinates (from Lick-2026B-02_targets.csv) rather
than an offset star or slit-center row. The standard star (Feige_110) is
included once; the night plan uses it twice (start and end of night) at
different airmass, per build_lick_2026b02_night_plan.py.
"""

import pandas as pd
from astropy.coordinates import SkyCoord

TARGETS_CSV = "Night_plans/Lick-2026B-02/Lick-2026B-02_targets.csv"
OUTFILE = "Night_plans/Lick-2026B-02/lick.starlist"

# Scheduled science targets for the night of 2026-09-14/15 (see
# claude_prompts/night_plans/lick_2026sep14.md, Prompt 2 schedule table),
# in observing order.
SCHEDULED_TNS = ["FRB20260623C", "FRB20260507D", "FRB20230805A", "FRB20260418B"]

# Standard star (build_lick_2026b02_night_plan.py STD_STAR)
STD_STAR = dict(name="Feige_110", ra="23:19:58.39", dec="-05:09:55.8")


def zpad(val, n):
    bits = val.split(".")
    return "%s.%s" % (bits[0].zfill(n), bits[1])


def starlist_row(name, coord):
    hour = f"{coord.ra.hms[0]:02.0f}"
    ra_min = f"{coord.ra.hms[1]:02.0f}"
    ra_sec = zpad(f"{coord.ra.hms[2]:.2f}", 2)

    deg = f"{coord.dec.dms[0]:+03.0f}"
    dec_min = f"{abs(coord.dec.dms[1]):02.0f}"
    dec_sec = zpad(f"{abs(coord.dec.dms[2]):.1f}", 2)

    return f"{name.ljust(16)} {hour} {ra_min} {ra_sec} {deg} {dec_min} {dec_sec} 2000.0"


def main():
    targets = pd.read_csv(TARGETS_CSV)

    rows = []
    for tns in SCHEDULED_TNS:
        row = targets.loc[targets["TNS"] == tns].iloc[0]
        coord = SkyCoord(row["Pri_RA"], row["Pri_Dec"], unit="deg")
        rows.append(starlist_row(tns, coord))

    std_coord = SkyCoord(STD_STAR["ra"], STD_STAR["dec"], unit=("hourangle", "deg"))
    rows.append(starlist_row(STD_STAR["name"], std_coord))

    with open(OUTFILE, "w") as f:
        f.write("\n".join(rows) + "\n")

    print(f"Wrote: {OUTFILE}")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
