from decimal import Decimal
from pathlib import Path

import pytest

from app.data.data_loader import DataLoader, DataLoadError, PriceRecord


class TestDataLoader:
    def test_load_valid_csv(self, sample_csv):
        loader = DataLoader(sample_csv).load()

        assert loader.record_count == 4
        assert set(loader.get_available_states()) == {"NSW", "VIC"}

    def test_load_missing_file(self):
        with pytest.raises(DataLoadError, match="not found"):
            DataLoader(Path("/nonexistent.csv")).load()

    def test_load_empty_csv(self, tmp_path):
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text("")

        with pytest.raises(DataLoadError, match="empty"):
            DataLoader(csv_path).load()

    def test_load_header_only_csv(self, tmp_path):
        csv_path = tmp_path / "header_only.csv"
        csv_path.write_text("state,price,timestamp\n")

        with pytest.raises(DataLoadError, match="no data rows"):
            DataLoader(csv_path).load()

    def test_load_missing_columns(self, tmp_path):
        csv_path = tmp_path / "missing_cols.csv"
        csv_path.write_text("state,price\n")  # Missing timestamp

        with pytest.raises(DataLoadError, match="Missing required columns"):
            DataLoader(csv_path).load()

    def test_load_invalid_price(self, tmp_path):
        csv_path = tmp_path / "bad_price.csv"
        csv_path.write_text("state,price,timestamp\nNSW,not_a_number,2025-01-01 00:00:00\n")

        with pytest.raises(DataLoadError, match="Invalid price"):
            DataLoader(csv_path).load()

    def test_load_invalid_timestamp(self, tmp_path):
        csv_path = tmp_path / "bad_timestamp.csv"
        csv_path.write_text("state,price,timestamp\nNSW,100.00,not-a-date\n")

        with pytest.raises(DataLoadError, match="Invalid timestamp"):
            DataLoader(csv_path).load()

    def test_state_normalization(self, tmp_path):
        csv_path = tmp_path / "mixed_case.csv"
        csv_path.write_text("state,price,timestamp\nvic,100.00,2025-01-01 00:00:00\n")

        loader = DataLoader(csv_path).load()

        assert loader.get_prices_for_state("VIC") is not None
        assert loader.get_prices_for_state("vic") is not None
        assert loader.get_available_states() == ["VIC"]

    def test_negative_prices_allowed(self, tmp_path):
        csv_path = tmp_path / "negative.csv"
        csv_path.write_text("state,price,timestamp\nNSW,-50.00,2025-01-01 00:00:00\n")

        loader = DataLoader(csv_path).load()
        records = loader.get_prices_for_state("NSW")

        assert records is not None
        assert records[0].price == Decimal("-50.00")

    def test_get_prices_unknown_state(self, sample_csv):
        loader = DataLoader(sample_csv).load()

        assert loader.get_prices_for_state("UNKNOWN") is None


class TestPriceRecord:
    def test_immutable(self):
        from datetime import datetime

        record = PriceRecord("NSW", Decimal("100.00"), datetime.now())

        with pytest.raises(AttributeError):
            record.price = Decimal("200.00")  # type: ignore[misc]
