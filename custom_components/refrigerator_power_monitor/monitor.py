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
    ALERT_LEVEL_CRITICAL,
    ALERT_LEVEL_NORMAL,
    ALERT_LEVEL_WARNING,
    ALERT_LEVEL_WATCH,
    CONF_AVG_POWER_MIN_W,
    CONF_BASELINE_AVG_HOURS,
    CONF_COMPRESSOR_MIN_W,
    CONF_CONTINUOUS_RUN_MIN,
    CONF_DEFROST_MAX_DURATION_MIN,
    CONF_DEFROST_MAX_W,
    CONF_DEFROST_MIN_DURATION_MIN,
    CONF_DUTY_BASELINE_HOURS,
    CONF_DUTY_RATIO,
    CONF_DUTY_RECENT_HOURS,
    CONF_HIGH_DUTY_CYCLE,
    CONF_IDLE_RECENT_HOURS,
    CONF_NO_IDLE_MINUTES,
    CONF_POWER_RATIO,
    CONF_POWER_SENSOR,
    CONF_SAMPLE_INTERVAL_SEC,
    CONF_SHORT_AVG_MIN,
    CONF_SHORT_SPIKE_MAX_DURATION_MIN,
    CONF_TREND_THRESHOLD_PERCENT,
    DEFAULT_AVG_POWER_MIN_W,
    DEFAULT_BASELINE_AVG_HOURS,
    DEFAULT_COMPRESSOR_MIN_W,
    DEFAULT_CONTINUOUS_RUN_MIN,
    DEFAULT_DEFROST_MAX_DURATION_MIN,
    DEFAULT_DEFROST_MAX_W,
    DEFAULT_DEFROST_MIN_DURATION_MIN,
    DEFAULT_DUTY_BASELINE_HOURS,
    DEFAULT_DUTY_RATIO,
    DEFAULT_DUTY_RECENT_HOURS,
    DEFAULT_HIGH_DUTY_CYCLE,
    DEFAULT_IDLE_RECENT_HOURS,
    DEFAULT_NO_IDLE_MINUTES,
    DEFAULT_POWER_RATIO,
    DEFAULT_SAMPLE_INTERVAL_SEC,
    DEFAULT_SHORT_AVG_MIN,
    DEFAULT_SHORT_SPIKE_MAX_DURATION_MIN,
    DEFAULT_TREND_THRESHOLD_PERCENT,
    DOMAIN,
    EVENT_COMPRESSOR,
    EVENT_DEFROST,
    EVENT_IDLE,
    EVENT_SHORT_SPIKE,
    EVENT_UNKNOWN_HIGH_POWER,
    EVENT_UNAVAILABLE,
    REASON_BASELINE_LEARNING,
    REASON_CONTINUOUS_COMPRESSOR_RUNTIME,
    REASON_DEFROST_ACTIVE,
    REASON_HEAVY_USE_OR_FREQUENT_OPENINGS,
    REASON_HIGH_DUTY_CYCLE_AND_POWER,
    REASON_NO_IDLE_RECOVERY,
    REASON_NONE,
    REASON_POWER_SENSOR_UNAVAILABLE,
    REASON_RECOVERING_FROM_WARM_LOAD,
    REASON_SHORT_POWER_SPIKE,
    STATUS_ALERT,
    STATUS_COOLING,
    STATUS_DEFROSTING,
    STATUS_HEAVY_USE,
    STATUS_LEARNING_BASELINE,
    STATUS_MONITORING,
    STATUS_POWER_SENSOR_UNAVAILABLE,
    STATUS_RECOVERING_FROM_LOAD,
    STATUS_STARTING,
    STORE_VERSION,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class PowerSample:
    """One power sample."""

    ts: float
    watts: float
    compressor_running: bool
    event_type: str = EVENT_IDLE


