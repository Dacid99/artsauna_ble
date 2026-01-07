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

"""Config flow for ArtsaunaBLE integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from bleak_retry_connector import BLEAK_EXCEPTIONS
from bluetooth_data_tools import human_readable_name
from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.const import CONF_ADDRESS

from .artsauna_ble import ArtsaunaBLEAdapter
from .const import DOMAIN, LOCAL_NAMES

_LOGGER = logging.getLogger(__name__)


class ArtsaunaBLEConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for artsauna BLE."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_devices: dict[str, BluetoothServiceInfoBleak] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> config_entries.ConfigFlowResult:
        """Handle the bluetooth discovery step."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self._discovery_info = discovery_info
        self.context["title_placeholders"] = {
            "name": human_readable_name(
                None, discovery_info.name, discovery_info.address
            )
        }
        return await self.async_step_user()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the user step to pick discovered device."""
        errors: dict[str, str] = {}

        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            discovery_info = self._discovered_devices[address]
            local_name = discovery_info.name
            await self.async_set_unique_id(
                discovery_info.address, raise_on_progress=False
            )
            self._abort_if_unique_id_configured()
            artsauna_ble = ArtsaunaBLEAdapter(discovery_info.device)
            try:
                await artsauna_ble.initialise()
            except BLEAK_EXCEPTIONS:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected error")
                errors["base"] = "unknown"
            else:
                await artsauna_ble.stop()
                return self.async_create_entry(
                    title=local_name,
                    data={
                        CONF_ADDRESS: discovery_info.address,
                    },
                )

        if discovery := self._discovery_info:
            self._discovered_devices[discovery.address] = discovery
        else:
            current_addresses = self._async_current_ids()
            for discovery in async_discovered_service_info(self.hass):
                if (
                    discovery.address in current_addresses
                    or discovery.address in self._discovered_devices
                ):
                    continue
                self._discovered_devices[discovery.address] = discovery

        if not self._discovered_devices:
            return self.async_abort(reason="no_devices_found")

        data_schema = vol.Schema(
            {
                vol.Required(CONF_ADDRESS): vol.In(
                    {
                        service_info.address: f"{service_info.name} ({service_info.address})"
                        for service_info in self._discovered_devices.values()
                    }
                ),
            }
        )
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )


# """Config flow for the artsauna-bt integration."""

# from __future__ import annotations

# import logging
# from typing import Any

# import voluptuous as vol

# from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
# from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
# from homeassistant.core import HomeAssistant
# from homeassistant.exceptions import HomeAssistantError

# from .const import DOMAIN

# _LOGGER = logging.getLogger(__name__)

# # TODO adjust the data schema to the data that you need
# STEP_USER_DATA_SCHEMA = vol.Schema(
#     {
#         vol.Required(CONF_HOST): str,
#         vol.Required(CONF_USERNAME): str,
#         vol.Required(CONF_PASSWORD): str,
#     }
# )


# class PlaceholderHub:
#     """Placeholder class to make tests pass.

#     TODO Remove this placeholder class and replace with things from your PyPI package.
#     """

#     def __init__(self, host: str) -> None:
#         """Initialize."""
#         self.host = host

#     async def authenticate(self, username: str, password: str) -> bool:
#         """Test if we can authenticate with the host."""
#         return True


# async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
#     """Validate the user input allows us to connect.

#     Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
#     """
#     # TODO validate the data can be used to set up a connection.

#     # If your PyPI package is not built with async, pass your methods
#     # to the executor:
#     # await hass.async_add_executor_job(
#     #     your_validate_func, data[CONF_USERNAME], data[CONF_PASSWORD]
#     # )

#     hub = PlaceholderHub(data[CONF_HOST])

#     if not await hub.authenticate(data[CONF_USERNAME], data[CONF_PASSWORD]):
#         raise InvalidAuth

#     # If you cannot connect:
#     # throw CannotConnect
#     # If the authentication is wrong:
#     # InvalidAuth

#     # Return info that you want to store in the config entry.
#     return {"title": "Name of the device"}


# class ConfigFlow(ConfigFlow, domain=DOMAIN):
#     """Handle a config flow for artsauna-bt."""

#     VERSION = 1

#     async def async_step_user(
#         self, user_input: dict[str, Any] | None = None
#     ) -> ConfigFlowResult:
#         """Handle the initial step."""
#         errors: dict[str, str] = {}
#         if user_input is not None:
#             try:
#                 info = await validate_input(self.hass, user_input)
#             except CannotConnect:
#                 errors["base"] = "cannot_connect"
#             except InvalidAuth:
#                 errors["base"] = "invalid_auth"
#             except Exception:
#                 _LOGGER.exception("Unexpected exception")
#                 errors["base"] = "unknown"
#             else:
#                 return self.async_create_entry(title=info["title"], data=user_input)

#         return self.async_show_form(
#             step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
#         )


# class CannotConnect(HomeAssistantError):
#     """Error to indicate we cannot connect."""


# class InvalidAuth(HomeAssistantError):
#     """Error to indicate there is invalid auth."""
