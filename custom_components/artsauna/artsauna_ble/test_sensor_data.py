import pytest
import sensor_data


@pytest.fixture
def data():
    return bytes.fromhex("ffaa0b5a470501103c41000b4892")


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
    assert sensor_data.device_state(data) == "ON"


def test_rgb_lighting(data):
    assert sensor_data.rgb_lighting(data) == "White"


def test_lighting(data):
    assert sensor_data.lighting(data) == "OFF"


def test_heating_state(data):
    assert sensor_data.heating_state(data) == "ON"
