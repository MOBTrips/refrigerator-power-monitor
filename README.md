# Refrigerator Power Monitor

A Home Assistant custom integration that creates a virtual refrigerator/freezer monitoring device from an existing power sensor.

It is designed for cases where you do **not** have a refrigerator/freezer door contact sensor, but you do have a power monitor on the refrigerator circuit or plug. The integration watches refrigerator power behavior and exposes anomaly entities that can be used to notify you when a refrigerator or lower freezer drawer is probably left open.

## What it creates

For each configured refrigerator/freezer, the integration creates one Home Assistant device with these entities:

### Binary sensors

- **Compressor running** — on when power is within the configured compressor-running range.
- **Power anomaly** — on when recent power and compressor duty cycle are both unusually high compared with baseline.
- **Continuous run anomaly** — on when the compressor appears to have run continuously longer than the configured threshold.

### Sensors

- **Current power**
- **Recent average power**
- **Baseline average power**
- **Power ratio**
- **Recent duty cycle**
- **Baseline duty cycle**
- **Continuous run**
- **Monitor status**

## How it works

The integration subscribes to the selected power sensor and samples it on a configurable interval. It keeps a rolling local sample history and calculates:

- Recent average power
- Baseline average power
- Recent compressor duty cycle
- Baseline compressor duty cycle
- Continuous compressor run time
- Power ratio

A power anomaly is detected when both are true:

1. Recent compressor duty cycle is high and much higher than the baseline duty cycle.
2. Recent average power is elevated and much higher than the baseline average power.

A continuous-run anomaly is detected separately, which can work even before a long baseline has been collected.

## Why this exists

A refrigerator/freezer door left slightly open usually causes the compressor to run more than normal and the average power to remain elevated. This integration detects that pattern without requiring a door sensor.

It does **not** instantly know that a door is open. It detects abnormal refrigerator behavior after the refrigerator starts working unusually hard.

## Installation through HACS as a custom repository

1. Push this repository to GitHub.
2. In Home Assistant, open **HACS**.
3. Open the three-dot menu.
4. Choose **Custom repositories**.
5. Add your GitHub repository URL.
6. Select category **Integration**.
7. Install **Refrigerator Power Monitor**.
8. Restart Home Assistant.

HACS custom repository instructions are documented by HACS. See the citations in the chat response that provided this project.

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
   - Defrost/high-load exclusion watts, for example `300`
5. Submit.

A new virtual device will appear with the monitor entities.

## Suggested starting thresholds

| Setting | Suggested start |
|---|---:|
| Compressor minimum watts | `60 W` |
| Defrost exclusion watts | `300 W` |
| Recent average window | `30 min` |
| Power baseline window | `24 hr` |
| Recent duty-cycle window | `2 hr` |
| Duty-cycle baseline window | `24 hr` |
| High duty-cycle threshold | `80%` |
| Duty-cycle ratio threshold | `1.8x` |
| Minimum recent average power | `75 W` |
| Power ratio threshold | `2.0x` |
| Continuous run threshold | `120 min` |
| Sample interval | `60 sec` |

Tune these after watching your refrigerator for a few days.

## Automation example

Create a normal Home Assistant automation using the generated device entities.

Example:

```yaml
alias: Kitchen Refrigerator - Possible Door Open
mode: single
trigger:
  - platform: state
    entity_id:
      - binary_sensor.kitchen_refrigerator_power_anomaly
      - binary_sensor.kitchen_refrigerator_continuous_run_anomaly
    to: "on"
    for:
      minutes: 5
action:
  - action: notify.mobile_app_your_phone
    data:
      title: "Check refrigerator/freezer"
      message: >
        The Kitchen Refrigerator is showing abnormal power behavior.
        Check the freezer drawer and refrigerator doors.
```

## Entity attributes for troubleshooting

Most entities include diagnostic attributes such as:

- `reason`
- `status`
- `source_power_sensor`
- `sample_count`
- `baseline_ready`
- `current_power_w`
- `power_recent_average_w`
- `power_baseline_average_w`
- `power_ratio`
- `duty_cycle_recent_pct`
- `duty_cycle_baseline_pct`
- `continuous_run_minutes`

## Baseline learning

After first setup or after clearing storage, the monitor status will show `learning_baseline` until enough samples exist. The continuous-run anomaly can still work before a full baseline is ready.

## Limitations

- This does not replace a physical door sensor.
- Defrost heaters, ice makers, warm groceries, and frequent door openings can affect power behavior.
- The integration is only as accurate as the power sensor and the chosen thresholds.
- After a restart, sample history is restored from Home Assistant storage, but continuous-run timing starts fresh.

## Repository layout

```text
custom_components/
  refrigerator_power_monitor/
    __init__.py
    binary_sensor.py
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

## Development notes

This project intentionally keeps the anomaly logic inside the integration rather than YAML packages or blueprints. That avoids Home Assistant blueprint/template limitations and makes the install experience much cleaner.

## License

MIT License. See `LICENSE`.
