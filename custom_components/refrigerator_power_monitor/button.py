"""Button platform for Refrigerator Power Monitor."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .entity import RefrigeratorPowerMonitorEntity
from .monitor import RefrigeratorPowerMonitor


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    """Set up button entities."""
    monitor: RefrigeratorPowerMonitor = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ResetBaselineButton(monitor)])


class ResetBaselineButton(RefrigeratorPowerMonitorEntity, ButtonEntity):
    """Reset baseline button."""

    def __init__(self, monitor: RefrigeratorPowerMonitor) -> None:
        super().__init__(monitor, "reset_baseline", "reset_baseline")

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.monitor.async_reset_baseline()
