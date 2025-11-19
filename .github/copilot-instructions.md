# Copilot instructions for Miner Pool Stats

Purpose: Help AI coding agents become productive quickly in this Home Assistant custom integration.

1) Big picture
- This is a Home Assistant custom integration at `custom_components/miner_pool_stats`.
- Core responsibility: poll several mining pool APIs and expose address/worker sensors.
- Main runtime pieces: `PoolCoordinator` (DataUpdateCoordinator) holds a `PoolClient` API
  implementation (created by `PoolFactory`). Entities are sensors built from coordinator data.

2) Key files (roles)
- `__init__.py`: sets up the integration and stores the coordinator in `entry.runtime_data`.
- `coordinator.py`: `PoolCoordinator` creates the `PoolClient` via `PoolFactory`, handles
  periodic updates and debouncing.
- `factory.py`: maps `CONF_POOL_KEY` values to specific `PoolClient` subclasses (e.g. `pool_f2.py`).
- `pool.py`: base `PoolClient`, dataclasses for `PoolInitData`, `PoolAddressData`, and history helpers.
- `sensor.py`: defines sensors via dataclass `SensorEntityDescription` with `value_fn` lambdas.
- `config_flow.py`: config entry flow (uses selectors/voluptuous); constructs unique ids and titles.
- `entity.py`: base CoordinatorEntity device handling and device_info identifiers.
- `const.py`: all config keys, pool-source keys, and units (single source of truth).

3) Important patterns & conventions (use these exactly)
- Factory pattern: use `PoolFactory.get(hass, config_data)` to obtain a `PoolClient` for tests or mocks.
- Coordinator pattern: `PoolCoordinator` is stored on the `ConfigEntry` as `runtime_data`.
- Debounce: coordinator uses `homeassistant.helpers.debounce.Debouncer` and an update interval of 300s.
- Entity creation: `sensor.py` loops `ADDRESS_SENSOR_DESCRIPTIONS` and `WORKER_SENSOR_DESCRIPTIONS` and
  constructs sensors only if `value_fn` returns non-None. Follow the same `SensorEntityDescription` + `value_fn`
  approach for new sensors.
- Unique IDs and entity_ids: unique_id is constructed in `config_flow.py` as
  `"{pool_key}_{coin_key}_{address.lower()}"`. Entity IDs follow `sensor` domain naming in `sensor.py`:
  `f"{SENSOR_DOMAIN}.{pool_config.unique_id}_{...}"`.
- Device identifiers: `DeviceInfo.identifiers` use `(DOMAIN, entry_id)` for addresses or `(DOMAIN, f"{entry_id}-{worker}")` for workers.
- Translations: `translations/en.json` and `strings.json` are used for translation/labels and `translation_key` usage.
- Error handling: pool IO failures raise `PoolConnectionError`; coordinator converts to `ConfigEntryNotReady` or `UpdateFailed`.

4) Integration/side-effects to be aware of
- Uses Home Assistant `recorder` and `history` in `pool.py` for computing historical maxima.
- `manifest.json` lists `recorder` as a dependency and no external Python requirements.
- No test suite present in repo (no tests directory). Development validation is typically by loading the
  integration into a Home Assistant dev instance and exercising the config flow.

5) Small examples and pointers
- Adding a new pool source:
  - Add a `POOL_SOURCE_*_KEY` in `const.py` and add to `config_flow.py` selector.
  - Implement `PoolClient` subclass in a new `pool_<source>.py` with `async_get_data()` and optional `async_initialize()`.
  - Register it in `factory.py` to be returned by `PoolFactory.get()`.
- Adding a new sensor:
  - Add a `PoolAddressSensorEntityDescription` to `ADDRESS_SENSOR_DESCRIPTIONS` (or worker list), provide `value_fn`.
  - Ensure `value_fn` returns `None` when not applicable.

6) What NOT to change lightly
- Changing the unique_id format will break existing entity ownership and stored entity registry entries.
- Changing device identifiers will unlink devices in the user's registry.

7) If you need more info
- Look at `coordinator.py`, `factory.py`, `pool.py`, `sensor.py`, and `config_flow.py` first — they capture the core flows.
- Ask for explicit examples if you want a sample `PoolClient` implementation or a sample test harness.

If anything above is unclear or you'd like me to expand examples (e.g., add a sample `pool_xxx.py`), tell me what to include.
