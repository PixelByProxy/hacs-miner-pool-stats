"""The Pool sensor platform."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import (
    KEY_BEST_DIFFICULTY,
    KEY_CURRENT_BALANCE,
    KEY_HASH_RATE,
    KEY_TOTAL_PAID,
    KEY_WORKER_COUNT,
    UNIT_DIFFICULTY,
    UNIT_HASH_RATE,
    UNIT_WORKER_COUNT,
    CryptoCoin,
)
from .coordinator import PoolConfigEntry, PoolCoordinator
from .entity import PoolAddressDeviceEntity, PoolAddressWorkerDeviceEntity
from .pool import PoolAddressData, PoolAddressWorkerData, PoolInitData

# Coordinator is used to centralize the data updates.
PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class PoolAddressSensorEntityDescription(SensorEntityDescription):
    """Class describing Pool Address sensor entities."""

    value_fn: Callable[[PoolAddressData], StateType]
    is_currency: bool = False


@dataclass(frozen=True, kw_only=True)
class PoolAddressWorkerEntityDescription(SensorEntityDescription):
    """Class describing Pool Address Worker sensor entities."""

    value_fn: Callable[[PoolAddressWorkerData], StateType]


ADDRESS_SENSOR_DESCRIPTIONS = [
    PoolAddressSensorEntityDescription(
        key=KEY_TOTAL_PAID,
        translation_key=KEY_TOTAL_PAID,
        state_class=SensorStateClass.MEASUREMENT,
        is_currency=True,
        value_fn=lambda data: data.total_paid,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PoolAddressSensorEntityDescription(
        key=KEY_CURRENT_BALANCE,
        translation_key=KEY_CURRENT_BALANCE,
        state_class=SensorStateClass.MEASUREMENT,
        is_currency=True,
        value_fn=lambda data: data.current_balance,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PoolAddressSensorEntityDescription(
        key=KEY_WORKER_COUNT,
        translation_key=KEY_WORKER_COUNT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UNIT_WORKER_COUNT,
        value_fn=lambda data: len(data.worker_list),
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PoolAddressSensorEntityDescription(
        key=KEY_BEST_DIFFICULTY,
        translation_key=KEY_BEST_DIFFICULTY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UNIT_DIFFICULTY,
        value_fn=lambda data: data.best_difficulty,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
]

WORKER_SENSOR_DESCRIPTIONS = [
    PoolAddressWorkerEntityDescription(
        key=KEY_BEST_DIFFICULTY,
        translation_key=KEY_BEST_DIFFICULTY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UNIT_DIFFICULTY,
        value_fn=lambda worker: worker.best_difficulty,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PoolAddressWorkerEntityDescription(
        key=KEY_HASH_RATE,
        translation_key=KEY_HASH_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UNIT_HASH_RATE,
        value_fn=lambda worker: worker.hash_rate,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: PoolConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Miner Pool sensor platform."""
    coordinator = config_entry.runtime_data

    sensors: list[SensorEntity] = []

    for address_desc in ADDRESS_SENSOR_DESCRIPTIONS:
        address_value = address_desc.value_fn(coordinator.data)
        if address_value is not None:
            address_sensor = PoolAddressSensorEntity(
                coordinator, address_desc, config_entry
            )
            sensors.append(address_sensor)

    for worker_desc in WORKER_SENSOR_DESCRIPTIONS:
        for worker in coordinator.data.worker_list:
            worker_value = worker_desc.value_fn(worker)
            if worker_value is not None:
                worker_sensor = PoolAddressWorkerSensorEntity(
                    coordinator, worker_desc, config_entry, worker
                )
                sensors.append(worker_sensor)

    async_add_entities(sensors)


class PoolAddressSensorEntity(PoolAddressDeviceEntity, SensorEntity):
    """Representation of a Pool Address sensor."""

    entity_description: PoolAddressSensorEntityDescription

    def __init__(
        self,
        coordinator: PoolCoordinator,
        description: PoolAddressSensorEntityDescription,
        config_entry: PoolConfigEntry,
    ) -> None:
        """Initialize the Pool Address sensor."""
        pool_config = PoolInitData(dict(config_entry.data))
        super().__init__(coordinator, config_entry, pool_config)
        self.entity_description = description
        self._attr_unique_id = f"{config_entry.entry_id}-{description.key}"
        self._attr_translation_key = description.translation_key
        self.entity_id = f"{SENSOR_DOMAIN}.{pool_config.unique_id}_{description.key}"
        # convert to coin currency if applicable
        if self.entity_description.is_currency:
            try:
                self._attr_native_unit_of_measurement = CryptoCoin(
                    pool_config.coin_key
                ).name
            except ValueError:
                self._attr_native_unit_of_measurement = pool_config.coin_name
        self._update_properties()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_properties()
        self.async_write_ha_state()

    @callback
    def _update_properties(self) -> None:
        """Update sensor properties."""
        self._attr_native_value = self.entity_description.value_fn(
            self.coordinator.data
        )


class PoolAddressWorkerSensorEntity(PoolAddressWorkerDeviceEntity, SensorEntity):
    """Representation of a Pool Address Worker sensor."""

    entity_description: PoolAddressWorkerEntityDescription
    is_online: bool = True

    def __init__(
        self,
        coordinator: PoolCoordinator,
        description: PoolAddressWorkerEntityDescription,
        config_entry: PoolConfigEntry,
        worker: PoolAddressWorkerData,
    ) -> None:
        """Initialize the Pool Address Worker sensor."""
        pool_config = PoolInitData(dict(config_entry.data))
        super().__init__(coordinator, config_entry, pool_config, worker.name)
        self.entity_description = description
        self.worker = worker
        self._attr_unique_id = (
            f"{config_entry.entry_id}-{worker.name}-{description.key}"
        )
        self._attr_translation_key = description.translation_key
        self.entity_id = (
            f"{SENSOR_DOMAIN}.{pool_config.unique_id}_{worker.name}_{description.key}"
        )
        self._update_properties()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        updated_worker = next(
            (
                w
                for w in self.coordinator.data.worker_list
                if w.name == self.worker_name
            ),
            None,
        )
        if updated_worker is not None:
            self.worker = updated_worker
            self.is_online = True
        else:
            self.is_online = False
        self._update_properties()
        self.async_write_ha_state()

    @callback
    def _update_properties(self) -> None:
        """Update sensor properties."""
        self._attr_native_value = self.entity_description.value_fn(self.worker)

    @property
    def available(self) -> bool:
        """Check if device and sensor is available in data."""
        return super().available and self.is_online
