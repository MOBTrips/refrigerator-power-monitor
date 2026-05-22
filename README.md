# Refrigerator Power Monitor

A Home Assistant custom integration that creates a virtual refrigerator/freezer monitoring device from an existing power sensor.

It is designed for cases where you do not have a refrigerator/freezer door contact sensor, but you do have a power monitor on the refrigerator circuit or plug. The integration watches refrigerator power behavior and exposes anomaly entities that can be used to notify you when a refrigerator or lower freezer drawer is probably left open.

> This is probable detection, not true door detection. A physical contact sensor is still the best way to know immediately that a door is open.

## What is new in v0.2.0

This release adds richer event classification and more user-friendly diagnostics:

- Defrost detection and suppression
- Short high-power spike classification for ice maker/accessory-like events
- Idle recovery tracking
- No-idle recovery anomaly detection
- Cooling trend detection
- Warm-load / recovery classification
- Heavy-use / frequent-opening classification
- Alert level and alert reason sensors
- Anomaly confidence score
- Suggested threshold sensors
- Reset baseline button
- Expanded entity attributes and documentation

## What it creates

For each configured refrigerator/freezer, the integration creates one Home Assistant device.

### Binary sensors

- **Compressor running** — on when power is within the configured compressor-running range.
- **Defrost active** — on when a high-power event looks like a defrost cycle.
- **Power anomaly** — on when recent power and compressor duty cycle are both unusually high compared with baseline, or no idle recovery is detected.
- **Continuous run anomaly** — on when the compressor appears to have run continuously longer than the configured threshold.
- **No idle recovery anomaly** — on when the refrigerator has not returned to idle for too long while cooling.

### Sensors

- Current power
- Recent average power
- Baseline average power
- Power ratio
- Recent duty cycle
- Baseline duty cycle
- Idle time recent
- Time since idle
- Continuous run
- Defrost count 24h
- Short spike count 24h
- Last defrost duration
- Anomaly confidence
- Suggested compressor minimum
- Suggested defrost threshold
- Suggested average power minimum
- Monitor status
- Last event type
- Cooling trend
- Alert level
- Alert reason

### Button

- **Reset baseline** — clears stored rolling history and starts learning again.

## How it works

The integration subscribes to the selected power sensor and samples it on a configurable interval. It keeps a rolling local sample history and calculates:

- Recent average power
- Baseline average power
- Recent compressor duty cycle
- Baseline compressor duty cycle
- Idle recovery time
- Continuous compressor run time
- Power ratio
- Cooling trend
- Defrost-like events
- Short high-power spikes

A power anomaly is detected when recent compressor duty cycle and average power are both unusually high versus baseline, or when the fridge has not returned to idle for too long.

Defrost and short spike classification help avoid false positives from defrost heaters, ice makers, valves, and other accessory loads.

## Event types

The `Last event type` sensor may show:

| Event type | Meaning |
|---|---|
| `idle` | Power is at or below the compressor minimum threshold |
| `compressor` | Power is within the compressor-running band |
| `defrost` | High-power event has lasted long enough to look like defrost |
| `short_spike` | Brief high-power event, often accessory/ice-maker-like |
| `unknown_high_power` | High-power event outside normal defrost timing |
| `unavailable` | Power sensor is unavailable or non-numeric |

## Monitor status

The `Monitor status` sensor may show:

| Status | Meaning |
|---|---|
| `learning_baseline` | Collecting enough samples to establish normal behavior |
| `monitoring` | Baseline is ready and no anomaly is active |
| `cooling` | Compressor is running normally |
| `defrosting` | A high-power defrost-like event is active |
| `recovering_from_load` | Cooling is high but trending down, often after warm groceries |
| `heavy_use` | Duty cycle is high but idle recovery is still present |
| `alert` | An anomaly is active |
| `power_sensor_unavailable` | Source power sensor is unavailable or non-numeric |

## Alert level

The `Alert level` sensor may show:

