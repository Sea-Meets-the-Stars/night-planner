# Target rejection/acceptance analysis -- Lick-2026B-02, night of 2026-09-14/2026-09-15

Evening twilight: 19:44 PST (LST 19h13m56.4s). Morning twilight: 04:21 PST (LST 03h52m21.3s).

Shane 3m limits: Dec <= 82 deg; -5.00h <= HA <= +3.75h (HA = LST - RA).

**Summary:** 4 SCHEDULED, 1 SCHEDULED (forced, partial), 7 NEVER HA-LEGAL, 3 DEC-CUT -- 15 targets total.

## Summary table

| TNS | RA (HMS) | Dec (DMS) | r-mag | Status | Reason |
|---|---|---|---|---|---|
| FRB20260623C | 00h38m52.2s | +32d52m28.1s | 16.98 | SCHEDULED | HA-legal window 20:08-04:21 PST (492 min, HA -5.00h to +3.22h) comfortably fits the 40 min Kast exposure needed at r=16.98; scheduled 20:38-21:18 PST. |
| FRB20260507D | 01h43m48.6s | +32d46m08.5s | 18.56 | SCHEDULED | HA-legal window 21:13-04:21 PST (427 min, HA -5.00h to +2.14h) comfortably fits the 60 min Kast exposure needed at r=18.56; scheduled 21:23-22:23 PST. |
| FRB20230805A | 02h24m04.0s | +52d41m36.0s | 17.99 | SCHEDULED | HA-legal window 21:53-04:21 PST (387 min, HA -5.00h to +1.47h) comfortably fits the 60 min Kast exposure needed at r=17.99; scheduled 22:28-23:28 PST. |
| FRB20260510A | 03h21m39.4s | +86d20m22.8s | 18.97 | DEC-CUT | Dec = +86d20m22.8s exceeds the Shane polar limit (Dec <= 82 deg) by 4.34 deg -- dropped before HA/scheduling analysis. |
| FRB20260418B | 06h11m02.7s | +39d21m33.4s | 20.23 | SCHEDULED | HA-legal window 01:40-04:21 PST (161 min, HA -5.00h to -2.31h) comfortably fits the 90 min Kast exposure needed at r=20.23; scheduled 01:40-03:10 PST. |
| FRB20260305A | 08h02m10.6s | +36d59m49.5s | 18.52 | NEVER HA-LEGAL | HA(beg night, evening twilight LST 19h13m56.4s) = +11.20h, HA(end night, morning twilight LST 03h52m21.3s) = -4.16h -- already past HA_MAX=+3.75h at evening twilight, and HA only increases through the night -- never re-enters the legal window before dawn. |
| FRB20260514A | 08h28m30.6s | +69d14m22.7s | 20.27 | NEVER HA-LEGAL | HA(beg night, evening twilight LST 19h13m56.4s) = +10.76h, HA(end night, morning twilight LST 03h52m21.3s) = -4.60h -- already past HA_MAX=+3.75h at evening twilight, and HA only increases through the night -- never re-enters the legal window before dawn. |
| FRB20251003A | 10h04m25.6s | +84d41m55.4s | 16.37 | DEC-CUT | Dec = +84d41m55.4s exceeds the Shane polar limit (Dec <= 82 deg) by 2.70 deg -- dropped before HA/scheduling analysis. |
| FRB20260625A | 10h18m57.3s | +82d24m13.5s | 17.83 | DEC-CUT | Dec = +82d24m13.5s exceeds the Shane polar limit (Dec <= 82 deg) by 0.40 deg -- dropped before HA/scheduling analysis. |
| FRB20260310B | 11h42m52.6s | +79d37m05.5s | 18.95 | NEVER HA-LEGAL | HA(beg night, evening twilight LST 19h13m56.4s) = +7.52h, HA(end night, morning twilight LST 03h52m21.3s) = -7.84h -- already past HA_MAX=+3.75h at evening twilight, and HA only increases through the night -- never re-enters the legal window before dawn. |
| FRB20201128D | 12h12m29.9s | +73d17m42.9s | 16.32 | NEVER HA-LEGAL | HA(beg night, evening twilight LST 19h13m56.4s) = +7.02h, HA(end night, morning twilight LST 03h52m21.3s) = -8.34h -- already past HA_MAX=+3.75h at evening twilight, and HA only increases through the night -- never re-enters the legal window before dawn. |
| FRB20260406B | 12h49m24.5s | +52d38m42.9s | 19.51 | NEVER HA-LEGAL | HA(beg night, evening twilight LST 19h13m56.4s) = +6.41h, HA(end night, morning twilight LST 03h52m21.3s) = -8.95h -- already past HA_MAX=+3.75h at evening twilight, and HA only increases through the night -- never re-enters the legal window before dawn. |
| FRB20240324A | 12h51m21.5s | +78d49m57.4s | 19.18 | NEVER HA-LEGAL | HA(beg night, evening twilight LST 19h13m56.4s) = +6.38h, HA(end night, morning twilight LST 03h52m21.3s) = -8.98h -- already past HA_MAX=+3.75h at evening twilight, and HA only increases through the night -- never re-enters the legal window before dawn. |
| FRB20260521A | 15h22m12.4s | +68d59m32.7s | 17.77 | NEVER HA-LEGAL | HA(beg night, evening twilight LST 19h13m56.4s) = +3.86h, HA(end night, morning twilight LST 03h52m21.3s) = -11.50h -- already past HA_MAX=+3.75h at evening twilight, and HA only increases through the night -- never re-enters the legal window before dawn. |
| FRB20260627D | 16h13m46.6s | +68d15m35.4s | 19.64 | SCHEDULED (forced, partial) | HA-legal window 19:44-20:28 PST (45 min) is too short for the 90 min Kast exposure needed at r=19.64 -- author's explicit call to attempt it anyway (faint, fast-setting target): forced first, scheduled 19:49-20:28 PST for a truncated 40 min exposure (partial spectrum expected). |

