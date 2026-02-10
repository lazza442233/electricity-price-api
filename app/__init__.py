import logging
import os

from flask import Flask

from app.config import config_by_name
from app.data.data_loader import DataLoader, DataLoadError
from app.routes.prices import prices_bp
from app.services.price_service import PriceService


def create_app(config_name: str | None = None) -> Flask:
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)

    config_class = config_by_name.get(config_name)
    if config_class is None:
        raise ValueError(f"Unknown config: {config_name}")
    app.config.from_object(config_class)

    _configure_logging(app)

    if app.config.get("DATA_FILE"):
        try:
            data_loader = DataLoader(app.config["DATA_FILE"]).load()
        except DataLoadError as e:
            app.logger.error(f"Failed to load data: {e}")
            raise
    else:
        data_loader = None

    if data_loader:
        price_service = PriceService(
            data_loader, decimal_places=app.config.get("PRICE_DECIMAL_PLACES", 2)
        )
        app.config["PRICE_SERVICE"] = price_service

    app.register_blueprint(prices_bp)

    _register_error_handlers(app)

    app.logger.info(f"Application initialized with config: {config_name}")

    return app


def _configure_logging(app: Flask) -> None:
    """Configure application logging."""
    log_level = logging.DEBUG if app.debug else logging.INFO

    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def _register_error_handlers(app: Flask) -> None:
    """Register global error handlers."""

    @app.errorhandler(404)
    def not_found(error: Exception) -> tuple[dict[str, str], int]:
        return {"error": "Resource not found"}, 404

    @app.errorhandler(500)
    def internal_error(error: Exception) -> tuple[dict[str, str], int]:
        app.logger.error(f"Internal error: {error}")
        return {"error": "Internal server error"}, 500

    @app.errorhandler(Exception)
    def handle_exception(error: Exception) -> tuple[dict[str, str], int]:
        app.logger.exception(f"Unhandled exception: {error}")
        return {"error": "An unexpected error occurred"}, 500
