"""Constants for Refrigerator Power Monitor."""

DOMAIN = "refrigerator_power_monitor"
PLATFORMS = ["sensor", "binary_sensor"]

CONF_NAME = "name"
CONF_POWER_SENSOR = "power_sensor"
CONF_COMPRESSOR_MIN_W = "compressor_min_w"
CONF_DEFROST_MAX_W = "defrost_max_w"
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

STORE_VERSION = 1