## Per-target detail

### FRB20260623C -- SCHEDULED

- RA: 00h38m52.2s, Dec: +32d52m28.1s
- Host r-mag: 16.98, P(O|x): 0.999, DM: 332.8, tags: CHIME-Unbiased,CHIME-Lowz
- **Reason:** HA-legal window 20:08-04:21 PST (492 min, HA -5.00h to +3.22h) comfortably fits the 40 min Kast exposure needed at r=16.98; scheduled 20:38-21:18 PST.

### FRB20260507D -- SCHEDULED

- RA: 01h43m48.6s, Dec: +32d46m08.5s
- Host r-mag: 18.56, P(O|x): 1.000, DM: 341.3, tags: CHIME-Unbiased,CHIME-Lowz
- **Reason:** HA-legal window 21:13-04:21 PST (427 min, HA -5.00h to +2.14h) comfortably fits the 60 min Kast exposure needed at r=18.56; scheduled 21:23-22:23 PST.

### FRB20230805A -- SCHEDULED

- RA: 02h24m04.0s, Dec: +52d41m36.0s
- Host r-mag: 17.99, P(O|x): 0.771, DM: 638.5, tags: CHIME-Repeater,CHIME-Blind
- **Reason:** HA-legal window 21:53-04:21 PST (387 min, HA -5.00h to +1.47h) comfortably fits the 60 min Kast exposure needed at r=17.99; scheduled 22:28-23:28 PST.

### FRB20260510A -- DEC-CUT

- RA: 03h21m39.4s, Dec: +86d20m22.8s
- Host r-mag: 18.97, P(O|x): 0.994, DM: 172.7, tags: CHIME-Lowz
- **Reason:** Dec = +86d20m22.8s exceeds the Shane polar limit (Dec <= 82 deg) by 4.34 deg -- dropped before HA/scheduling analysis.

### FRB20260418B -- SCHEDULED

- RA: 06h11m02.7s, Dec: +39d21m33.4s
- Host r-mag: 20.23, P(O|x): 0.976, DM: 211.3, tags: CHIME-Lowz
- **Reason:** HA-legal window 01:40-04:21 PST (161 min, HA -5.00h to -2.31h) comfortably fits the 90 min Kast exposure needed at r=20.23; scheduled 01:40-03:10 PST.

### FRB20260305A -- NEVER HA-LEGAL

- RA: 08h02m10.6s, Dec: +36d59m49.5s
- Host r-mag: 18.52, P(O|x): 0.998, DM: 297.1, tags: CHIME-Blind
- **Reason:** HA(beg night, evening twilight LST 19h13m56.4s) = +11.20h, HA(end night, morning twilight LST 03h52m21.3s) = -4.16h -- already past HA_MAX=+3.75h at evening twilight, and HA only increases through the night -- never re-enters the legal window before dawn.

### FRB20260514A -- NEVER HA-LEGAL

