"""Config flow for Refrigerator Power Monitor."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector

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
                    CONF_SHORT_AVG_MIN: DEFAULT_SHORT_AVG_MIN,
                    CONF_BASELINE_AVG_HOURS: DEFAULT_BASELINE_AVG_HOURS,
                    CONF_DUTY_RECENT_HOURS: DEFAULT_DUTY_RECENT_HOURS,
                    CONF_DUTY_BASELINE_HOURS: DEFAULT_DUTY_BASELINE_HOURS,
                    CONF_HIGH_DUTY_CYCLE: DEFAULT_HIGH_DUTY_CYCLE,
                    CONF_DUTY_RATIO: DEFAULT_DUTY_RATIO,
                    CONF_AVG_POWER_MIN_W: DEFAULT_AVG_POWER_MIN_W,
                    CONF_POWER_RATIO: DEFAULT_POWER_RATIO,
                    CONF_CONTINUOUS_RUN_MIN: DEFAULT_CONTINUOUS_RUN_MIN,
                    CONF_SAMPLE_INTERVAL_SEC: DEFAULT_SAMPLE_INTERVAL_SEC,
                },
            )
        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)

    @staticmethod
    def async_get_options_flow(config_entry):
        return RefrigeratorPowerMonitorOptionsFlow(config_entry)

class RefrigeratorPowerMonitorOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = {**self.config_entry.options}
        schema = vol.Schema(
            {
                vol.Required(CONF_SHORT_AVG_MIN, default=current.get(CONF_SHORT_AVG_MIN, DEFAULT_SHORT_AVG_MIN)): selector.NumberSelector(selector.NumberSelectorConfig(min=5, max=240, step=5, unit_of_measurement="min")),
                vol.Required(CONF_BASELINE_AVG_HOURS, default=current.get(CONF_BASELINE_AVG_HOURS, DEFAULT_BASELINE_AVG_HOURS)): selector.NumberSelector(selector.NumberSelectorConfig(min=2, max=168, step=1, unit_of_measurement="hr")),
                vol.Required(CONF_DUTY_RECENT_HOURS, default=current.get(CONF_DUTY_RECENT_HOURS, DEFAULT_DUTY_RECENT_HOURS)): selector.NumberSelector(selector.NumberSelectorConfig(min=1, max=12, step=1, unit_of_measurement="hr")),
                vol.Required(CONF_DUTY_BASELINE_HOURS, default=current.get(CONF_DUTY_BASELINE_HOURS, DEFAULT_DUTY_BASELINE_HOURS)): selector.NumberSelector(selector.NumberSelectorConfig(min=2, max=168, step=1, unit_of_measurement="hr")),
                vol.Required(CONF_HIGH_DUTY_CYCLE, default=current.get(CONF_HIGH_DUTY_CYCLE, DEFAULT_HIGH_DUTY_CYCLE)): selector.NumberSelector(selector.NumberSelectorConfig(min=40, max=100, step=1, unit_of_measurement="%")),
                vol.Required(CONF_DUTY_RATIO, default=current.get(CONF_DUTY_RATIO, DEFAULT_DUTY_RATIO)): selector.NumberSelector(selector.NumberSelectorConfig(min=1.0, max=5.0, step=0.1)),
                vol.Required(CONF_AVG_POWER_MIN_W, default=current.get(CONF_AVG_POWER_MIN_W, DEFAULT_AVG_POWER_MIN_W)): selector.NumberSelector(selector.NumberSelectorConfig(min=1, max=1000, step=1, unit_of_measurement="W")),
                vol.Required(CONF_POWER_RATIO, default=current.get(CONF_POWER_RATIO, DEFAULT_POWER_RATIO)): selector.NumberSelector(selector.NumberSelectorConfig(min=1.0, max=5.0, step=0.1)),
                vol.Required(CONF_CONTINUOUS_RUN_MIN, default=current.get(CONF_CONTINUOUS_RUN_MIN, DEFAULT_CONTINUOUS_RUN_MIN)): selector.NumberSelector(selector.NumberSelectorConfig(min=15, max=720, step=5, unit_of_measurement="min")),
                vol.Required(CONF_SAMPLE_INTERVAL_SEC, default=current.get(CONF_SAMPLE_INTERVAL_SEC, DEFAULT_SAMPLE_INTERVAL_SEC)): selector.NumberSelector(selector.NumberSelectorConfig(min=15, max=600, step=15, unit_of_measurement="sec")),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