| Level | Meaning |
|---|---|
| `normal` | No concern |
| `watch` | Interesting behavior, but likely explainable |
| `warning` | Abnormal behavior worth checking |
| `critical` | Stronger probability of a real issue |

## Alert reason

The `Alert reason` sensor may show:

| Reason | Meaning |
|---|---|
| `none` | No issue |
| `baseline_learning` | Still collecting baseline samples |
| `power_sensor_unavailable` | Source power sensor is unavailable |
| `defrost_active` | Defrost-like high-power event is active |
| `short_power_spike` | Brief accessory-like spike detected |
| `recovering_from_warm_load` | High load is trending down |
| `heavy_use_or_frequent_openings` | High duty cycle but idle recovery exists |
| `high_duty_cycle_and_power` | Main power anomaly logic triggered |
| `continuous_compressor_runtime` | Compressor has run too long continuously |
| `no_idle_recovery` | Refrigerator has not returned to idle for too long |

## Installation through HACS as a custom repository

1. Push this repository to GitHub.
2. In Home Assistant, open HACS.
3. Open the three-dot menu.
4. Choose **Custom repositories**.
5. Add your GitHub repository URL.
6. Select category **Integration**.
7. Install **Refrigerator Power Monitor**.
8. Restart Home Assistant.

## Manual installation

Copy this folder:

```text
custom_components/refrigerator_power_monitor
```

into:

```text
/homeassistant/custom_components/refrigerator_power_monitor
```

Then restart Home Assistant.

## Add a refrigerator device

After installation and restart:

1. Go to **Settings → Devices & services**.
2. Select **Add integration**.
3. Search for **Refrigerator Power Monitor**.
4. Enter:
   - Device name, for example `Kitchen Refrigerator`
   - Power sensor, for example `sensor.refrigerator_power_2`
   - Compressor minimum watts, for example `60`
   - High-power / defrost threshold watts, for example `300`
5. Submit.

A new virtual device will appear with the monitor entities.

## Suggested starting thresholds

| Setting | Suggested start |
|---|---:|
| Compressor minimum watts | `60 W` |
| High-power / defrost threshold watts | `300 W` |
| Recent average window | `30 min` |
| Power baseline window | `24 hr` |
| Recent duty-cycle window | `2 hr` |
| Duty-cycle baseline window | `24 hr` |
| High duty-cycle threshold | `80%` |
| Duty-cycle ratio threshold | `1.8x` |
| Minimum recent average power | `75 W` |
| Power ratio threshold | `2.0x` |
| Continuous run threshold | `120 min` |
| Defrost minimum duration | `3 min` |
| Defrost maximum duration | `60 min` |
| Short spike maximum duration | `3 min` |
| Idle recovery lookback | `2 hr` |
| No-idle recovery threshold | `90 min` |
| Cooling trend threshold | `10%` |
| Sample interval | `60 sec` |

Tune these after watching your refrigerator for a few days.

## Example automation

```yaml
alias: Kitchen Refrigerator - Possible Door Open
mode: single
trigger:
  - platform: state
    entity_id:
      - binary_sensor.kitchen_refrigerator_power_anomaly
      - binary_sensor.kitchen_refrigerator_continuous_run_anomaly
      - binary_sensor.kitchen_refrigerator_no_idle_recovery_anomaly
    to: "on"
    for:
      minutes: 5
action:
  - action: notify.mobile_app_your_phone
    data:
      title: "Check refrigerator/freezer"
      message: >
        The Kitchen Refrigerator is showing abnormal power behavior.
        Status: {{ states('sensor.kitchen_refrigerator_monitor_status') }}.
        Reason: {{ states('sensor.kitchen_refrigerator_alert_reason') }}.
        Confidence: {{ states('sensor.kitchen_refrigerator_anomaly_confidence') }}%.
        Check the freezer drawer, refrigerator doors, blocked vents, warm groceries, frost buildup, and condenser airflow.
```

## Example dashboard card

