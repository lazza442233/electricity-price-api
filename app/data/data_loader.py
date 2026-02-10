from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class PriceRecord:
    state: str
    price: Decimal
    timestamp: datetime


class DataLoadError(Exception):
    pass


class DataLoader:
    EXPECTED_COLUMNS = {"state", "price", "timestamp"}
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, file_path: Path):
        self._file_path = Path(file_path)
        self._records: list[PriceRecord] = []
        self._records_by_state: dict[str, list[PriceRecord]] = {}

    def load(self) -> DataLoader:
        if not self._file_path.exists():
            raise DataLoadError(f"Data file not found: {self._file_path}")

        try:
            with open(self._file_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                if reader.fieldnames is None:
                    raise DataLoadError("CSV file is empty")

                actual_columns = set(reader.fieldnames)
                if not self.EXPECTED_COLUMNS.issubset(actual_columns):
                    missing = self.EXPECTED_COLUMNS - actual_columns
                    raise DataLoadError(f"Missing required columns: {missing}")

                for line_num, row in enumerate(reader, start=2):
                    record = self._parse_row(row, line_num)
                    self._records.append(record)

                    state = record.state
                    if state not in self._records_by_state:
                        self._records_by_state[state] = []
                    self._records_by_state[state].append(record)

        except csv.Error as e:
            raise DataLoadError(f"CSV parsing error: {e}")
        except OSError as e:
            raise DataLoadError(f"Failed to read file: {e}")

        if not self._records:
            raise DataLoadError("CSV file contains no data rows")

        logger.info(f"Loaded {len(self._records)} records for {len(self._records_by_state)} states")
        return self

    def _parse_row(self, row: dict, line_num: int) -> PriceRecord:
        try:
            state = row["state"].strip().upper()
            if not state:
                raise DataLoadError(f"Line {line_num}: Empty state value")

            try:
                price = Decimal(row["price"].strip())
            except InvalidOperation:
                raise DataLoadError(f"Line {line_num}: Invalid price value '{row['price']}'")

            try:
                timestamp = datetime.strptime(row["timestamp"].strip(), self.TIMESTAMP_FORMAT)
            except ValueError:
                raise DataLoadError(f"Line {line_num}: Invalid timestamp '{row['timestamp']}'")

            return PriceRecord(state=state, price=price, timestamp=timestamp)

        except KeyError as e:
            raise DataLoadError(f"Line {line_num}: Missing column {e}")

    def get_prices_for_state(self, state: str) -> list[PriceRecord] | None:
        return self._records_by_state.get(state.upper())

    def get_available_states(self) -> list[str]:
        return sorted(self._records_by_state.keys())

    @property
    def record_count(self) -> int:
        return len(self._records)
