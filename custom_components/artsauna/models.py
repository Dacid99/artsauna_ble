"""The ld2450 ble integration models."""

from __future__ import annotations

from dataclasses import dataclass

from .artsauna_ble import ArtsaunaBLE
from .coordinator import ArtsaunaBLECoordinator


@dataclass
class ArtsaunaBLEData:
    """Data for the artsauna ble integration."""

    title: str
    device: ArtsaunaBLE
    coordinator: ArtsaunaBLECoordinator
