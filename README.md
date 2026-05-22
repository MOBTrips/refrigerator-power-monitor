# Refrigerator Power Monitor

A Home Assistant custom integration that creates a virtual refrigerator/freezer monitoring device from an existing power sensor.

It watches refrigerator power behavior to detect probable problems such as a freezer drawer left open, a door left open, continuous compressor runtime, unusually high duty cycle, no idle recovery, and abnormal power usage.

> This is probable detection based on power behavior. It is not a replacement for a physical door contact sensor, but it can catch many real-world refrigerator/freezer problems when you already have a power monitor installed.

## Features

- Creates one Home Assistant device per refrigerator/freezer monitor.
- Uses an existing power sensor such as a smart plug, circuit monitor, or energy monitor.
- Tracks rolling power history internally.
- Classifies refrigerator behavior:
  - Idle
  - Compressor running
  - Defrost-like high-power event
  - Short spike / accessory event
  - Unknown high-power event
- Detects:
  - Power anomaly
  - Continuous run anomaly
  - No idle recovery anomaly
  - Defrost active
- Exposes diagnostic sensors:
  - Current power
  - Recent average power
  - Baseline average power
  - Power ratio
  - Recent duty cycle
  - Baseline duty cycle
  - Idle time recent
  - Time since idle
  - Continuous run time
  - Alert level
  - Alert reason
  - Anomaly confidence
  - Monitor status
  - Last event type
  - Cooling trend
- Includes Auto-Tune Assistant:
  - Suggested thresholds
  - Analyze baseline button
  - Apply suggested thresholds button
  - Optional auto-apply mode

## Installation with HACS

1. In Home Assistant, open **HACS**.
2. Go to **Integrations**.
3. Open the three-dot menu.
4. Choose **Custom repositories**.
5. Add this repository URL:

```text
https://github.com/MOBTrips/refrigerator-power-monitor
```

6. Select category **Integration**.
7. Install **Refrigerator Power Monitor**.
8. Restart Home Assistant.

## Add a refrigerator monitor

Go to:

```text
Settings → Devices & services → Add integration → Refrigerator Power Monitor
```

Enter:

- Device name, for example `Kitchen Refrigerator`
- Power sensor, for example `sensor.refrigerator_power_2`
- Initial compressor minimum watts
- Initial high-power / defrost threshold watts

The integration creates a virtual device with multiple sensors and binary sensors.

## Auto-Tune Assistant

Version `0.3.0` adds an Auto-Tune Assistant to make setup easier.

### Auto-tune modes

| Mode | Behavior |
|---|---|
| `off` | Does not suggest or apply threshold changes. |
| `suggest_only` | Calculates suggested thresholds and exposes them as sensors. This is the recommended default. |
| `auto_apply` | Periodically applies safe suggested thresholds after enough baseline data is available. |

### Sensitivity

| Sensitivity | Behavior |
|---|---|
| `low` | Fewer alerts, more tolerant of heavy use. |
| `normal` | Balanced default. |
| `high` | More sensitive, may alert sooner. |

### Auto-tune buttons

| Button | Purpose |
|---|---|
| Reset baseline | Clears rolling history and starts learning again. |
| Analyze baseline | Recalculates suggested thresholds from existing history. |
| Apply suggested thresholds | Applies the currently suggested thresholds to the integration options. |

Recommended workflow:

1. Install the integration.
2. Leave auto-tune mode on `suggest_only`.
3. Let the refrigerator run normally for 24–72 hours.
4. Review the suggested threshold sensors.
5. Press **Apply suggested thresholds** if the suggestions look reasonable.
6. Keep `auto_apply` disabled unless you are comfortable with the integration periodically updating thresholds.

## Important entities

### Binary sensors

| Entity | Meaning |
|---|---|
| Compressor running | Power is in the configured compressor range. |
| Defrost active | High-power event looks like a defrost cycle. |
| Power anomaly | Combined abnormal power/duty-cycle behavior. |
| Continuous run anomaly | Compressor has run continuously longer than the configured threshold. |
| No idle recovery anomaly | Refrigerator has not returned to idle for too long. |

