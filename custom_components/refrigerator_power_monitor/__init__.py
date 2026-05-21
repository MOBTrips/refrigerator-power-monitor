"""Refrigerator Power Monitor integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .monitor import RefrigeratorPowerMonitor

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Refrigerator Power Monitor from a config entry."""
    monitor = RefrigeratorPowerMonitor(hass, entry)
    await monitor.async_start()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = monitor
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload this config entry when options are changed from the gear/settings page.
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    return True

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle updated options."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    monitor: RefrigeratorPowerMonitor | None = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if monitor is not None:
        await monitor.async_stop()
    return unload_ok

async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old config entries."""
    return True
