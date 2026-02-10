import logging
from decimal import ROUND_HALF_UP, Decimal
from typing import NamedTuple

from app.data.data_loader import DataLoader, PriceRecord

logger = logging.getLogger(__name__)


class PriceStatistics(NamedTuple):
    mean: Decimal
    count: int
    state: str


class StateNotFoundError(Exception):
    pass


class PriceService:
    def __init__(self, data_loader: DataLoader, decimal_places: int = 2):
        self._data_loader = data_loader
        self._decimal_places = decimal_places
        self._stats_cache: dict[str, PriceStatistics] = {}

    def get_mean_price(self, state: str) -> PriceStatistics:
        normalised_state = state.upper().strip()

        if normalised_state in self._stats_cache:
            logger.debug(f"Cache hit for state: {normalised_state}")
            return self._stats_cache[normalised_state]

        records = self._data_loader.get_prices_for_state(normalised_state)

        if records is None:
            available = self._data_loader.get_available_states()
            raise StateNotFoundError(f"State '{state}' not found. Available states: {available}")

        stats = self._calculate_statistics(records, normalised_state)

        self._stats_cache[normalised_state] = stats
        logger.debug(f"Cached statistics for state: {normalised_state}")

        return stats

    def _calculate_statistics(self, records: list[PriceRecord], state: str) -> PriceStatistics:
        total = sum((r.price for r in records), Decimal(0))
        count = len(records)

        mean = total / count

        quantize_str = "0." + "0" * self._decimal_places
        rounded_mean = mean.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)

        return PriceStatistics(mean=rounded_mean, count=count, state=state)

    def get_available_states(self) -> list[str]:
        return self._data_loader.get_available_states()

    def clear_cache(self) -> None:
        self._stats_cache.clear()
        logger.debug("Statistics cache cleared")
