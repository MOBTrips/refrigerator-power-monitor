"""Base entity for Refrigerator Power Monitor."""
from __future__ import annotations

from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .monitor import RefrigeratorPowerMonitor


class RefrigeratorPowerMonitorEntity(Entity):
    """Base entity."""

    _attr_has_entity_name = True

    def __init__(self, monitor: RefrigeratorPowerMonitor, key: str, translation_key: str) -> None:
        self.monitor = monitor
        self._attr_unique_id = f"{monitor.entry.entry_id}_{key}"
        self._attr_translation_key = translation_key
        self._attr_device_info = {
            "identifiers": {(DOMAIN, monitor.entry.entry_id)},
            "name": monitor.name,
            "manufacturer": "Custom",
            "model": "Power-based Refrigerator Monitor",
        }

    async def async_added_to_hass(self) -> None:
        """Subscribe to monitor updates."""
        self.async_on_remove(self.monitor.add_listener(self.async_write_ha_state))

    @property
    def available(self) -> bool:
        """Return availability."""
        return self.monitor.metrics.current_power_w is not None

    @property
    def extra_state_attributes(self):
        """Return diagnostic attributes."""
        metrics = self.monitor.metrics
        return {
            "reason": metrics.reason,
            "status": metrics.status,
            "alert_level": metrics.alert_level,
            "alert_reason": metrics.alert_reason,
            "anomaly_confidence": metrics.anomaly_confidence,
            "source_power_sensor": self.monitor.power_sensor,
            "sample_count": metrics.sample_count,
            "baseline_ready": metrics.baseline_ready,
            "current_power_w": metrics.current_power_w,
            "power_recent_average_w": metrics.power_30m_avg_w,
            "power_baseline_average_w": metrics.power_baseline_avg_w,
            "power_ratio": metrics.power_ratio,
            "duty_cycle_recent_pct": metrics.duty_cycle_recent_pct,
            "duty_cycle_baseline_pct": metrics.duty_cycle_baseline_pct,
            "idle_time_recent_minutes": metrics.idle_time_recent_minutes,
            "time_since_idle_minutes": metrics.time_since_idle_minutes,
            "continuous_run_minutes": metrics.continuous_run_minutes,
            "last_event_type": metrics.last_event_type,
            "cooling_trend": metrics.cooling_trend,
            "defrost_active": metrics.defrost_active,
            "last_defrost_started": metrics.last_defrost_started,
            "last_defrost_duration_minutes": metrics.last_defrost_duration_minutes,
            "defrost_count_24h": metrics.defrost_count_24h,
            "short_spike_count_24h": metrics.short_spike_count_24h,
            "suggested_compressor_min_w": metrics.suggested_compressor_min_w,
            "suggested_defrost_min_w": metrics.suggested_defrost_min_w,
            "suggested_average_power_minimum_w": metrics.suggested_average_power_minimum_w,
        }
