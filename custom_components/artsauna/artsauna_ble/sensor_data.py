DEVICE_STATE_BYTE_POSITION = -9
HEATING_STATE_BYTE_POSITION = -8
CURRENT_TEMP_BYTE_POSITION = -7
TARGET_TEMP_BYTE_POSITION = -6
TIME_BYTE_POSITION = -5
UNIT_BYTE_POSITION = -4
VOLUME_BYTE_POSITION = -3
LIGHTING_BYTE_POSITION = -2
CHECKSUM_BYTE_POSITION = -1
CHECKSUM_BYTES_SLICE = slice(2, -1)
FM_FREQUENCY_BYTES_SLICE = slice(-2, None)

UNIT_BYTES_MAP = {0: "Celsius", 1: "Fahrenheit"}
DEVICE_STATE_BYTES_MAP = {5: "OFF", 4: "ON", 0: "RADIO", 1: "AUX/BT", 3: "USB"}
HEATING_BYTES_MAP = {0: "No Info", 1: "ON", 2: "OFF"}
LIGHTING_HEX_1_MAP = {
    0: "OFF",
    1: "External",
    2: "Internal",
    3: "External & Internal",
}
RGB_LIGHTING_HEX_2_MAP = {
    0: "LED02: White",
    1: "LED03: Green",
    3: "LED05: Blue",
    2: "LED04: Red",
    4: "LED06: Purple",
    5: "LED07: Cyan",
    6: "LED08: OFF",
    7: "LED09: Rainbow",
    8: "LED01: White",
}


def validate(data: bytes) -> bool:
    return sum(data[CHECKSUM_BYTES_SLICE]) % 256 == int(data[CHECKSUM_BYTE_POSITION])


def target_temp(data: bytes) -> int:
    return int(data[TARGET_TEMP_BYTE_POSITION])


def device_state(data: bytes) -> str:
    return DEVICE_STATE_BYTES_MAP[int(data[DEVICE_STATE_BYTE_POSITION])]


def heating_state(data: bytes) -> str:
    return HEATING_BYTES_MAP[int(data[HEATING_STATE_BYTE_POSITION])]


def time(data: bytes) -> int:
    return int(data[TIME_BYTE_POSITION])


def current_temp(data: bytes) -> int:
    return int(data[CURRENT_TEMP_BYTE_POSITION])


def unit(data: bytes) -> str:
    return UNIT_BYTES_MAP[int(data[UNIT_BYTE_POSITION])]


def rgb_lighting(data: bytes) -> str:
    return RGB_LIGHTING_HEX_2_MAP[int(data[LIGHTING_BYTE_POSITION].to_bytes().hex()[1])]


def lighting(data: bytes) -> str:
    return LIGHTING_HEX_1_MAP[int(data[LIGHTING_BYTE_POSITION].to_bytes().hex()[0]) % 4]


def volume(data: bytes) -> int:
    return int(data[VOLUME_BYTE_POSITION])


def fm_frequency(data: bytes) -> float:
    return int.from_bytes(data[FM_FREQUENCY_BYTES_SLICE]) / 100.0
