from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ArtsaunaState:
    """State of the Artsauna as communicated via BLE.

    Note:
        The artsauna internal values are used.
        It is the job of protocols using this dataclass to make sense of them.
    """

    power_on: bool = False
    heating_on: int = 0
    target_temp: int = 0
    current_temp: int = 0
    remaining_time: int = 0
    volume: int = 0
    lighting: int = 0
    rgb: int = 0
    fm_frequency: int = 0
    unit_is_celsius: bool = True

    def update_from_data(self, data: bytes) -> None:
