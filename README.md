# Artsauna BLE Integration for HomeAssistant

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

Get it on HACS

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
