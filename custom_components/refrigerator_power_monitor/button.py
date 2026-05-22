"""Button platform for Refrigerator Power Monitor."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .entity import RefrigeratorPowerMonitorEntity
from .monitor import RefrigeratorPowerMonitor

BUTTON_DESCRIPTIONS = (
    ("reset_baseline", "reset_baseline"),
    ("analyze_baseline", "analyze_baseline"),
    ("apply_suggested_thresholds", "apply_suggested_thresholds"),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    """Set up button entities."""
    monitor: RefrigeratorPowerMonitor = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RefrigeratorMonitorButton(monitor, *description) for description in BUTTON_DESCRIPTIONS])


class RefrigeratorMonitorButton(RefrigeratorPowerMonitorEntity, ButtonEntity):
    """Refrigerator monitor action button."""

    def __init__(self, monitor: RefrigeratorPowerMonitor, key: str, translation_key: str) -> None:
        super().__init__(monitor, key, translation_key)
        self._key = key

    async def async_press(self) -> None:
        """Handle the button press."""
        if self._key == "reset_baseline":
            await self.monitor.async_reset_baseline()
        elif self._key == "analyze_baseline":
            await self.monitor.async_analyze_baseline()
        elif self._key == "apply_suggested_thresholds":
            await self.monitor.async_apply_suggested_thresholds()
