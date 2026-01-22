# Artsauna BLE Integration for HomeAssistant

[![License](https://img.shields.io/github/license/Dacid99/artsauna_ble)](LICENSE)
[![HACS Supported](https://img.shields.io/badge/HACS-Supported-03a9f4)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Dacid99&repository=artsauna_ble&category=integration)
[![Downloads](https://img.shields.io/github/downloads/Dacid99/artsauna_ble/total)](https://github.com/Dacid99/artsauna_ble/releases)
[![Translation status](https://hosted.weblate.org/widget/artsauna_ble/svg-badge.svg)](https://hosted.weblate.org/engage/artsauna_ble/)

This free and open-source integration allows you to control your Artsauna Device via HomeAssistant.

It has been developed for and tested with an Artsauna Infrared Cabin Type Oslo.

The controller used is marked as CS-128 and is most likely manufactured by china-based HiMaterial. 

## Features

You can control the Artsauna the same way the proprietary app would allow you to.

All relevant datapoints the sauna BLE exposes are mapped to HA entities.

Sensors:
- Target and current temperature
- Remaining time
- Current radio frequency
- RGB light color

Switches:
- Power and heating state
- Audio input and radio search mode
- Lights

Buttons:
- In- and decrease target temperature and time
- Cycle RGB light color

Numbers:
- Set audio volume

### Known quirks

- Heating is always reported as ON when the sauna power is switched to ON.

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Dacid99&repository=artsauna_ble&category=integration)

[![Add integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=artsauna_ble)

or install manually on your server by running these commmands

```bash
git clone https://github.com/dacid99/Artsauna-ble.git
cp -r Artsauna-ble/custom_components/Artsauna_ble <ha_root>/custom_components/
```

or copying the contents manually with a filebrowser of your choice.

## Translation

You'd like to help with the translation of this project?

You can do this by going to [Weblate](https://hosted.weblate.org/projects/artsauna_ble/) and add your language!

## Contributing

If you encounter any issue with this integration please let us know via the issues section of this repo!

We welcome pull requests, especially if they extend the number of Artsauna products that this integration can be used for!

## Thank-yous and References

- [Wireshark](https://www.wireshark.org/)
- [LD2450 HA Integration](https://github.com/MassiPi/ld2450_ble/), which served as template for the bluetooth connection components
- [Samurai1202's reverse-engineering of the BLE interface](https://github.com/Samurai1201/Artsauna-BLE), which was the foundation for this project

## Disclaimer

The developers of this integration are not affiliated with Artsauna or HiMaterial. 
They have created the integration as open source in their spare time on the basis of publicly accessible information. 
The use of the integration is at the user's own risk and responsibility. 
The developers are not liable for any damages arising from the use of the integration.