```yaml
type: entities
title: Kitchen Refrigerator Monitor
entities:
  - entity: sensor.kitchen_refrigerator_monitor_status
  - entity: sensor.kitchen_refrigerator_alert_level
  - entity: sensor.kitchen_refrigerator_alert_reason
  - entity: sensor.kitchen_refrigerator_anomaly_confidence
  - entity: binary_sensor.kitchen_refrigerator_power_anomaly
  - entity: binary_sensor.kitchen_refrigerator_continuous_run_anomaly
  - entity: binary_sensor.kitchen_refrigerator_no_idle_recovery_anomaly
  - entity: binary_sensor.kitchen_refrigerator_defrost_active
  - entity: binary_sensor.kitchen_refrigerator_compressor_running
  - entity: sensor.kitchen_refrigerator_current_power
  - entity: sensor.kitchen_refrigerator_power_ratio
  - entity: sensor.kitchen_refrigerator_recent_duty_cycle
  - entity: sensor.kitchen_refrigerator_time_since_idle
  - entity: button.kitchen_refrigerator_reset_baseline
```

Entity IDs depend on the device name and Home Assistant's entity registry.

## Troubleshooting checklist

If you get an alert:

1. Check the freezer drawer and refrigerator doors.
2. Check if warm groceries were recently added.
3. Check if the fridge has been opened frequently.
4. Check if vents are blocked inside the refrigerator/freezer.
5. Check for frost buildup.
6. Check condenser coils and airflow.
7. Check if the room temperature is unusually high.
8. Review the source power graph for continuous running, defrost events, and short spikes.

## Understanding common patterns

| Situation | Likely pattern |
|---|---|
| Door left open | Continuous compressor, high duty cycle, little/no idle recovery |
| Warm groceries | High duty cycle but cooling trend decreases over time |
| Frequent door openings | Higher duty cycle but still returns to idle periodically |
| Defrost | High wattage above compressor range for a limited duration |
| Ice maker/accessory | Brief high-power spikes |
| Dirty coils/failing fridge | Repeated high duty cycle across many days |

## Resetting the baseline

Use the **Reset baseline** button when:

- You changed major thresholds
- You moved the refrigerator
- You replaced the refrigerator
- You changed the power monitor
- The stored baseline looks wrong

After reset, `monitor_status` will return to `learning_baseline` until enough samples are collected.

## Entity attributes for troubleshooting

Most entities include diagnostic attributes such as:

- `reason`
- `status`
- `alert_level`
- `alert_reason`
- `anomaly_confidence`
- `source_power_sensor`
- `sample_count`
- `baseline_ready`
- `current_power_w`
- `power_recent_average_w`
- `power_baseline_average_w`
- `power_ratio`
- `duty_cycle_recent_pct`
- `duty_cycle_baseline_pct`
- `idle_time_recent_minutes`
- `time_since_idle_minutes`
- `continuous_run_minutes`
- `last_event_type`
- `cooling_trend`
- `defrost_count_24h`
- `short_spike_count_24h`
- `suggested_compressor_min_w`
- `suggested_defrost_min_w`
- `suggested_average_power_minimum_w`

## Limitations

- This does not replace a physical door sensor.
- It cannot know for certain that warm groceries were added or that a door was opened frequently.
- Defrost heaters, ice makers, room temperature, blocked vents, dirty coils, and failing components can affect power behavior.
- Suggested thresholds are estimates from observed power data and should be reviewed by the user.
- After a restart, sample history is restored from Home Assistant storage, but current continuous-run timing starts fresh.

## Repository layout

```text
custom_components/
  refrigerator_power_monitor/
    __init__.py
    binary_sensor.py
    button.py
    config_flow.py
    const.py
    entity.py
    manifest.json
    monitor.py
    sensor.py
    translations/
      en.json
hacs.json
README.md
```

## License

MIT


## v0.2.1 storage compatibility note

Version 0.2.1 keeps the internal storage schema at version `1` so existing installations from v0.1.x can load their saved rolling samples without Home Assistant requesting a storage migration. If you saw `NotImplementedError` from `homeassistant.helpers.storage`, update to v0.2.1 or newer, redownload through HACS, and restart Home Assistant.