@dataclass(slots=True)
class MonitorMetrics:
    """Calculated metrics."""

    current_power_w: float | None = None
    compressor_running: bool = False
    defrost_active: bool = False
    power_30m_avg_w: float | None = None
    power_baseline_avg_w: float | None = None
    power_ratio: float | None = None
    duty_cycle_recent_pct: float | None = None
    duty_cycle_baseline_pct: float | None = None
    idle_time_recent_minutes: float | None = None
    time_since_idle_minutes: float | None = None
    continuous_run_minutes: float = 0.0
    baseline_ready: bool = False
    sample_count: int = 0
    status: str = STATUS_STARTING
    anomaly: bool = False
    continuous_run_anomaly: bool = False
    no_idle_recovery_anomaly: bool = False
    last_event_type: str = EVENT_UNAVAILABLE
    last_defrost_started: str | None = None
    last_defrost_duration_minutes: float | None = None
    defrost_count_24h: int = 0
    short_spike_count_24h: int = 0
    cooling_trend: str = "unknown"
    alert_level: str = ALERT_LEVEL_NORMAL
    alert_reason: str = REASON_NONE
    anomaly_confidence: int = 0
    suggested_compressor_min_w: float | None = None
    suggested_defrost_min_w: float | None = None
    suggested_average_power_minimum_w: float | None = None
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
        self._high_power_started_at: datetime | None = None
        self._last_defrost_started: datetime | None = None
        self._last_defrost_duration_minutes: float | None = None
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

    def data_value(self, key: str, default: Any) -> Any:
        return self.entry.data.get(key, default)

    def option_value(self, key: str, default: Any) -> Any:
        return self.entry.options.get(key, default)

    def config_value(self, key: str, default: Any) -> Any:
        """Return an option value, falling back to original setup data."""
        return self.entry.options.get(key, self.entry.data.get(key, default))

    async def async_start(self) -> None:
        """Start monitoring."""
        stored = await self._store.async_load()
        if stored:
            self._samples = []
            for item in stored.get("samples", []):
                try:
                    self._samples.append(
                        PowerSample(
                            float(item["ts"]),
                            float(item["watts"]),
                            bool(item.get("compressor_running", False)),
                            str(item.get("event_type", EVENT_IDLE)),
                        )
                    )
                except (KeyError, TypeError, ValueError):
                    continue
            last_defrost_started = stored.get("last_defrost_started")
            if last_defrost_started:
                try:
                    self._last_defrost_started = dt_util.parse_datetime(last_defrost_started)
                except (TypeError, ValueError):
                    self._last_defrost_started = None
            self._last_defrost_duration_minutes = stored.get("last_defrost_duration_minutes")
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

    async def async_stop(self) -> None:
        """Stop monitoring and persist samples."""
        for unsub in self._unsub:
            unsub()
        self._unsub.clear()
        await self._async_save()

    async def async_reset_baseline(self) -> None:
        """Clear rolling history and start learning a new baseline."""
        self._samples.clear()
        self._compressor_started_at = None
        self._high_power_started_at = None
        self._last_defrost_started = None
        self._last_defrost_duration_minutes = None
        await self._async_save()
        self._sample_now()

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
            watts > float(self.config_value(CONF_COMPRESSOR_MIN_W, DEFAULT_COMPRESSOR_MIN_W))
            and watts < float(self.config_value(CONF_DEFROST_MAX_W, DEFAULT_DEFROST_MAX_W))
        )

    def _classify_event(self, watts: float | None, now: datetime) -> tuple[str, bool]:
        """Classify the current power state."""
        if watts is None:
            return EVENT_UNAVAILABLE, False

        compressor_min = float(self.config_value(CONF_COMPRESSOR_MIN_W, DEFAULT_COMPRESSOR_MIN_W))
        defrost_min = float(self.config_value(CONF_DEFROST_MAX_W, DEFAULT_DEFROST_MAX_W))
        defrost_min_duration = float(
            self.option_value(CONF_DEFROST_MIN_DURATION_MIN, DEFAULT_DEFROST_MIN_DURATION_MIN)
        )
        defrost_max_duration = float(
            self.option_value(CONF_DEFROST_MAX_DURATION_MIN, DEFAULT_DEFROST_MAX_DURATION_MIN)
        )
        short_spike_max_duration = float(
            self.option_value(CONF_SHORT_SPIKE_MAX_DURATION_MIN, DEFAULT_SHORT_SPIKE_MAX_DURATION_MIN)
        )

        if watts <= compressor_min:
            if self._high_power_started_at is not None:
                duration = (now - self._high_power_started_at).total_seconds() / 60
                if duration >= defrost_min_duration:
                    self._last_defrost_started = self._high_power_started_at
                    self._last_defrost_duration_minutes = round(duration, 1)
                self._high_power_started_at = None
            return EVENT_IDLE, False

        if watts < defrost_min:
            if self._high_power_started_at is not None:
                duration = (now - self._high_power_started_at).total_seconds() / 60
                if duration >= defrost_min_duration:
                    self._last_defrost_started = self._high_power_started_at
                    self._last_defrost_duration_minutes = round(duration, 1)
                self._high_power_started_at = None
            return EVENT_COMPRESSOR, False

        if self._high_power_started_at is None:
            self._high_power_started_at = now

        duration = (now - self._high_power_started_at).total_seconds() / 60
        if defrost_min_duration <= duration <= defrost_max_duration:
            return EVENT_DEFROST, True
        if duration < short_spike_max_duration:
            return EVENT_SHORT_SPIKE, False
        return EVENT_UNKNOWN_HIGH_POWER, False

    def _sample_now(self) -> None:
        now_utc = dt_util.utcnow()
        now_local = dt_util.now()
        watts = self._current_power()
        event_type, defrost_active = self._classify_event(watts, now_local)
        running = self._is_compressor_running(watts)

        if running and self._compressor_started_at is None:
            self._compressor_started_at = now_local
        elif not running:
            self._compressor_started_at = None

        if watts is not None:
            self._samples.append(PowerSample(now_utc.timestamp(), watts, running, event_type))
        self._prune_samples()
        self._recalculate(watts, running, defrost_active, event_type)
        self._notify_listeners()

    def _max_retention_hours(self) -> float:
        return max(
            float(self.option_value(CONF_BASELINE_AVG_HOURS, DEFAULT_BASELINE_AVG_HOURS)),
            float(self.option_value(CONF_DUTY_BASELINE_HOURS, DEFAULT_DUTY_BASELINE_HOURS)),
            float(self.option_value(CONF_IDLE_RECENT_HOURS, DEFAULT_IDLE_RECENT_HOURS)),
            24.0,
        )

    def _prune_samples(self) -> None:
        cutoff = dt_util.utcnow().timestamp() - ((self._max_retention_hours() + 1) * 3600)
        self._samples = [sample for sample in self._samples if sample.ts >= cutoff]

    def _samples_since(self, seconds: float) -> list[PowerSample]:
        cutoff = dt_util.utcnow().timestamp() - seconds
        return [sample for sample in self._samples if sample.ts >= cutoff]

    def _samples_between(self, start_seconds_ago: float, end_seconds_ago: float) -> list[PowerSample]:
        now_ts = dt_util.utcnow().timestamp()
        start = now_ts - start_seconds_ago
        end = now_ts - end_seconds_ago
        return [sample for sample in self._samples if start <= sample.ts < end]

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

    @staticmethod
    def _event_pct(samples: list[PowerSample], event_type: str) -> float | None:
        if not samples:
            return None
        count = sum(1 for sample in samples if sample.event_type == event_type)
        return round((count / len(samples)) * 100, 1)

    def _time_since_idle(self) -> float | None:
        for sample in reversed(self._samples):
            if sample.event_type == EVENT_IDLE:
                return round((dt_util.utcnow().timestamp() - sample.ts) / 60, 1)
        return None

    def _count_event_starts_24h(self, event_type: str) -> int:
        samples = self._samples_since(24 * 3600)
        count = 0
        previous = None
        for sample in samples:
            if sample.event_type == event_type and previous != event_type:
                count += 1
            previous = sample.event_type
        return count

    def _cooling_trend(self, short_avg_seconds: float) -> str:
        current = self._average(self._samples_since(short_avg_seconds))
        previous = self._average(self._samples_between(short_avg_seconds * 2, short_avg_seconds))
        if current is None or previous is None or previous <= 0:
            return "unknown"
        delta_pct = ((current - previous) / previous) * 100
        threshold = float(self.option_value(CONF_TREND_THRESHOLD_PERCENT, DEFAULT_TREND_THRESHOLD_PERCENT))
        if delta_pct > threshold:
            return "increasing"
        if delta_pct < -threshold:
            return "decreasing"
        return "stable"

    def _suggest_thresholds(self) -> tuple[float | None, float | None, float | None]:
        if len(self._samples) < 30:
            return None, None, None
        watts_sorted = sorted(sample.watts for sample in self._samples)

        def percentile(p: float) -> float:
            if not watts_sorted:
                return 0.0
            idx = min(len(watts_sorted) - 1, max(0, int(round((len(watts_sorted) - 1) * p))))
            return watts_sorted[idx]

        p50 = percentile(0.50)
        p75 = percentile(0.75)
        p90 = percentile(0.90)
        p97 = percentile(0.97)
        suggested_compressor_min = round(max(10.0, p50 + ((p75 - p50) * 0.5)), 1)
        suggested_defrost_min = round(max(suggested_compressor_min + 50.0, p97 * 0.85), 1)
        suggested_avg_min = round(max(DEFAULT_AVG_POWER_MIN_W, p90), 1)
        return suggested_compressor_min, suggested_defrost_min, suggested_avg_min

    def _recalculate(self, watts: float | None, running: bool, defrost_active: bool, event_type: str) -> None:
        short_avg_seconds = float(self.option_value(CONF_SHORT_AVG_MIN, DEFAULT_SHORT_AVG_MIN)) * 60
        baseline_avg_seconds = float(self.option_value(CONF_BASELINE_AVG_HOURS, DEFAULT_BASELINE_AVG_HOURS)) * 3600
        duty_recent_seconds = float(self.option_value(CONF_DUTY_RECENT_HOURS, DEFAULT_DUTY_RECENT_HOURS)) * 3600
        duty_baseline_seconds = float(self.option_value(CONF_DUTY_BASELINE_HOURS, DEFAULT_DUTY_BASELINE_HOURS)) * 3600
        idle_recent_seconds = float(self.option_value(CONF_IDLE_RECENT_HOURS, DEFAULT_IDLE_RECENT_HOURS)) * 3600

        short_avg = self._average(self._samples_since(short_avg_seconds))
        baseline_avg = self._average(self._samples_since(baseline_avg_seconds))
        duty_recent = self._duty_cycle(self._samples_since(duty_recent_seconds))
        duty_baseline = self._duty_cycle(self._samples_since(duty_baseline_seconds))
        idle_recent_pct = self._event_pct(self._samples_since(idle_recent_seconds), EVENT_IDLE)
        idle_time_recent_minutes = None if idle_recent_pct is None else round((idle_recent_pct / 100) * (idle_recent_seconds / 60), 1)
        time_since_idle = self._time_since_idle()
        cooling_trend = self._cooling_trend(short_avg_seconds)

        power_ratio = None
        if short_avg is not None and baseline_avg and baseline_avg > 0:
            power_ratio = round(short_avg / baseline_avg, 2)

        continuous_minutes = 0.0
        if running and self._compressor_started_at is not None:
            continuous_minutes = round((dt_util.now() - self._compressor_started_at).total_seconds() / 60, 1)

        min_baseline_seconds = min(baseline_avg_seconds, duty_baseline_seconds)
        sample_interval = max(15, int(self.option_value(CONF_SAMPLE_INTERVAL_SEC, DEFAULT_SAMPLE_INTERVAL_SEC)))
        min_baseline_samples = max(10, int((min_baseline_seconds / sample_interval) * 0.25))
        baseline_ready = len(self._samples_since(min_baseline_seconds)) >= min_baseline_samples

        high_duty = duty_recent is not None and duty_recent > float(self.option_value(CONF_HIGH_DUTY_CYCLE, DEFAULT_HIGH_DUTY_CYCLE))
        duty_anomaly = (
            baseline_ready
            and duty_recent is not None
            and duty_baseline is not None
            and duty_baseline > 0
            and high_duty
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

        no_idle_minutes = float(self.option_value(CONF_NO_IDLE_MINUTES, DEFAULT_NO_IDLE_MINUTES))
        no_idle_recovery = time_since_idle is not None and time_since_idle >= no_idle_minutes and running
        continuous_anomaly = continuous_minutes >= float(self.option_value(CONF_CONTINUOUS_RUN_MIN, DEFAULT_CONTINUOUS_RUN_MIN))

        recovering = bool(high_duty and cooling_trend == "decreasing" and not no_idle_recovery and not continuous_anomaly)
        heavy_use = bool(high_duty and idle_time_recent_minutes is not None and idle_time_recent_minutes >= 10 and not continuous_anomaly)
        anomaly = bool((duty_anomaly and power_anomaly and not defrost_active and not recovering) or no_idle_recovery)

        confidence = 0
        if high_duty:
            confidence += 25
        if power_anomaly:
            confidence += 25
        if duty_anomaly:
            confidence += 20
        if no_idle_recovery:
            confidence += 25
        if continuous_anomaly:
            confidence += 35
        if defrost_active:
            confidence -= 35
        if recovering:
            confidence -= 20
        if event_type == EVENT_SHORT_SPIKE:
            confidence -= 15
        confidence = max(0, min(100, confidence))

        if watts is None:
            status = STATUS_POWER_SENSOR_UNAVAILABLE
            alert_level = ALERT_LEVEL_WARNING
            alert_reason = REASON_POWER_SENSOR_UNAVAILABLE
            reason = "Power sensor is unavailable or not numeric."
        elif defrost_active:
            status = STATUS_DEFROSTING
            alert_level = ALERT_LEVEL_NORMAL
            alert_reason = REASON_DEFROST_ACTIVE
            reason = "High-power defrost-like event is active; anomaly alerts are suppressed."
        elif event_type == EVENT_SHORT_SPIKE:
            status = STATUS_MONITORING if baseline_ready else STATUS_LEARNING_BASELINE
            alert_level = ALERT_LEVEL_NORMAL
            alert_reason = REASON_SHORT_POWER_SPIKE
            reason = "Short high-power spike detected, likely accessory or ice-maker related."
        elif continuous_anomaly:
            status = STATUS_ALERT
            alert_level = ALERT_LEVEL_CRITICAL
            alert_reason = REASON_CONTINUOUS_COMPRESSOR_RUNTIME
            reason = "Compressor has been running continuously longer than the configured threshold."
        elif no_idle_recovery:
            status = STATUS_ALERT
            alert_level = ALERT_LEVEL_CRITICAL
            alert_reason = REASON_NO_IDLE_RECOVERY
            reason = "Compressor is running and the refrigerator has not returned to idle for too long."
        elif anomaly:
            status = STATUS_ALERT
            alert_level = ALERT_LEVEL_WARNING if confidence < 75 else ALERT_LEVEL_CRITICAL
            alert_reason = REASON_HIGH_DUTY_CYCLE_AND_POWER
            reason = "Recent compressor duty cycle and average power are both unusually high versus baseline."
        elif recovering:
            status = STATUS_RECOVERING_FROM_LOAD
            alert_level = ALERT_LEVEL_WATCH
            alert_reason = REASON_RECOVERING_FROM_WARM_LOAD
            reason = "Cooling load is high but trending down, which can happen after adding warm groceries."
        elif heavy_use:
            status = STATUS_HEAVY_USE
            alert_level = ALERT_LEVEL_WATCH
            alert_reason = REASON_HEAVY_USE_OR_FREQUENT_OPENINGS
            reason = "Duty cycle is high, but idle recovery is still present; this may be frequent door openings or warm load."
        elif not baseline_ready:
            status = STATUS_LEARNING_BASELINE
            alert_level = ALERT_LEVEL_NORMAL
            alert_reason = REASON_BASELINE_LEARNING
            reason = "Collecting enough samples to establish a baseline."
        elif running:
            status = STATUS_COOLING
            alert_level = ALERT_LEVEL_NORMAL
            alert_reason = REASON_NONE
            reason = "Compressor is running normally."
        else:
            status = STATUS_MONITORING
            alert_level = ALERT_LEVEL_NORMAL
            alert_reason = REASON_NONE
            reason = "No anomaly detected."

        suggested_comp, suggested_defrost, suggested_avg = self._suggest_thresholds()

        self.metrics = MonitorMetrics(
            current_power_w=watts,
            compressor_running=running,
            defrost_active=defrost_active,
            power_30m_avg_w=short_avg,
            power_baseline_avg_w=baseline_avg,
            power_ratio=power_ratio,
            duty_cycle_recent_pct=duty_recent,
            duty_cycle_baseline_pct=duty_baseline,
            idle_time_recent_minutes=idle_time_recent_minutes,
            time_since_idle_minutes=time_since_idle,
            continuous_run_minutes=continuous_minutes,
            baseline_ready=baseline_ready,
            sample_count=len(self._samples),
            status=status,
            anomaly=anomaly,
            continuous_run_anomaly=continuous_anomaly,
            no_idle_recovery_anomaly=no_idle_recovery,
            last_event_type=event_type,
            last_defrost_started=self._last_defrost_started.isoformat() if self._last_defrost_started else None,
            last_defrost_duration_minutes=self._last_defrost_duration_minutes,
            defrost_count_24h=self._count_event_starts_24h(EVENT_DEFROST),
            short_spike_count_24h=self._count_event_starts_24h(EVENT_SHORT_SPIKE),
            cooling_trend=cooling_trend,
            alert_level=alert_level,
            alert_reason=alert_reason,
            anomaly_confidence=confidence,
            suggested_compressor_min_w=suggested_comp,
            suggested_defrost_min_w=suggested_defrost,
            suggested_average_power_minimum_w=suggested_avg,
            reason=reason,
        )

    async def _async_save(self) -> None:
        data = {
            "samples": [
                {
                    "ts": sample.ts,
                    "watts": sample.watts,
                    "compressor_running": sample.compressor_running,
                    "event_type": sample.event_type,
                }
                for sample in self._samples
            ],
            "last_defrost_started": self._last_defrost_started.isoformat() if self._last_defrost_started else None,
            "last_defrost_duration_minutes": self._last_defrost_duration_minutes,
        }
        await self._store.async_save(data)

    def _notify_listeners(self) -> None:
        for update_callback in list(self._callbacks):
            update_callback()
