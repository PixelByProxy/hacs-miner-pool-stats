# Miner Pool Stats (Home Assistant integration)

Miner Pool Stats is a Home Assistant custom integration that polls several mining pool
APIs and exposes wallet address and worker sensors (hashrate, best difficulty, balances,
and more) to Home Assistant.

## Features

- Polls multiple supported mining pool providers via pluggable `PoolClient` implementations.
- Exposes sensors for both wallet addresses and individual workers.
- Uses Home Assistant `DataUpdateCoordinator` for centralized polling and debouncing.
- Persists history via the `recorder` integration (used to compute historical maxima).

## Installation

Recommended: install via HACS (Home Assistant Community Store).

1. In Home Assistant open **HACS → Integrations**.
2. Click the three dots (top-right) → **Custom repositories**.
3. Add this repository URL, set **Category** to `Integration`, and click **Add**.
4. Install the integration from HACS and restart Home Assistant.

Manual install

1. Copy the `custom_components/miner_pool_stats` directory into your Home Assistant
   `config/custom_components/` directory.
2. Restart Home Assistant.

Notes

- `manifest.json` declares `recorder` as a dependency. Ensure the `recorder` integration
  is enabled if you rely on historical calculations.
- No additional Python packages are required by this integration.

## Configuration (in-UI)

- Add the integration via **Settings → Devices & Services → Add Integration** and search
  for "Miner Pool Stats".
- The config flow will prompt you to pick a pool source (e.g. `f2pool`, `coin_miners`,
  `public_pool`, `solo_pool`, `ck_pool`, `mining_dutch`) and then collect pool-specific
  settings (coin, API key, account/wallet address, etc.).
- The integration constructs a `unique_id` in the form:

```
{pool_key}_{coin_key}_{address.lower()}
```

Entity IDs are created under the `sensor` domain using the `unique_id` and sensor key,
for example: `sensor.{unique_id}_hash_rate`.

## Developer notes

- Core files:
  - `custom_components/miner_pool_stats/coordinator.py` — `PoolCoordinator` (DataUpdateCoordinator).
  - `custom_components/miner_pool_stats/factory.py` — maps pool keys to `PoolClient` classes.
  - `custom_components/miner_pool_stats/pool.py` — base `PoolClient` and data classes.
  - `custom_components/miner_pool_stats/sensor.py` — sensor descriptions and entity creation.
  - `custom_components/miner_pool_stats/config_flow.py` — UI config flow and unique_id creation.
  - `custom_components/miner_pool_stats/const.py` — constants and coin enum.

- Add a new pool provider:
  1. Create `pool_<provider>.py` implementing `PoolClient.async_get_data()` and optional `async_initialize()`.
  2. Register the provider in `factory.py` to return your client for its `CONF_POOL_KEY`.
  3. Add `POOL_SOURCE_*` keys and labels in `const.py` and update `config_flow.py` selectors.

- Add a new sensor:
  - Add a `PoolAddressSensorEntityDescription` (address-level) or `PoolAddressWorkerEntityDescription` (worker-level)
    to `ADDRESS_SENSOR_DESCRIPTIONS` or `WORKER_SENSOR_DESCRIPTIONS` in `sensor.py` and provide a `value_fn`.
  - `value_fn` should return `None` when the sensor is not applicable for current data.

## Testing locally

To test locally during development:

1. Copy the integration into your HA config `custom_components` folder.
2. Restart Home Assistant (or reload integrations via developer tools where possible).
3. Add the integration via UI and exercise the config flow.

PowerShell example to copy from this repository into a running HA config directory (adjust paths):

```powershell
Copy-Item -Recurse -Force .\custom_components\miner_pool_stats C:\path\to\homeassistant\config\custom_components\miner_pool_stats
```

## Contributing

Contributions are welcome — please open an issue or PR with a clear description of the change.

## License

See the repository `LICENSE` file for license details.