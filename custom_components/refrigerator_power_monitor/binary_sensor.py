"""Binary sensor platform for Refrigerator Power Monitor."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .entity import RefrigeratorPowerMonitorEntity
from .monitor import RefrigeratorPowerMonitor

BINARY_SENSOR_DESCRIPTIONS = (
    ("compressor_running", "compressor_running", BinarySensorDeviceClass.RUNNING),
    ("power_anomaly", "power_anomaly", BinarySensorDeviceClass.PROBLEM),
    ("continuous_run_anomaly", "continuous_run_anomaly", BinarySensorDeviceClass.PROBLEM),
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    monitor: RefrigeratorPowerMonitor = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RefrigeratorBinarySensor(monitor, *description) for description in BINARY_SENSOR_DESCRIPTIONS])

class RefrigeratorBinarySensor(RefrigeratorPowerMonitorEntity, BinarySensorEntity):
    def __init__(self, monitor: RefrigeratorPowerMonitor, key: str, translation_key: str, device_class) -> None:
        super().__init__(monitor, key, translation_key)
        self._key = key
        self._attr_device_class = device_class

    @property
    def is_on(self) -> bool:
        metrics = self.monitor.metrics
        return {
            "compressor_running": metrics.compressor_running,
            "power_anomaly": metrics.anomaly,
            "continuous_run_anomaly": metrics.continuous_run_anomaly,
        }[self._key]
