# Changelog

## v0.3.0 - Auto-Tune Assistant

Adds an Auto-Tune Assistant to reduce manual threshold tuning.

### Added

- Auto-tune mode option:
  - `off`
  - `suggest_only`
  - `auto_apply`
- Sensitivity option:
  - `low`
  - `normal`
  - `high`
- New buttons:
  - Analyze baseline
  - Apply suggested thresholds
  - Reset baseline
- New suggested-threshold sensors:
  - Suggested compressor minimum
  - Suggested defrost threshold
  - Suggested average power minimum
  - Suggested high duty-cycle threshold
  - Suggested power ratio threshold
  - Suggested duty-cycle ratio threshold
  - Suggested continuous run threshold
- New auto-tune status sensor.

### Notes

- `suggest_only` is the recommended default.
- `auto_apply` only applies suggestions after the monitor has enough baseline data and throttles updates to avoid constant option changes.
- Storage version remains `1` for compatibility with v0.1/v0.2 history data.

## v0.2.1 - Storage Compatibility Fix

- Keeps internal storage version at `1` to avoid migration errors when upgrading from earlier releases.

## v0.2.0 - Event Classification and Diagnostics

- Defrost detection and anomaly suppression.
- Short spike classification for ice-maker/accessory-like events.
- Idle recovery tracking.
- No-idle recovery anomaly detection.
- Warm-load recovery and heavy-use classification.
- Alert level, alert reason, and confidence sensors.
- Suggested threshold sensors.
- Reset baseline button.

## v0.1.1 - Fix Options Flow

- Fixes gear/settings page options flow error on newer Home Assistant versions.

## v0.1.0 - Initial Release

- Initial HACS custom integration release.
