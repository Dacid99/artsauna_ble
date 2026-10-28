# Artsauna (HiMaterial CS-128) BLE Protocol

Derived from this integration’s implementation and hardware fixtures against
Artsauna infrared cabins advertising as `SAUNA*` (e.g. `SAUNA-OSLO`). Additional
command dumps that are not used here come from
[Samurai1201/Artsauna-BLE](https://github.com/Samurai1201/Artsauna-BLE) and are
marked **upstream only**.

## GATT layout

| UUID                                   | Short | Properties (upstream scan) | Purpose                          |
| -------------------------------------- | ----- | -------------------------- | -------------------------------- |
| `0000ae00-0000-1000-8000-00805f9b34fb` | AE00  | Primary service            | Artsauna service                 |
| `0000ae01-0000-1000-8000-00805f9b34fb` | AE01  | Write                      | Command channel                  |
| `0000ae02-0000-1000-8000-00805f9b34fb` | AE02  | Read                       | Unused in this integration       |
| `0000ae03-0000-1000-8000-00805f9b34fb` | AE03  | Notify                     | Status + FM frequency notifies   |

Device advertises as `SAUNA*`. One Bleak client is shared for auth, command
writes on AE01, and notifications on AE03.

## Session / auth

On connect:

1. Establish GATT connection
2. Write auth: `FF AA 05 41 53 4F 4B 33` (`FF AA 05` + ASCII `ASOK3`)
3. Wait ~100 ms
4. Subscribe to notifications on AE03

Auth uses the same `FF AA` + length framing as commands but carries the ASCII
payload `ASOK3` and **no checksum byte**.

## Command frame (host → device, write on AE01)

8 bytes for fixed toggles / steps; volume and RGB append a parameter then
checksum.


| Byte | Meaning                                      |
| ---- | -------------------------------------------- |
| 0–1  | Start `FF AA`                                |
| 2    | Length `0x05` (payload including checksum)   |
| 3–4  | Tag `5A 47` = ASCII `"ZG"`                   |
| 5    | Command ID                                   |
| 6    | Parameter                                    |
| 7    | Checksum = `sum(bytes[2:7]) % 256`           |


### Commands used by this integration


| Function           | Cmd | Param        | Hex example            |
| ------------------ | --- | ------------ | ---------------------- |
| Auth               | —   | `ASOK3`      | `ffaa0541534f4b33`     |
| Toggle heating     | `00`| `02`         | `ffaa055a470002a8`     |
| Toggle FM / search | `01`| `00`         | `ffaa055a470100a7`     |
| Toggle BT          | `02`| `00`         | `ffaa055a470200a8`     |
| Toggle USB         | `03`| `00`         | `ffaa055a470300a9`     |
| Toggle AUX         | `04`| `00`         | `ffaa055a470400aa`     |
| Toggle unit °C/°F  | `05`| `00`         | `ffaa055a470500ab`     |
| Temp up            | `06`| `00`         | `ffaa055a470600ac`     |
| Temp down          | `07`| `00`         | `ffaa055a470700ad`     |
| Time up            | `08`| `00`         | `ffaa055a470800ae`     |
| Time down          | `09`| `00`         | `ffaa055a470900af`     |
| Set RGB            | `0A`| `00`–`08`    | see RGB table          |
| Toggle external light | `0B` | `00`      | `ffaa055a470b00b1`     |
| Toggle internal light | `0C` | `00`      | `ffaa055a470c00b2`     |
| Set volume         | `0D`| absolute 0–40| `ffaa055a470d` + vol + chk |
| Toggle power       | `0E`| `00`         | `ffaa055a470e00b4`     |

USB and AUX commands are defined in code; this integration does not expose HA
entities for them.

### RGB wire parameters (`cmd 0A`)


| Wire param | Hex (full packet)   | Name    | Status-frame internal ID |
| ---------- | ------------------- | ------- | ------------------------ |
| `00`       | `ffaa055a470a00b0`  | White   | 8                        |
| `01`       | `ffaa055a470a01b1`  | Green   | 0                        |
| `02`       | `ffaa055a470a02b2`  | Red     | 1                        |
| `03`       | `ffaa055a470a03b3`  | Blue    | 2                        |
| `04`       | `ffaa055a470a04b4`  | Yellow  | 3                        |
| `05`       | `ffaa055a470a05b5`  | Cyan    | 4                        |
| `06`       | `ffaa055a470a06b6`  | Pink    | 5                        |
| `07`       | `ffaa055a470a07b7`  | OFF     | 6                        |
| `08`       | `ffaa055a470a08b8`  | Rainbow | 7                        |

Wire index and status-frame RGB nibble are **not** the same numbering. The
integration maps between them via an internal bidict.

### Upstream only (not sent by this integration)


| Hex                  | Meaning                                      |
| -------------------- | -------------------------------------------- |
| `ffaa055a470001a7`   | Heating OFF (cmd `00`, param `01`)           |
| `ffaa055a470a09b9`   | RGB wire param `09` (9th mode; unused here)  |

This integration always sends heating as param `02` (“ON” / toggle-style), for
both turn-on and turn-off of the heating switch.

## Status frame (device → host, notify on AE03)

14 bytes, `FF AA` framing, checksummed.


| Byte(s) | Field               | Values / notes                                      |
| ------- | ------------------- | --------------------------------------------------- |
| 0–1     | Start               | `FF AA`                                             |
| 2       | Length              | `0x0B`                                              |
| 3–4     | Tag                 | `5A 47` (`"ZG"`)                                    |
| 5       | Device state        | `5` OFF, `4` ON, `0` RADIO, `1` AUX/BT, `3` USB     |
| 6       | Heating             | `0` no info, `1` ON, `2` OFF                        |
| 7       | Current temperature | Integer in the active unit                          |
| 8       | Target temperature  | Integer in the active unit                          |
| 9       | Remaining time      | Minutes                                             |
| 10      | Unit                | `0` Celsius, `1` Fahrenheit                         |
| 11      | Volume              | Typically 0–40                                      |
| 12      | Light + RGB         | Packed nibble (below)                               |
| 13      | Checksum            | `sum(bytes[2:13]) % 256`                            |

Notifications may arrive fragmented; the adapter buffers until a full
`FF AA` + 12-byte match is found, then validates the checksum.

### Light byte (byte 12)

Interpreted as two hex digits of the single byte:

- High nibble `% 4` → light mode: `0` OFF, `1` external, `2` internal, `3` both
- Low nibble → RGB **internal** ID (see RGB table above)

### Captured example

```
ffaa0b5a470501103c41000b4892
```

| Field        | Value                          |
| ------------ | ------------------------------ |
| State        | `05` → OFF                     |
| Heating      | `01` → ON                      |
| Current temp | `16`                           |
| Target temp  | `60`                           |
| Time         | `65` min                       |
| Unit         | `00` Celsius                   |
| Volume       | `11`                           |
| Light byte   | `48` → lights OFF, RGB White   |
| Checksum     | `92` (valid)                   |

## FM notification (device → host, notify on AE03)

6 bytes, no checksum, separate from the status frame.


| Byte(s) | Meaning                                              |
| ------- | ---------------------------------------------------- |
| 0–3     | Fixed prefix `42 02 03 00`                            |
| 4–5     | Big-endian uint16; frequency MHz = value / 100       |

Example: `420203002706` → `0x2706` = 9990 → **99.9 MHz**.

## Notes

- **No absolute set** for power, heating, temperature, or timer — only toggles
  and relative steps (except volume and RGB, which are absolute).
- **Power “on”** in software means device state ≠ `5` (OFF); RADIO / AUX/BT /
  USB / ON all count as powered on.
- **Heating writes** always use param `02`; upstream documents a distinct OFF
  packet (`00 01`) that this integration does not send.
- **Auth (`ASOK3`)** is required by this stack before reliable notifications.
- Service UUID `AE00` is documented from upstream GATT scans; this repo only
  hard-codes AE01 (write) and AE03 (notify).
