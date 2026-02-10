import pytest

from app import create_app
from app.data.data_loader import DataLoader
from app.services.price_service import PriceService


@pytest.fixture
def sample_csv(tmp_path):
    csv_path = tmp_path / "test_prices.csv"
    csv_path.write_text(
        "state,price,timestamp\n"
        "NSW,100.00,2025-01-01 00:00:00\n"
        "NSW,200.00,2025-01-01 00:30:00\n"
        "VIC,150.00,2025-01-01 00:00:00\n"
        "VIC,-50.00,2025-01-01 00:30:00\n"
    )
    return csv_path


@pytest.fixture
def data_loader(sample_csv):
    return DataLoader(sample_csv).load()


@pytest.fixture
def price_service(data_loader):
    return PriceService(data_loader)


@pytest.fixture
def app(sample_csv):
    app = create_app("testing")

    data_loader = DataLoader(sample_csv).load()
    price_service = PriceService(data_loader)
    app.config["PRICE_SERVICE"] = price_service

    yield app


@pytest.fixture
def client(app):
    return app.test_client()
