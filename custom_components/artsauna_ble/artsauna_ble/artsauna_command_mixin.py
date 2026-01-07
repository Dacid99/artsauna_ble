from . import utils
from .const import (
    CMD_APP_AUTH,
    CMD_TEMP_DOWN,
    CMD_TEMP_UP,
    CMD_TIME_DOWN,
    CMD_TIME_UP,
    CMD_TOGGLE_AUX,
    CMD_TOGGLE_BT,
    CMD_TOGGLE_EXTERNAL_LIGHT,
    CMD_TOGGLE_FM,
    CMD_TOGGLE_HEATING,
    CMD_TOGGLE_INTERNAL_LIGHT,
    CMD_TOGGLE_POWER,
    CMD_TOGGLE_UNIT,
    CMD_TOGGLE_USB,
)


class ArtsaunaBLECommandMixin:
    async def send_auth(self):
        return await self._send_command(CMD_APP_AUTH)

    async def send_toggle_power(self):
        return await self._send_command(CMD_TOGGLE_POWER)

    async def send_toggle_heating(self):
        return await self._send_command(CMD_TOGGLE_HEATING)

    async def send_temp_up(self):
        return await self._send_command(CMD_TEMP_UP)

    async def send_temp_down(self):
        return await self._send_command(CMD_TEMP_DOWN)

    async def send_time_up(self):
        return await self._send_command(CMD_TIME_UP)

    async def send_time_down(self):
        return await self._send_command(CMD_TIME_DOWN)

    async def send_toggle_internal_light(self):
        return await self._send_command(CMD_TOGGLE_INTERNAL_LIGHT)

    async def send_toggle_external_light(self):
        return await self._send_command(CMD_TOGGLE_EXTERNAL_LIGHT)

    async def send_toggle_unit(self):
        return await self._send_command(CMD_TOGGLE_UNIT)

    async def send_toggle_fm(self):
        return await self._send_command(CMD_TOGGLE_FM)

    async def send_toggle_bt(self):
        return await self._send_command(CMD_TOGGLE_BT)

    async def send_toggle_aux(self):
        return await self._send_command(CMD_TOGGLE_AUX)

    async def send_toggle_usb(self):
        return await self._send_command(CMD_TOGGLE_USB)

    async def send_set_rgb(self, rgb: int):
        cmd_data = utils.construct_rgb_cmd_data(rgb)
        return await self._send_command(cmd_data)

    async def send_set_volume(self, volume: int):
        cmd_data = utils.construct_volume_cmd_data(volume)
        return await self._send_command(cmd_data)
