import const
import utils


def validate(data: bytes) -> bool:
    return sum(data[const.CHECKSUM_BYTES_SLICE]) % 256 == int(
        data[const.CHECKSUM_BYTE_POSITION]
    )


def target_temp(data: bytes) -> int:
    return int(data[const.TARGET_TEMP_BYTE_POSITION])


def device_state(data: bytes) -> str:
    return const.DEVICE_STATE_BYTES_MAP[int(data[const.DEVICE_STATE_BYTE_POSITION])]


def heating_state(data: bytes) -> str:
    return const.HEATING_BYTES_MAP[int(data[const.HEATING_STATE_BYTE_POSITION])]


def time(data: bytes) -> int:
    return int(data[const.TIME_BYTE_POSITION])


def current_temp(data: bytes) -> int:
    return int(data[const.CURRENT_TEMP_BYTE_POSITION])


def unit(data: bytes) -> str:
    return const.UNIT_BYTES_MAP[int(data[const.UNIT_BYTE_POSITION])]


def rgb_lighting(data: bytes) -> str:
    internal_rgb = int(data[const.LIGHTING_BYTE_POSITION].to_bytes().hex()[1])
    return utils.external_rgb_to_color_led_label(
        utils.internal_to_external_rgb(internal_rgb)
    )


def lighting(data: bytes) -> str:
    return const.LIGHTING_HEX_1_MAP[
        int(data[const.LIGHTING_BYTE_POSITION].to_bytes().hex()[0]) % 4
    ]


def is_light_on(data: bytes) -> bool:
    return lighting(data) != "OFF" or rgb_lighting(data) != "OFF"


def volume(data: bytes) -> int:
    return int(data[const.VOLUME_BYTE_POSITION])


def fm_frequency(data: bytes) -> float:
    return int.from_bytes(data[const.FM_FREQUENCY_BYTES_SLICE]) / 100.0
