"""Rolling-history engine for Refrigerator Power Monitor."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, State, callback
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    CONF_AVG_POWER_MIN_W,
    CONF_BASELINE_AVG_HOURS,
    CONF_COMPRESSOR_MIN_W,
    CONF_CONTINUOUS_RUN_MIN,
    CONF_DEFROST_MAX_W,
    CONF_DUTY_BASELINE_HOURS,
    CONF_DUTY_RATIO,
    CONF_DUTY_RECENT_HOURS,
    CONF_HIGH_DUTY_CYCLE,
    CONF_POWER_RATIO,
    CONF_POWER_SENSOR,
    CONF_SAMPLE_INTERVAL_SEC,
    CONF_SHORT_AVG_MIN,
    DEFAULT_AVG_POWER_MIN_W,
    DEFAULT_BASELINE_AVG_HOURS,
    DEFAULT_COMPRESSOR_MIN_W,
    DEFAULT_CONTINUOUS_RUN_MIN,
    DEFAULT_DEFROST_MAX_W,
    DEFAULT_DUTY_BASELINE_HOURS,
    DEFAULT_DUTY_RATIO,
    DEFAULT_DUTY_RECENT_HOURS,
    DEFAULT_HIGH_DUTY_CYCLE,
    DEFAULT_POWER_RATIO,
    DEFAULT_SAMPLE_INTERVAL_SEC,
    DEFAULT_SHORT_AVG_MIN,
    DOMAIN,
    STORE_VERSION,
)

_LOGGER = logging.getLogger(__name__)

@dataclass(slots=True)
class PowerSample:
    """One power sample."""
    ts: float
    watts: float
    compressor_running: bool

@dataclass(slots=True)
class MonitorMetrics:
    """Calculated metrics."""
    current_power_w: float | None = None
    compressor_running: bool = False
    power_30m_avg_w: float | None = None
    power_baseline_avg_w: float | None = None
    power_ratio: float | None = None
    duty_cycle_recent_pct: float | None = None
    duty_cycle_baseline_pct: float | None = None
    continuous_run_minutes: float = 0.0
    baseline_ready: bool = False
    sample_count: int = 0
    status: str = "starting"
    anomaly: bool = False
    continuous_run_anomaly: bool = False
    reason: str = ""

class RefrigeratorPowerMonitor:
    """Maintains rolling power history and exposes derived refrigerator metrics."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._callbacks: list[Callable[[], None]] = []
        self._unsub: list[Callable[[], None]] = []
        self._samples: list[PowerSample] = []
        self.metrics = MonitorMetrics()
        self._compressor_started_at: datetime | None = None
        self._store: Store[dict[str, Any]] = Store(
            hass, STORE_VERSION, f"{DOMAIN}.{entry.entry_id}"
        )

    @property
    def name(self) -> str:
        return self.entry.data[CONF_NAME]

    @property
    def power_sensor(self) -> str:
        return self.entry.data[CONF_POWER_SENSOR]

    @property
    def device_id(self) -> str:
        return self.entry.entry_id

    @property
    def options(self) -> dict[str, Any]:
        return {**self.entry.options}

    def data_value(self, key: str, default: Any) -> Any:
        return self.entry.data.get(key, default)

    def option_value(self, key: str, default: Any) -> Any:
        return self.entry.options.get(key, default)

    async def async_start(self) -> None:
        """Start monitoring."""
        stored = await self._store.async_load()
        if stored:
            self._samples = [
                PowerSample(float(item["ts"]), float(item["watts"]), bool(item["compressor_running"]))
                for item in stored.get("samples", [])
                if "ts" in item and "watts" in item and "compressor_running" in item
            ]
        self._prune_samples()
        self._sample_now()

        self._unsub.append(
            async_track_state_change_event(self.hass, [self.power_sensor], self._async_power_changed)
        )
        self._unsub.append(
            async_track_time_interval(
                self.hass,
                self._async_interval,
                timedelta(seconds=int(self.option_value(CONF_SAMPLE_INTERVAL_SEC, DEFAULT_SAMPLE_INTERVAL_SEC))),
            )
        )
        self.entry.async_on_unload(self.entry.add_update_listener(_async_options_updated))

    async def async_stop(self) -> None:
        """Stop monitoring and persist samples."""
        for unsub in self._unsub:
            unsub()
        self._unsub.clear()
        await self._async_save()

    def add_listener(self, update_callback: Callable[[], None]) -> Callable[[], None]:
        """Register an update callback."""
        self._callbacks.append(update_callback)

        def remove() -> None:
            if update_callback in self._callbacks:
                self._callbacks.remove(update_callback)

        return remove

    @callback
    def _async_power_changed(self, event) -> None:
        self._sample_now()

    @callback
    def _async_interval(self, now: datetime) -> None:
        self._sample_now()
        self.hass.async_create_task(self._async_save())

    def _current_power(self) -> float | None:
        state: State | None = self.hass.states.get(self.power_sensor)
        if state is None or state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            return None
        try:
            return float(state.state)
        except (TypeError, ValueError):
            return None

    def _is_compressor_running(self, watts: float | None) -> bool:
        if watts is None:
            return False
        return (
            watts > float(self.data_value(CONF_COMPRESSOR_MIN_W, DEFAULT_COMPRESSOR_MIN_W))
            and watts < float(self.data_value(CONF_DEFROST_MAX_W, DEFAULT_DEFROST_MAX_W))
        )

    def _sample_now(self) -> None:
        now = dt_util.utcnow()
        watts = self._current_power()
        running = self._is_compressor_running(watts)

        if running and self._compressor_started_at is None:
            self._compressor_started_at = dt_util.now()
        elif not running:
            self._compressor_started_at = None

        if watts is not None:
            self._samples.append(PowerSample(now.timestamp(), watts, running))
        self._prune_samples()
        self._recalculate(watts, running)
        self._notify_listeners()

    def _prune_samples(self) -> None:
        baseline_hours = max(
            float(self.option_value(CONF_BASELINE_AVG_HOURS, DEFAULT_BASELINE_AVG_HOURS)),
            float(self.option_value(CONF_DUTY_BASELINE_HOURS, DEFAULT_DUTY_BASELINE_HOURS)),
        )
        cutoff = dt_util.utcnow().timestamp() - ((baseline_hours + 1) * 3600)
        self._samples = [sample for sample in self._samples if sample.ts >= cutoff]

    def _samples_since(self, seconds: float) -> list[PowerSample]:
        cutoff = dt_util.utcnow().timestamp() - seconds
        return [sample for sample in self._samples if sample.ts >= cutoff]

    @staticmethod
    def _average(samples: list[PowerSample]) -> float | None:
        if not samples:
            return None
        return round(sum(sample.watts for sample in samples) / len(samples), 2)

    @staticmethod
    def _duty_cycle(samples: list[PowerSample]) -> float | None:
        if not samples:
            return None
        running = sum(1 for sample in samples if sample.compressor_running)
        return round((running / len(samples)) * 100, 1)

    def _recalculate(self, watts: float | None, running: bool) -> None:
        short_avg_seconds = float(self.option_value(CONF_SHORT_AVG_MIN, DEFAULT_SHORT_AVG_MIN)) * 60
        baseline_avg_seconds = float(self.option_value(CONF_BASELINE_AVG_HOURS, DEFAULT_BASELINE_AVG_HOURS)) * 3600
        duty_recent_seconds = float(self.option_value(CONF_DUTY_RECENT_HOURS, DEFAULT_DUTY_RECENT_HOURS)) * 3600
        duty_baseline_seconds = float(self.option_value(CONF_DUTY_BASELINE_HOURS, DEFAULT_DUTY_BASELINE_HOURS)) * 3600

        short_avg = self._average(self._samples_since(short_avg_seconds))
        baseline_avg = self._average(self._samples_since(baseline_avg_seconds))
        duty_recent = self._duty_cycle(self._samples_since(duty_recent_seconds))
        duty_baseline = self._duty_cycle(self._samples_since(duty_baseline_seconds))

        power_ratio = None
        if short_avg is not None and baseline_avg and baseline_avg > 0:
            power_ratio = round(short_avg / baseline_avg, 2)

        continuous_minutes = 0.0
        if running and self._compressor_started_at is not None:
            continuous_minutes = round((dt_util.now() - self._compressor_started_at).total_seconds() / 60, 1)

        min_baseline_samples = max(10, int((min(baseline_avg_seconds, duty_baseline_seconds) / max(15, int(self.option_value(CONF_SAMPLE_INTERVAL_SEC, DEFAULT_SAMPLE_INTERVAL_SEC)))) * 0.25))
        baseline_ready = len(self._samples_since(min(baseline_avg_seconds, duty_baseline_seconds))) >= min_baseline_samples

        duty_anomaly = (
            baseline_ready
            and duty_recent is not None
            and duty_baseline is not None
            and duty_baseline > 0
            and duty_recent > float(self.option_value(CONF_HIGH_DUTY_CYCLE, DEFAULT_HIGH_DUTY_CYCLE))
            and duty_recent > duty_baseline * float(self.option_value(CONF_DUTY_RATIO, DEFAULT_DUTY_RATIO))
        )
        power_anomaly = (
            baseline_ready
            and short_avg is not None
            and baseline_avg is not None
            and power_ratio is not None
            and short_avg > float(self.option_value(CONF_AVG_POWER_MIN_W, DEFAULT_AVG_POWER_MIN_W))
            and power_ratio > float(self.option_value(CONF_POWER_RATIO, DEFAULT_POWER_RATIO))
        )
        anomaly = bool(duty_anomaly and power_anomaly)
        continuous_anomaly = continuous_minutes >= float(self.option_value(CONF_CONTINUOUS_RUN_MIN, DEFAULT_CONTINUOUS_RUN_MIN))

        if watts is None:
            status = "power_sensor_unavailable"
            reason = "Power sensor is unavailable or not numeric."
        elif continuous_anomaly:
            status = "alert"
            reason = "Compressor has been running continuously longer than the configured threshold."
        elif anomaly:
            status = "alert"
            reason = "Recent compressor duty cycle and average power are both unusually high versus baseline."
        elif not baseline_ready:
            status = "learning_baseline"
            reason = "Collecting enough samples to establish a baseline."
        else:
            status = "monitoring"
            reason = "No anomaly detected."

        self.metrics = MonitorMetrics(
            current_power_w=watts,
            compressor_running=running,
            power_30m_avg_w=short_avg,
            power_baseline_avg_w=baseline_avg,
            power_ratio=power_ratio,
            duty_cycle_recent_pct=duty_recent,
            duty_cycle_baseline_pct=duty_baseline,
            continuous_run_minutes=continuous_minutes,
            baseline_ready=baseline_ready,
            sample_count=len(self._samples),
            status=status,
            anomaly=anomaly,
            continuous_run_anomaly=continuous_anomaly,
            reason=reason,
        )

    async def _async_save(self) -> None:
        data = {
            "samples": [
                {"ts": sample.ts, "watts": sample.watts, "compressor_running": sample.compressor_running}
                for sample in self._samples
            ]
        }
        await self._store.async_save(data)

    def _notify_listeners(self) -> None:
        for update_callback in list(self._callbacks):
            update_callback()

async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
