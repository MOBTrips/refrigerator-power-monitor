"""Sensor platform for Refrigerator Power Monitor."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfPower, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .entity import RefrigeratorPowerMonitorEntity
from .monitor import RefrigeratorPowerMonitor

SENSOR_DESCRIPTIONS = (
    ("current_power", "current_power", SensorDeviceClass.POWER, UnitOfPower.WATT, SensorStateClass.MEASUREMENT),
    ("power_recent_average", "power_recent_average", SensorDeviceClass.POWER, UnitOfPower.WATT, SensorStateClass.MEASUREMENT),
    ("power_baseline_average", "power_baseline_average", SensorDeviceClass.POWER, UnitOfPower.WATT, SensorStateClass.MEASUREMENT),
    ("power_ratio", "power_ratio", None, None, SensorStateClass.MEASUREMENT),
    ("duty_cycle_recent", "duty_cycle_recent", None, PERCENTAGE, SensorStateClass.MEASUREMENT),
    ("duty_cycle_baseline", "duty_cycle_baseline", None, PERCENTAGE, SensorStateClass.MEASUREMENT),
    ("continuous_run", "continuous_run", SensorDeviceClass.DURATION, UnitOfTime.MINUTES, SensorStateClass.MEASUREMENT),
    ("monitor_status", "monitor_status", None, None, None),
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    monitor: RefrigeratorPowerMonitor = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RefrigeratorSensor(monitor, *description) for description in SENSOR_DESCRIPTIONS])

class RefrigeratorSensor(RefrigeratorPowerMonitorEntity, SensorEntity):
    def __init__(self, monitor: RefrigeratorPowerMonitor, key: str, translation_key: str, device_class, unit, state_class) -> None:
        super().__init__(monitor, key, translation_key)
        self._key = key
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = state_class

    @property
    def native_value(self):
        metrics = self.monitor.metrics
        return {
            "current_power": metrics.current_power_w,
            "power_recent_average": metrics.power_30m_avg_w,
            "power_baseline_average": metrics.power_baseline_avg_w,
            "power_ratio": metrics.power_ratio,
            "duty_cycle_recent": metrics.duty_cycle_recent_pct,
            "duty_cycle_baseline": metrics.duty_cycle_baseline_pct,
            "continuous_run": metrics.continuous_run_minutes,
            "monitor_status": metrics.status,
        }[self._key]
