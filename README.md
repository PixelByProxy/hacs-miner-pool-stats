# Miner Pool Stats (Home Assistant Integration)

Miner Pool Stats is a Home Assistant custom integration that polls several mining pool
APIs and exposes wallet address and worker sensors (hashrate, best difficulty, balances,
and more) to Home Assistant.

## Features

- Polls multiple supported mining pool providers to capture wallet and worker data.
- Exposes sensors for both wallet addresses and individual workers.

### Supported Mining Pools

- [CKPool](https://solo.ckpool.org/)
- [Coin-Miners.info](https://coin-miners.info/)
- [F2Pool](https://f2pool.com)
- [Mining Core](http://retromike.net/) (via Umbrel)
- [Mining Dutch](https://www.mining-dutch.nl)
- [Public Pool](https://web.public-pool.io) (hosted or via Umbrel)
- [SoloPool.org](https://solopool.org/)

## Installation

Install via HACS (Home Assistant Community Store).

1. In Home Assistant open **HACS → Integrations**.
2. Click the three dots (top-right) → **Custom repositories**.
3. Add this repository URL, set **Category** to `Integration`, and click **Add**.
4. Install the integration from HACS and restart Home Assistant.

## Configuration (in-UI)

- Add the integration via **Settings → Devices & Services → Add Integration** and search
  for "Miner Pool Stats".
- The config flow will prompt you to pick a pool source (e.g. `CKPool`, `Coin-Miners.info`,
  `F2Pool`, `Mining Core`, `Mining Dutch`, `Public Pool`, `SoloPool.org`) and then collect pool-specific
  settings (coin, API key, account/wallet address, etc.).
- The integration constructs a `unique_id` in the form:

```
{pool_key}_{coin_key}_{address.lower()}
```

Entity IDs are created under the `sensor` domain using the `unique_id` and sensor key,
for example: `sensor.{unique_id}_hash_rate`.

## Contributing

Contributions are welcome — please open an issue or PR with a clear description of the change.

## License

See the repository `LICENSE` file for license details.