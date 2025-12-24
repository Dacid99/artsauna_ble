import const


def construct_volume_cmd_data(volume: int) -> bytes:
    data = const.CMD_VOLUME_PREFIX + bytes([volume])
    data += bytes([sum(data[2:])])
    return data


def construct_rgb_cmd_data(rgb: int) -> bytes:
    data = const.CMD_RGB_PREFIX + bytes([rgb + const.CMD_RGB_OFFSET])
    return data


def internal_to_external_rgb(internal_rgb: int):
    return (internal_rgb - 2) % 9


def external_to_internal_rgb(external_rgb: int):
    return (external_rgb + 2) % 9


def external_rgb_to_color_led_label(external_rgb):
    return f"LED0{external_rgb}: {const.EXTERNAL_RGB_COLOR_MAP[external_rgb]}"
