import os
from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_FILE = os.environ.get("PRICE_DATA_FILE", BASE_DIR / "data" / "coding_challenge_prices.csv")

    PRICE_DECIMAL_PLACES = 2

    VALID_STATES = frozenset({"NSW", "QLD", "SA", "TAS", "VIC"})


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    DEBUG = False
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
