"""Window for Hyundai / Kia Connect integration."""
from __future__ import annotations

import logging

from homeassistant.components.cover import (
    CoverEntity,
    CoverDeviceClass,
    WindowsRequestOptions,
    WINDOW_STATE,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from hyundai_kia_connect_api import Vehicle
from .const import DOMAIN
from .coordinator import HyundaiKiaConnectDataUpdateCoordinator
from .entity import HyundaiKiaConnectEntity


_LOGGER = logging.getLogger(__name__)
OPEN_WINDOW_OPTIONS = WindowsRequestOptions(
    back_left=WINDOW_STATE.OPEN,
    back_right=WINDOW_STATE.OPEN,
    front_left=WINDOW_STATE.OPEN,
    front_right=WINDOW_STATE.OPEN,
)
CLOSE_WINDOW_OPTIONS = WindowsRequestOptions(
    back_left=WINDOW_STATE.CLOSED,
    back_right=WINDOW_STATE.CLOSED,
    front_left=WINDOW_STATE.CLOSED,
    front_right=WINDOW_STATE.CLOSED,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][config_entry.unique_id]
    entities = []
    for vehicle_id in coordinator.vehicle_manager.vehicles.keys():
        vehicle: Vehicle = coordinator.vehicle_manager.vehicles[vehicle_id]
        entities.append(HyundaiKiaConnectWindows(coordinator, vehicle))

    async_add_entities(entities)
    return True


class HyundaiKiaConnectWindows(CoverEntity, HyundaiKiaConnectEntity):
    def __init__(
        self,
        coordinator: HyundaiKiaConnectDataUpdateCoordinator,
        vehicle: Vehicle,
    ):
        HyundaiKiaConnectEntity.__init__(self, coordinator, vehicle)
        self._attr_unique_id = f"{DOMAIN}_{vehicle.id}_windows"
        self._attr_name = f"{vehicle.name} Windows"
        self.device_class = CoverDeviceClass.WINDOW

    @property
    def icon(self):
        return "mdi:card-outline" if self.has_window_open else "mdi:card"

    @property
    def is_closed(self):
        has_window_open = (
            getattr(self.vehicle, "front_left_window_is_open")
            or getattr(self.vehicle, "front_right_window_is_open")
            or getattr(self.vehicle, "back_left_window_is_open")
            or getattr(self.vehicle, "back_right_window_is_open")
        )
        return not has_window_open

    async def async_open_cover(self, **kwargs):
        await self.coordinator.async_set_windows_state(
            self.vehicle.id, OPEN_WINDOW_OPTIONS
        )

    async def async_close_cover(self, **kwargs):
        await self.coordinator.async_set_windows_state(
            self.vehicle.id, CLOSE_WINDOW_OPTIONS
        )
