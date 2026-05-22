"""Constants for Refrigerator Power Monitor."""

DOMAIN = "refrigerator_power_monitor"
PLATFORMS = ["sensor", "binary_sensor", "button"]

CONF_NAME = "name"
CONF_POWER_SENSOR = "power_sensor"
CONF_COMPRESSOR_MIN_W = "compressor_min_w"
CONF_DEFROST_MAX_W = "defrost_max_w"  # Historical option name; used as high-power/defrost threshold.
CONF_SHORT_AVG_MIN = "short_avg_minutes"
CONF_BASELINE_AVG_HOURS = "baseline_avg_hours"
CONF_DUTY_RECENT_HOURS = "duty_recent_hours"
CONF_DUTY_BASELINE_HOURS = "duty_baseline_hours"
CONF_HIGH_DUTY_CYCLE = "high_duty_cycle_threshold"
CONF_DUTY_RATIO = "duty_cycle_ratio_threshold"
CONF_AVG_POWER_MIN_W = "average_power_minimum_w"
CONF_POWER_RATIO = "power_ratio_threshold"
CONF_CONTINUOUS_RUN_MIN = "continuous_run_minutes"
CONF_SAMPLE_INTERVAL_SEC = "sample_interval_seconds"
CONF_DEFROST_MIN_DURATION_MIN = "defrost_min_duration_minutes"
CONF_DEFROST_MAX_DURATION_MIN = "defrost_max_duration_minutes"
CONF_SHORT_SPIKE_MAX_DURATION_MIN = "short_spike_max_duration_minutes"
CONF_IDLE_RECENT_HOURS = "idle_recent_hours"
CONF_NO_IDLE_MINUTES = "no_idle_minutes"
CONF_TREND_THRESHOLD_PERCENT = "trend_threshold_percent"
CONF_AUTO_TUNE_MODE = "auto_tune_mode"
CONF_SENSITIVITY = "sensitivity"

DEFAULT_COMPRESSOR_MIN_W = 60.0
DEFAULT_DEFROST_MAX_W = 300.0
DEFAULT_SHORT_AVG_MIN = 30
DEFAULT_BASELINE_AVG_HOURS = 24
DEFAULT_DUTY_RECENT_HOURS = 2
DEFAULT_DUTY_BASELINE_HOURS = 24
DEFAULT_HIGH_DUTY_CYCLE = 80.0
DEFAULT_DUTY_RATIO = 1.8
DEFAULT_AVG_POWER_MIN_W = 75.0
DEFAULT_POWER_RATIO = 2.0
DEFAULT_CONTINUOUS_RUN_MIN = 120
DEFAULT_SAMPLE_INTERVAL_SEC = 60
DEFAULT_DEFROST_MIN_DURATION_MIN = 3
DEFAULT_DEFROST_MAX_DURATION_MIN = 60
DEFAULT_SHORT_SPIKE_MAX_DURATION_MIN = 3
DEFAULT_IDLE_RECENT_HOURS = 2
DEFAULT_NO_IDLE_MINUTES = 90
DEFAULT_TREND_THRESHOLD_PERCENT = 10.0
DEFAULT_AUTO_TUNE_MODE = "suggest_only"
DEFAULT_SENSITIVITY = "normal"

AUTO_TUNE_OFF = "off"
AUTO_TUNE_SUGGEST_ONLY = "suggest_only"
AUTO_TUNE_AUTO_APPLY = "auto_apply"

SENSITIVITY_LOW = "low"
SENSITIVITY_NORMAL = "normal"
SENSITIVITY_HIGH = "high"

STORE_VERSION = 1

EVENT_IDLE = "idle"
EVENT_COMPRESSOR = "compressor"
EVENT_DEFROST = "defrost"
EVENT_SHORT_SPIKE = "short_spike"
EVENT_UNKNOWN_HIGH_POWER = "unknown_high_power"
EVENT_UNAVAILABLE = "unavailable"

STATUS_STARTING = "starting"
STATUS_LEARNING_BASELINE = "learning_baseline"
STATUS_MONITORING = "monitoring"
STATUS_COOLING = "cooling"
STATUS_DEFROSTING = "defrosting"
STATUS_RECOVERING_FROM_LOAD = "recovering_from_load"
STATUS_HEAVY_USE = "heavy_use"
STATUS_ALERT = "alert"
STATUS_POWER_SENSOR_UNAVAILABLE = "power_sensor_unavailable"

ALERT_LEVEL_NORMAL = "normal"
ALERT_LEVEL_WATCH = "watch"
ALERT_LEVEL_WARNING = "warning"
ALERT_LEVEL_CRITICAL = "critical"

REASON_NONE = "none"
REASON_BASELINE_LEARNING = "baseline_learning"
REASON_POWER_SENSOR_UNAVAILABLE = "power_sensor_unavailable"
REASON_DEFROST_ACTIVE = "defrost_active"
REASON_SHORT_POWER_SPIKE = "short_power_spike"
REASON_RECOVERING_FROM_WARM_LOAD = "recovering_from_warm_load"
REASON_HEAVY_USE_OR_FREQUENT_OPENINGS = "heavy_use_or_frequent_openings"
REASON_HIGH_DUTY_CYCLE_AND_POWER = "high_duty_cycle_and_power"
REASON_CONTINUOUS_COMPRESSOR_RUNTIME = "continuous_compressor_runtime"
REASON_NO_IDLE_RECOVERY = "no_idle_recovery"

AUTO_TUNE_STATUS_OFF = "off"
AUTO_TUNE_STATUS_LEARNING = "learning"
AUTO_TUNE_STATUS_SUGGESTIONS_READY = "suggestions_ready"
AUTO_TUNE_STATUS_APPLIED = "applied"
AUTO_TUNE_STATUS_AUTO_APPLIED = "auto_applied"
AUTO_TUNE_STATUS_NO_SUGGESTIONS = "no_suggestions"
