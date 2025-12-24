from uuid import UUID

CHARACTERISTIC_WRITE = UUID("0000ae01-0000-1000-8000-00805f9b34fb")
CHARACTERISTIC_NOTIFY = UUID("0000ae03-0000-1000-8000-00805f9b34fb")

CMD_APP_AUTH = b"\xff\xaa\x05ASOK3"
CMD_TOGGLE_POWER = b"\xff\xaa\x05ZG\x0e\x00\xb4"
CMD_TOGGLE_HEATING = b"\xff\xaa\x05ZG\x00\x02\xa8"
CMD_TEMP_UP = b"\xff\xaa\x05ZG\x06\x00\xac"
CMD_TEMP_DOWN = b"\xff\xaa\x05ZG\x06\x00\xac"
CMD_VOLUME_PREFIX = b"\xff\xaa\x05ZG\r"
CMD_TIME_UP = b"\xff\xaa\x05ZG\x08\x00\xae"
CMD_TIME_DOWN = b"\xff\xaa\x05ZG\t\x00\xaf"
CMD_RGB_PREFIX = b"\xff\xaa\x05ZG\n\x00"
CMD_RGB_OFFSET = 177  # 11*16 + 1 , 0xb1 , based on external rgb id
CMD_RGB_1 = b"\xff\xaa\x05ZG\n\x00\xb0"
CMD_RGB_2 = b"\xff\xaa\x05ZG\n\x00\xb1"
CMD_RGB_3 = b"\xff\xaa\x05ZG\n\x00\xb2"
CMD_RGB_4 = b"\xff\xaa\x05ZG\n\x00\xb3"
CMD_RGB_5 = b"\xff\xaa\x05ZG\n\x00\xb4"
CMD_RGB_6 = b"\xff\xaa\x05ZG\n\x00\xb5"
CMD_RGB_7 = b"\xff\xaa\x05ZG\n\x00\xb6"
CMD_RGB_8 = b"\xff\xaa\x05ZG\n\x00\xb7"
CMD_RGB_9 = b"\xff\xaa\x05ZG\n\x00\xb8"
CMD_RGB_WHITE = CMD_RGB_1
CMD_RGB_GREEN = CMD_RGB_2
CMD_RGB_RED = CMD_RGB_3
CMD_RGB_BLUE = CMD_RGB_4
CMD_RGB_YELLOW = CMD_RGB_5
CMD_RGB_CYAN = CMD_RGB_6
CMD_RGB_PINK = CMD_RGB_7
CMD_RGB_OFF = CMD_RGB_8
CMD_RGB_RAINBOW = CMD_RGB_9
CMD_TOGGLE_EXTERNAL_LIGHT = b"\xff\xaa\x05ZG\x0b\x00\xb1"
CMD_TOGGLE_INTERNAL_LIGHT = b"\xff\xaa\x05ZG\x0b\x00\xb2"
CMD_TOGGLE_FM = b"\xff\xaa\x05ZG\x01\x00\xa7"
CMD_TOGGLE_BT = "b\xff\xaa\x05ZG\x02\x00\xa8"
CMD_TOGGLE_AUX = b"\xff\xaa\x05ZG\x04\x00\xaa"
CMD_TOGGLE_USB = b"\xff\xaa\x05ZG\x03\x00\xa9"
CMD_TOGGLE_UNIT = b"\xff\xaa\x05ZG\x05\x00\xab"

DEVICE_STATE_BYTE_POSITION = -9
HEATING_STATE_BYTE_POSITION = -8
CURRENT_TEMP_BYTE_POSITION = -7
TARGET_TEMP_BYTE_POSITION = -6
TIME_BYTE_POSITION = -5
UNIT_BYTE_POSITION = -4
VOLUME_BYTE_POSITION = -3
LIGHTING_BYTE_POSITION = -2
CHECKSUM_BYTE_POSITION = -1
CHECKSUM_BYTES_SLICE = slice(-13, -1)
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
EXTERNAL_RGB_COLOR_MAP = {
    1: "White",
    2: "Green",
    3: "Red",
    4: "Blue",
    5: "Yellow",
    6: "Cyan",
    7: "Pink",
    8: "OFF",
    9: "Rainbow",
}
