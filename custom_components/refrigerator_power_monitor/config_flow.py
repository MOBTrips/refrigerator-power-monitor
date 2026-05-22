"""Config flow for Refrigerator Power Monitor."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    AUTO_TUNE_AUTO_APPLY,
    AUTO_TUNE_OFF,
    AUTO_TUNE_SUGGEST_ONLY,
    CONF_AUTO_TUNE_MODE,
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
    CONF_SENSITIVITY,
    CONF_SHORT_AVG_MIN,
    CONF_SHORT_SPIKE_MAX_DURATION_MIN,
    CONF_TREND_THRESHOLD_PERCENT,
    DEFAULT_AUTO_TUNE_MODE,
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
    DEFAULT_SENSITIVITY,
    DEFAULT_SHORT_AVG_MIN,
    DEFAULT_SHORT_SPIKE_MAX_DURATION_MIN,
    DEFAULT_TREND_THRESHOLD_PERCENT,
    DOMAIN,
    SENSITIVITY_HIGH,
    SENSITIVITY_LOW,
    SENSITIVITY_NORMAL,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default="Kitchen Refrigerator"): selector.TextSelector(),
        vol.Required(CONF_POWER_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        ),
        vol.Required(CONF_COMPRESSOR_MIN_W, default=DEFAULT_COMPRESSOR_MIN_W): selector.NumberSelector(
            selector.NumberSelectorConfig(min=1, max=1000, step=1, unit_of_measurement="W")
        ),
        vol.Required(CONF_DEFROST_MAX_W, default=DEFAULT_DEFROST_MAX_W): selector.NumberSelector(
            selector.NumberSelectorConfig(min=10, max=2500, step=5, unit_of_measurement="W")
        ),
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_AUTO_TUNE_MODE, default=DEFAULT_AUTO_TUNE_MODE): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[AUTO_TUNE_OFF, AUTO_TUNE_SUGGEST_ONLY, AUTO_TUNE_AUTO_APPLY],
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Required(CONF_SENSITIVITY, default=DEFAULT_SENSITIVITY): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[SENSITIVITY_LOW, SENSITIVITY_NORMAL, SENSITIVITY_HIGH],
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Required(CONF_COMPRESSOR_MIN_W, default=DEFAULT_COMPRESSOR_MIN_W): selector.NumberSelector(
            selector.NumberSelectorConfig(min=1, max=1000, step=1, unit_of_measurement="W")
        ),
        vol.Required(CONF_DEFROST_MAX_W, default=DEFAULT_DEFROST_MAX_W): selector.NumberSelector(
            selector.NumberSelectorConfig(min=10, max=2500, step=5, unit_of_measurement="W")
        ),
        vol.Required(CONF_SHORT_AVG_MIN, default=DEFAULT_SHORT_AVG_MIN): selector.NumberSelector(
            selector.NumberSelectorConfig(min=5, max=240, step=5, unit_of_measurement="min")
        ),
        vol.Required(CONF_BASELINE_AVG_HOURS, default=DEFAULT_BASELINE_AVG_HOURS): selector.NumberSelector(
            selector.NumberSelectorConfig(min=2, max=168, step=1, unit_of_measurement="hr")
        ),
        vol.Required(CONF_DUTY_RECENT_HOURS, default=DEFAULT_DUTY_RECENT_HOURS): selector.NumberSelector(
            selector.NumberSelectorConfig(min=1, max=12, step=1, unit_of_measurement="hr")
        ),
        vol.Required(CONF_DUTY_BASELINE_HOURS, default=DEFAULT_DUTY_BASELINE_HOURS): selector.NumberSelector(
            selector.NumberSelectorConfig(min=2, max=168, step=1, unit_of_measurement="hr")
        ),
        vol.Required(CONF_HIGH_DUTY_CYCLE, default=DEFAULT_HIGH_DUTY_CYCLE): selector.NumberSelector(
            selector.NumberSelectorConfig(min=40, max=100, step=1, unit_of_measurement="%")
        ),
        vol.Required(CONF_DUTY_RATIO, default=DEFAULT_DUTY_RATIO): selector.NumberSelector(
            selector.NumberSelectorConfig(min=1.0, max=5.0, step=0.1)
        ),
        vol.Required(CONF_AVG_POWER_MIN_W, default=DEFAULT_AVG_POWER_MIN_W): selector.NumberSelector(
            selector.NumberSelectorConfig(min=1, max=1000, step=1, unit_of_measurement="W")
        ),
        vol.Required(CONF_POWER_RATIO, default=DEFAULT_POWER_RATIO): selector.NumberSelector(
            selector.NumberSelectorConfig(min=1.0, max=5.0, step=0.1)
        ),
        vol.Required(CONF_CONTINUOUS_RUN_MIN, default=DEFAULT_CONTINUOUS_RUN_MIN): selector.NumberSelector(
            selector.NumberSelectorConfig(min=15, max=720, step=5, unit_of_measurement="min")
        ),
        vol.Required(CONF_DEFROST_MIN_DURATION_MIN, default=DEFAULT_DEFROST_MIN_DURATION_MIN): selector.NumberSelector(
            selector.NumberSelectorConfig(min=1, max=30, step=1, unit_of_measurement="min")
        ),
        vol.Required(CONF_DEFROST_MAX_DURATION_MIN, default=DEFAULT_DEFROST_MAX_DURATION_MIN): selector.NumberSelector(
            selector.NumberSelectorConfig(min=10, max=180, step=5, unit_of_measurement="min")
        ),
        vol.Required(CONF_SHORT_SPIKE_MAX_DURATION_MIN, default=DEFAULT_SHORT_SPIKE_MAX_DURATION_MIN): selector.NumberSelector(
            selector.NumberSelectorConfig(min=1, max=15, step=1, unit_of_measurement="min")
        ),
        vol.Required(CONF_IDLE_RECENT_HOURS, default=DEFAULT_IDLE_RECENT_HOURS): selector.NumberSelector(
            selector.NumberSelectorConfig(min=1, max=12, step=1, unit_of_measurement="hr")
        ),
        vol.Required(CONF_NO_IDLE_MINUTES, default=DEFAULT_NO_IDLE_MINUTES): selector.NumberSelector(
            selector.NumberSelectorConfig(min=15, max=360, step=5, unit_of_measurement="min")
        ),
        vol.Required(CONF_TREND_THRESHOLD_PERCENT, default=DEFAULT_TREND_THRESHOLD_PERCENT): selector.NumberSelector(
            selector.NumberSelectorConfig(min=1, max=50, step=1, unit_of_measurement="%")
        ),
        vol.Required(CONF_SAMPLE_INTERVAL_SEC, default=DEFAULT_SAMPLE_INTERVAL_SEC): selector.NumberSelector(
            selector.NumberSelectorConfig(min=15, max=600, step=15, unit_of_measurement="sec")
        ),
    }
)


class RefrigeratorPowerMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_POWER_SENSOR])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
                options={
                    CONF_AUTO_TUNE_MODE: DEFAULT_AUTO_TUNE_MODE,
                    CONF_SENSITIVITY: DEFAULT_SENSITIVITY,
                    CONF_COMPRESSOR_MIN_W: user_input[CONF_COMPRESSOR_MIN_W],
                    CONF_DEFROST_MAX_W: user_input[CONF_DEFROST_MAX_W],
                    CONF_SHORT_AVG_MIN: DEFAULT_SHORT_AVG_MIN,
                    CONF_BASELINE_AVG_HOURS: DEFAULT_BASELINE_AVG_HOURS,
                    CONF_DUTY_RECENT_HOURS: DEFAULT_DUTY_RECENT_HOURS,
                    CONF_DUTY_BASELINE_HOURS: DEFAULT_DUTY_BASELINE_HOURS,
                    CONF_HIGH_DUTY_CYCLE: DEFAULT_HIGH_DUTY_CYCLE,
                    CONF_DUTY_RATIO: DEFAULT_DUTY_RATIO,
                    CONF_AVG_POWER_MIN_W: DEFAULT_AVG_POWER_MIN_W,
                    CONF_POWER_RATIO: DEFAULT_POWER_RATIO,
                    CONF_CONTINUOUS_RUN_MIN: DEFAULT_CONTINUOUS_RUN_MIN,
                    CONF_DEFROST_MIN_DURATION_MIN: DEFAULT_DEFROST_MIN_DURATION_MIN,
                    CONF_DEFROST_MAX_DURATION_MIN: DEFAULT_DEFROST_MAX_DURATION_MIN,
                    CONF_SHORT_SPIKE_MAX_DURATION_MIN: DEFAULT_SHORT_SPIKE_MAX_DURATION_MIN,
                    CONF_IDLE_RECENT_HOURS: DEFAULT_IDLE_RECENT_HOURS,
                    CONF_NO_IDLE_MINUTES: DEFAULT_NO_IDLE_MINUTES,
                    CONF_TREND_THRESHOLD_PERCENT: DEFAULT_TREND_THRESHOLD_PERCENT,
                    CONF_SAMPLE_INTERVAL_SEC: DEFAULT_SAMPLE_INTERVAL_SEC,
                },
            )
        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Create the options flow."""
        return RefrigeratorPowerMonitorOptionsFlow()


class RefrigeratorPowerMonitorOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    async def async_step_init(self, user_input=None):
        """Manage integration options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        suggested = {
            CONF_COMPRESSOR_MIN_W: self.config_entry.options.get(
                CONF_COMPRESSOR_MIN_W,
                self.config_entry.data.get(CONF_COMPRESSOR_MIN_W, DEFAULT_COMPRESSOR_MIN_W),
            ),
            CONF_DEFROST_MAX_W: self.config_entry.options.get(
                CONF_DEFROST_MAX_W,
                self.config_entry.data.get(CONF_DEFROST_MAX_W, DEFAULT_DEFROST_MAX_W),
            ),
            **self.config_entry.options,
        }
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(OPTIONS_SCHEMA, suggested),
        )
