# KDY Sauna BLE Protocol

Reverse-engineered from the decompiled vendor app and hardware captures against `KDYSauna-10`. Confidence labels:

| Label | Meaning |
| ----- | ------- |
| verified | Confirmed against hardware GATT / frame framing |
| observed | Matched live status packets on real hardware |
| unconfirmed | Present in decompiled app code; never sent to real hardware |
| unknown | Present in frames; meaning not established |

## GATT layout

| UUID | Short | Properties | Purpose | Confidence |
| ---- | ----- | ---------- | ------- | ---------- |
| `0000fff0-0000-1000-8000-00805f9b34fb` | FFF0 | Service | KDY service | verified |
| `0000fff1-0000-1000-8000-00805f9b34fb` | FFF1 | Write-without-response, Notify | Command channel; also emits status frames | verified |
| `0000fff2-0000-1000-8000-00805f9b34fb` | FFF2 | Read, Notify | Status channel | verified |
| `0000fff3-0000-1000-8000-00805f9b34fb` | FFF3 | Write-without-response | Unused (phase 1) | verified (UUID only) |

Device advertises as `KDYSauna*`. A single Bleak client/connection is shared for status notifications and command writes.

## Status frame (device → host, on FFF1 and FFF2)

22 bytes, `AA … CC` framing.

| Byte(s) | Field | Values | Confidence |
| ------- | ----- | ------ | ---------- |
| 0 | Start | `0xAA` | verified |
| 1 | Power | `0x00` OFF, `0x01` ON | observed |
| 2–3 | Remaining time | Minutes, decimal-as-hex; both bytes match | verified |
| 4 | Current temperature | °C | verified |
| 5 | Target temperature | °C | verified |
| 6–12 | Unknown | Light/RGB write-side only; never read back | unknown |
| 13 | Volume | 1–20 | observed |
| 14 | FM on | `0x00`/`0x01` | observed |
| 15 | BT on | `0x00`/`0x01` | observed |
| 16 | USB on | `0x00`/`0x01` | observed |
| 17 | Work mode indicator | present, unused by any entity | unknown |
| 18 | Unit | `0x00` Celsius, non-zero Fahrenheit | observed |
| 19–20 | Unknown | — | unknown |
| 21 | End | `0xCC` | verified |

## Command frame (host → device, write on FFF1)

22 bytes, `AA … CC` framing, all bytes zero except start/end and exactly **one** target byte.

| Byte | Value |
| ---- | ----- |
| 0 | `0xAA` |
| 1–20 | all `0x00` except one byte set per command below |
| 21 | `0xCC` |

### Command byte indices

| Byte index | Function | Value semantics | Confidence |
| ---------- | -------- | ---------------- | ---------- |
| 1 | Power | `0x01` = toggle (no explicit OFF) | verified |
| 3 | Timer | `0x01` = step up, `0x02` = step down | verified |
| 5 | Target temperature | `0x01` = step up, `0x02` = step down | verified |
| 6 | Outside light | `0x01` = toggle | verified |
| 7 | Inside light | `0x01` = toggle | verified |
| 8 | RGB | `0x01` = cycle | verified |
| 13 | Volume | `1`–`20` absolute | unconfirmed |
| 14 | FM | `0x01` = toggle | verified |
| 15 | BT | `0x01` = toggle (see audio source below) | unconfirmed |
| 16 | USB | `0x01` = toggle (see audio source below) | unconfirmed |
| 18 | Unit | `0x01` = toggle Celsius/Fahrenheit | verified |

### Notes

- **No absolute set** exists for power, timer, or target temperature — only relative step/toggle commands. Absolute set is faked in software by sending repeated step commands.
- **Power has no explicit OFF byte.** Sending the power command always toggles; the caller must gate on the last known status to avoid turning the device on when it is already off, or vice versa.
- **Audio source is a swap, not two independent switches.** The app sends byte 16 (USB) when BT is currently on, and byte 15 (BT) when USB/other is current. There is no independent on/off per source.
- Bytes 6–12 (light/RGB detail) are write-only from the app's perspective; the status frame never reflects light/RGB state back, so no read-side entity can be derived from them.
- Read side: remaining time and current/target temperature (status frame bytes 2–5) have been confirmed to decode correctly against real hardware (`KDYSauna-10`).
- Write side: power, timer, target temperature, outside light, inside light, RGB, FM, and unit toggle have been confirmed against real hardware. Volume, BT, and USB remain decompiled-app values only, not yet confirmed.
