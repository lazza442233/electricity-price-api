from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.data.data_loader import PriceRecord
from app.services.price_service import PriceService, PriceStatistics, StateNotFoundError


class TestPriceService:
    def test_get_mean_price_valid_state(self, price_service):
        stats = price_service.get_mean_price("NSW")

        assert stats.state == "NSW"
        assert stats.count == 2
        assert stats.mean == Decimal("150.00")  # (100 + 200) / 2

    def test_get_mean_price_case_insensitive(self, price_service):
        stats_lower = price_service.get_mean_price("nsw")
        stats_upper = price_service.get_mean_price("NSW")
        stats_mixed = price_service.get_mean_price("Nsw")

        assert stats_lower.mean == stats_upper.mean == stats_mixed.mean

    def test_get_mean_price_unknown_state(self, price_service):
        with pytest.raises(StateNotFoundError, match="not found"):
            price_service.get_mean_price("UNKNOWN")

    def test_negative_prices_in_mean(self, price_service):
        stats = price_service.get_mean_price("VIC")

        # VIC has 150.00 and -50.00, mean = 50.00
        assert stats.mean == Decimal("50.00")

    def test_caching_behavior(self, price_service):
        """Test that statistics are cached."""
        stats1 = price_service.get_mean_price("NSW")
        stats2 = price_service.get_mean_price("NSW")

        assert stats1 is stats2

    def test_clear_cache(self, price_service):
        """Test cache clearing."""
        stats1 = price_service.get_mean_price("NSW")
        price_service.clear_cache()
        stats2 = price_service.get_mean_price("NSW")

        assert stats1 == stats2
        assert stats1 is not stats2

    def test_get_available_states(self, price_service):
        states = price_service.get_available_states()

        assert set(states) == {"NSW", "VIC"}
        assert states == sorted(states)

    def test_decimal_precision(self):
        # Create mock loader with values that would cause float error
        mock_loader = Mock()
        mock_loader.get_prices_for_state.return_value = [
            PriceRecord("TEST", Decimal("0.1"), datetime.now()) for _ in range(10)
        ]
        mock_loader.get_available_states.return_value = ["TEST"]

        service = PriceService(mock_loader)
        stats = service.get_mean_price("TEST")

        # With floats this would be 0.09999... not 0.10
        assert stats.mean == Decimal("0.10")


class TestPriceStatistics:
    def test_immutable(self):
        stats = PriceStatistics(mean=Decimal("100.00"), count=10, state="NSW")

        with pytest.raises(AttributeError):
            stats.mean = Decimal("200.00")  # type: ignore[misc]

    def test_tuple_unpacking(self):
        stats = PriceStatistics(mean=Decimal("100.00"), count=10, state="NSW")
        mean, count, state = stats

        assert mean == Decimal("100.00")
        assert count == 10
        assert state == "NSW"
