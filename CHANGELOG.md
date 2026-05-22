# Changelog

## v0.2.1

### Fixed
- Fixed Home Assistant setup failure caused by internal storage version mismatch when upgrading from earlier releases.
- Keeps stored rolling sample history compatible with v0.1.x installations.


## v0.2.0

### Added

- Defrost active binary sensor.
- No-idle recovery anomaly binary sensor.
- Reset baseline button.
- Last event type sensor.
- Cooling trend sensor.
- Alert level sensor.
- Alert reason sensor.
- Idle time recent sensor.
- Time since idle sensor.
- Defrost count 24h sensor.
- Short spike count 24h sensor.
- Last defrost duration sensor.
- Anomaly confidence sensor.
- Suggested threshold sensors.
- More detailed diagnostic attributes.
- Expanded README with tuning, troubleshooting, dashboard, and automation examples.

### Changed

- Improved event classification for compressor, idle, defrost, short spikes, and unknown high-power events.
- Suppresses main anomaly alerts during defrost-like high-power events.
- Adds heavy-use and recovering-from-load status classification.
- Allows compressor and high-power thresholds to be changed from the options/gear page.
- Updates HACS metadata to include the button platform.

## v0.1.1

- Fixed options flow gear/settings page compatibility.

## v0.1.0

- Initial release.