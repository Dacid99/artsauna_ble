# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Artsauna-BLE - integration for Home Assistant
# Copyright (C) 2025 David & Philipp Aderbauer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import pytest
import sensor_data


@pytest.fixture
def data():
    return bytes.fromhex("ffaa0b5a470501103c41000b4892")


@pytest.fixture
def radio_data():
    return bytes.fromhex("420203002706")


def test_validate(data):
    assert sensor_data.validate(data)


def test_time(data):
    assert sensor_data.time(data) == 65


def test_volume(data):
    assert sensor_data.volume(data) == 11


def test_current_temp(data):
    assert sensor_data.current_temp(data) == 16


def test_target_temp(data):
    assert sensor_data.target_temp(data) == 60


def test_unit(data):
    assert sensor_data.unit(data) == "Celsius"


def test_device_state(data):
    assert sensor_data.device_state(data) == "OFF"


def test_rgb_lighting(data):
    assert sensor_data.rgb_lighting(data) == "LED01: White"


def test_lighting(data):
    assert sensor_data.lighting(data) == "OFF"


def test_heating_state(data):
    assert sensor_data.heating_state(data) == "ON"


def test_fm_frequency(radio_data):
    assert sensor_data.fm_frequency(radio_data) == 99.9
