# KDY Sauna BLE Protocol

Reverse-engineered from the decompiled vendor app and hardware captures against `KDYSauna-10`. 

## GATT layout


| UUID                                   | Short | Properties                     | Purpose                                   |
| -------------------------------------- | ----- | ------------------------------ | ----------------------------------------- |
| `0000fff0-0000-1000-8000-00805f9b34fb` | FFF0  | Service                        | KDY service                               |
| `0000fff1-0000-1000-8000-00805f9b34fb` | FFF1  | Write-without-response, Notify | Command channel; also emits status frames |
| `0000fff2-0000-1000-8000-00805f9b34fb` | FFF2  | Read, Notify                   | Status channel                            |
| `0000fff3-0000-1000-8000-00805f9b34fb` | FFF3  | Write-without-response         | Unused (phase 1)                          |


Device advertises as `KDYSauna*`. A single Bleak client/connection is shared for status notifications and command writes.

## Status frame (device → host, on FFF1 and FFF2)

22 bytes, `AA … CC` framing.


| Byte(s) | Field               | Values                                     |
| ------- | ------------------- | ------------------------------------------ |
| 0       | Start               | `0xAA`                                     |
| 1       | Power               | `0x00` OFF, `0x01` ON                      |
| 2–3     | Remaining time      | Minutes, decimal-as-hex; both bytes match  |
| 4       | Current temperature | °C                                         |
| 5       | Target temperature  | °C                                         |
| 6–12    | Unknown             | Light/RGB write-side only; never read back |
| 13      | Volume              | 1–20                                       |
| 14      | FM on               | `0x00`/`0x01`                              |
| 15      | BT on               | `0x00`/`0x01`                              |
| 16      | USB on              | `0x00`/`0x01`                              |
| 17      | Work mode indicator | present, unused by any entity              |
| 18      | Unit                | `0x00` Celsius, non-zero Fahrenheit        |
| 19–20   | Unknown             | —                                          |
| 21      | End                 | `0xCC`                                     |




## Command frame (host → device, write on FFF1)

22 bytes, `AA … CC` framing, all bytes zero except start/end and exactly **one** target byte.


| Byte | Value                                            |
| ---- | ------------------------------------------------ |
| 0    | `0xAA`                                           |
| 1–20 | all `0x00` except one byte set per command below |
| 21   | `0xCC`                                           |




### Command byte indices


| Byte index | Function           | Value semantics                          |
| ---------- | ------------------ | ---------------------------------------- |
| 1          | Power              | `0x01` = toggle (no explicit OFF)        |
| 3          | Timer              | `0x01` = step up, `0x02` = step down     |
| 5          | Target temperature | `0x01` = step up, `0x02` = step down     |
| 6          | Outside light      | `0x01` = toggle                          |
| 7          | Inside light       | `0x01` = toggle                          |
| 8          | RGB                | `0x01` = cycle                           |
| 13         | Volume             | `1`–`20` absolute                        |
| 14         | FM                 | `0x01` = toggle                          |
| 15         | BT                 | `0x01` = toggle (see audio source below) |
| 16         | USB                | `0x01` = toggle (see audio source below) |
| 18         | Unit               | `0x01` = toggle Celsius/Fahrenheit       |




### Notes

- **No absolute set** exists for power, timer, or target temperature — only relative step/toggle commands. Absolute set is faked in software by sending repeated step commands.
- **Power has no explicit OFF byte.** Sending the power command always toggles; the caller must gate on the last known status to avoid turning the device on when it is already off, or vice versa.
- **Audio source is a swap, not two independent switches.** The app sends byte 16 (USB) when BT is currently on, and byte 15 (BT) when USB/other is current. There is no independent on/off per source.
- Bytes 6–12 (light/RGB detail) are write-only from the app's perspective; the status frame never reflects light/RGB state back, so no read-side entity can be derived from them.