- RA: 08h28m30.6s, Dec: +69d14m22.7s
- Host r-mag: 20.27, P(O|x): 1.000, DM: 617.5, tags: CHIME-Unbiased
- **Reason:** HA(beg night, evening twilight LST 19h13m56.4s) = +10.76h, HA(end night, morning twilight LST 03h52m21.3s) = -4.60h -- already past HA_MAX=+3.75h at evening twilight, and HA only increases through the night -- never re-enters the legal window before dawn.

### FRB20251003A -- DEC-CUT

- RA: 10h04m25.6s, Dec: +84d41m55.4s
- Host r-mag: 16.37, P(O|x): 0.946, DM: 268.0, tags: CHIME-Unbiased,CHIME-Lowz
- **Reason:** Dec = +84d41m55.4s exceeds the Shane polar limit (Dec <= 82 deg) by 2.70 deg -- dropped before HA/scheduling analysis.

### FRB20260625A -- DEC-CUT

- RA: 10h18m57.3s, Dec: +82d24m13.5s
- Host r-mag: 17.83, P(O|x): 1.000, DM: 233.3, tags: CHIME-Unbiased,CHIME-Lowz
- **Reason:** Dec = +82d24m13.5s exceeds the Shane polar limit (Dec <= 82 deg) by 0.40 deg -- dropped before HA/scheduling analysis.

### FRB20260310B -- NEVER HA-LEGAL

- RA: 11h42m52.6s, Dec: +79d37m05.5s
- Host r-mag: 18.95, P(O|x): 0.998, DM: 287.5, tags: CHIME-Unbiased,CHIME-Lowz
- **Reason:** HA(beg night, evening twilight LST 19h13m56.4s) = +7.52h, HA(end night, morning twilight LST 03h52m21.3s) = -7.84h -- already past HA_MAX=+3.75h at evening twilight, and HA only increases through the night -- never re-enters the legal window before dawn.

### FRB20201128D -- NEVER HA-LEGAL

- RA: 12h12m29.9s, Dec: +73d17m42.9s
- Host r-mag: 16.32, P(O|x): 0.957, DM: 158.1, tags: CHIME-Blind
- **Reason:** HA(beg night, evening twilight LST 19h13m56.4s) = +7.02h, HA(end night, morning twilight LST 03h52m21.3s) = -8.34h -- already past HA_MAX=+3.75h at evening twilight, and HA only increases through the night -- never re-enters the legal window before dawn.

### FRB20260406B -- NEVER HA-LEGAL

- RA: 12h49m24.5s, Dec: +52d38m42.9s
- Host r-mag: 19.51, P(O|x): 1.000, DM: 353.4, tags: CHIME-Unbiased
- **Reason:** HA(beg night, evening twilight LST 19h13m56.4s) = +6.41h, HA(end night, morning twilight LST 03h52m21.3s) = -8.95h -- already past HA_MAX=+3.75h at evening twilight, and HA only increases through the night -- never re-enters the legal window before dawn.

### FRB20240324A -- NEVER HA-LEGAL

- RA: 12h51m21.5s, Dec: +78d49m57.4s
- Host r-mag: 19.18, P(O|x): 0.956, DM: 163.7, tags: CHIME-Blind
- **Reason:** HA(beg night, evening twilight LST 19h13m56.4s) = +6.38h, HA(end night, morning twilight LST 03h52m21.3s) = -8.98h -- already past HA_MAX=+3.75h at evening twilight, and HA only increases through the night -- never re-enters the legal window before dawn.

### FRB20260521A -- NEVER HA-LEGAL

- RA: 15h22m12.4s, Dec: +68d59m32.7s
- Host r-mag: 17.77, P(O|x): 0.969, DM: 336.8, tags: CHIME-Unbiased,CHIME-Lowz
- **Reason:** HA(beg night, evening twilight LST 19h13m56.4s) = +3.86h, HA(end night, morning twilight LST 03h52m21.3s) = -11.50h -- already past HA_MAX=+3.75h at evening twilight, and HA only increases through the night -- never re-enters the legal window before dawn.

### FRB20260627D -- SCHEDULED (forced, partial)

- RA: 16h13m46.6s, Dec: +68d15m35.4s
- Host r-mag: 19.64, P(O|x): 1.000, DM: 280.2, tags: CHIME-Unbiased,CHIME-Lowz
- **Reason:** HA-legal window 19:44-20:28 PST (45 min) is too short for the 90 min Kast exposure needed at r=19.64 -- author's explicit call to attempt it anyway (faint, fast-setting target): forced first, scheduled 19:49-20:28 PST for a truncated 40 min exposure (partial spectrum expected).

