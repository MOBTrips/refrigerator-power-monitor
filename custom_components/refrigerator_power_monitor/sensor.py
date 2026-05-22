"""Sensor platform for Refrigerator Power Monitor."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower, UnitOfTime
from homeassistant.core import HomeAssistant

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
    ("idle_time_recent", "idle_time_recent", SensorDeviceClass.DURATION, UnitOfTime.MINUTES, SensorStateClass.MEASUREMENT),
    ("time_since_idle", "time_since_idle", SensorDeviceClass.DURATION, UnitOfTime.MINUTES, SensorStateClass.MEASUREMENT),
    ("continuous_run", "continuous_run", SensorDeviceClass.DURATION, UnitOfTime.MINUTES, SensorStateClass.MEASUREMENT),
    ("defrost_count_24h", "defrost_count_24h", None, None, SensorStateClass.MEASUREMENT),
    ("short_spike_count_24h", "short_spike_count_24h", None, None, SensorStateClass.MEASUREMENT),
    ("last_defrost_duration", "last_defrost_duration", SensorDeviceClass.DURATION, UnitOfTime.MINUTES, SensorStateClass.MEASUREMENT),
    ("anomaly_confidence", "anomaly_confidence", None, PERCENTAGE, SensorStateClass.MEASUREMENT),
    ("suggested_compressor_min", "suggested_compressor_min", SensorDeviceClass.POWER, UnitOfPower.WATT, SensorStateClass.MEASUREMENT),
    ("suggested_defrost_min", "suggested_defrost_min", SensorDeviceClass.POWER, UnitOfPower.WATT, SensorStateClass.MEASUREMENT),
    ("suggested_average_power_minimum", "suggested_average_power_minimum", SensorDeviceClass.POWER, UnitOfPower.WATT, SensorStateClass.MEASUREMENT),
    ("monitor_status", "monitor_status", None, None, None),
    ("last_event_type", "last_event_type", None, None, None),
    ("cooling_trend", "cooling_trend", None, None, None),
    ("alert_level", "alert_level", None, None, None),
    ("alert_reason", "alert_reason", None, None, None),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    """Set up sensor entities."""
    monitor: RefrigeratorPowerMonitor = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RefrigeratorSensor(monitor, *description) for description in SENSOR_DESCRIPTIONS])


class RefrigeratorSensor(RefrigeratorPowerMonitorEntity, SensorEntity):
    """Refrigerator monitor sensor."""

    def __init__(self, monitor: RefrigeratorPowerMonitor, key: str, translation_key: str, device_class, unit, state_class) -> None:
        super().__init__(monitor, key, translation_key)
        self._key = key
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = state_class

    @property
    def native_value(self):
        """Return the native value."""
        metrics = self.monitor.metrics
        return {
            "current_power": metrics.current_power_w,
            "power_recent_average": metrics.power_30m_avg_w,
            "power_baseline_average": metrics.power_baseline_avg_w,
            "power_ratio": metrics.power_ratio,
            "duty_cycle_recent": metrics.duty_cycle_recent_pct,
            "duty_cycle_baseline": metrics.duty_cycle_baseline_pct,
            "idle_time_recent": metrics.idle_time_recent_minutes,
            "time_since_idle": metrics.time_since_idle_minutes,
            "continuous_run": metrics.continuous_run_minutes,
            "defrost_count_24h": metrics.defrost_count_24h,
            "short_spike_count_24h": metrics.short_spike_count_24h,
            "last_defrost_duration": metrics.last_defrost_duration_minutes,
            "anomaly_confidence": metrics.anomaly_confidence,
            "suggested_compressor_min": metrics.suggested_compressor_min_w,
            "suggested_defrost_min": metrics.suggested_defrost_min_w,
            "suggested_average_power_minimum": metrics.suggested_average_power_minimum_w,
            "monitor_status": metrics.status,
            "last_event_type": metrics.last_event_type,
            "cooling_trend": metrics.cooling_trend,
            "alert_level": metrics.alert_level,
            "alert_reason": metrics.alert_reason,
        }[self._key]