### Diagnostic sensors

| Sensor | Meaning |
|---|---|
| Monitor status | Current monitor state, such as learning, cooling, defrosting, heavy use, alert. |
| Alert level | `normal`, `watch`, `warning`, or `critical`. |
| Alert reason | Human-readable reason code for the current state. |
| Anomaly confidence | 0–100 score based on multiple signals. |
| Power ratio | Recent average power divided by baseline average power. |
| Recent duty cycle | Percent of recent samples where compressor was running. |
| Baseline duty cycle | Longer-term compressor runtime baseline. |
| Idle time recent | Estimated idle time in the recent lookback window. |
| Time since idle | How long since the monitor last saw idle behavior. |

## Suggested dashboard card

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
  - entity: sensor.kitchen_refrigerator_baseline_duty_cycle
  - entity: sensor.kitchen_refrigerator_auto_tune_status
  - entity: button.kitchen_refrigerator_analyze_baseline
  - entity: button.kitchen_refrigerator_apply_suggested_thresholds
  - entity: button.kitchen_refrigerator_reset_baseline
```

## Example notification automation

```yaml
alias: Kitchen Refrigerator - Power Anomaly Alert
mode: single
trigger:
  - platform: state
    entity_id:
      - binary_sensor.kitchen_refrigerator_power_anomaly
      - binary_sensor.kitchen_refrigerator_continuous_run_anomaly
      - binary_sensor.kitchen_refrigerator_no_idle_recovery_anomaly
    to: "on"
    for:
      minutes: 10
action:
  - action: notify.mobile_app_your_phone
    data:
      title: "Check refrigerator"
      message: >
        Kitchen Refrigerator may need attention.
        Status: {{ states('sensor.kitchen_refrigerator_monitor_status') }}.
        Alert level: {{ states('sensor.kitchen_refrigerator_alert_level') }}.
        Reason: {{ states('sensor.kitchen_refrigerator_alert_reason') }}.
        Confidence: {{ states('sensor.kitchen_refrigerator_anomaly_confidence') }}%.
```

## Tuning guidance

Start with these approximate values for many standard refrigerators:

| Setting | Starting point |
|---|---:|
| Compressor minimum watts | 60 W |
| High-power / defrost threshold | 300 W |
| High duty-cycle threshold | 80% |
| Power ratio threshold | 2.0x |
| Duty-cycle ratio threshold | 1.8x |
| Continuous run threshold | 120 min |
| No-idle threshold | 90 min |

Then let Auto-Tune Assistant make suggestions after several days of normal operation.

## Interpreting common situations

| Situation | Likely monitor behavior |
|---|---|
| Door/freezer drawer left open | Continuous run, high duty cycle, no idle recovery, high confidence. |
| Warm groceries added | High duty cycle but cooling trend may decrease over time. |
| Frequent door openings | Higher duty cycle but still some idle recovery. |
| Defrost cycle | Defrost active, anomaly suppressed. |
| Ice maker/accessory | Short spike count increases, usually no alert. |
| Dirty coils/failing fridge | Repeated high duty cycle over many days. |

## Troubleshooting

If setup fails, check:

```text
Settings → System → Logs
```

If no entities update:

- Confirm the selected power sensor exists.
- Confirm the power sensor reports numeric watts.
- Confirm Home Assistant was restarted after HACS installation/update.

If alerts are too sensitive:

- Set sensitivity to `low`.
- Increase continuous run threshold.
- Increase high duty-cycle threshold.
- Increase power ratio threshold.

If alerts are too slow:

- Set sensitivity to `high`.
- Lower continuous run threshold.
- Lower no-idle threshold.

## Development notes

The integration keeps internal rolling samples using Home Assistant storage. Storage version remains `1` for compatibility with earlier releases.
