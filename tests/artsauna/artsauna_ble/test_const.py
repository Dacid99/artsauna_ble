import re

from custom_components.artsauna_ble.artsauna_ble import const


def test_STATE_NOTIFICATION_REGEX():
    assert re.search(
        const.STATE_NOTIFICATION_REGEX, b"\xff\xaa\x0bZG\x05\x01\x10<A\x00\x0bH\x92"
    )


def test_FM_NOTIFICATION_REGEX():
    assert re.search(const.FM_NOTIFICATION_REGEX, b"B\x02\x03\x00)\xae")
