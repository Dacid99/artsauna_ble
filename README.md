# Artsauna BLE Integration for HomeAssistant 

icon

This free and open-source integration allows you to control your Artsauna Device via HomeAssistant.

It has been developed for and tested with an Artsauna Infrared Cabin Type xxxxxxxx.

The controller used is marked as CS-128 and is most likely manufactured by china-based HiMaterial. 

## Features

You can control the Artsauna the same way the proprietary app would allow you to.

All relevant datapoints the sauna BLE exposes are mapped to HA entities.

Sensors:
- Target and current temperature
- Remaining time
- Current radio frequency

Switches:
- Power and heating state
- Audio input and radio search mode
- Lights

Buttons:
- In- and decrease target temperature and time

Numbers:
- Set audio volume

Selects:
- RGB light color

## Installation

Get it on HACS (image with link)

or install manually on your server:

By running these commmandss
```bash
git clone https://github.com/SBV/artsauna-ble.git
cp -r artsauna-ble/custom_components/artsauna_ble <ha_root>/custom_components/
```
or copying the contents manually   
## Contributing

If you encounter any issue with this integration please let us know via the issues section of this repo!

We welcome pull requests, especially if they extend the number of artsauna products that this integration can be used for!

## Thankyous and References

- Wireshark (https://www.wireshark.org/)
- https://github.com/MassiPi/ld2450_ble/ , which served as template for the bluetooth connection components
- https://github.com/Samurai1201/Artsauna-BLE
