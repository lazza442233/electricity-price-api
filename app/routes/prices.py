from flask import Blueprint, jsonify, request, current_app
from http import HTTPStatus
import logging

from app.services.price_service import PriceService, StateNotFoundError

logger = logging.getLogger(__name__)

prices_bp = Blueprint('prices', __name__, url_prefix='/api/v1')


def get_price_service() -> PriceService:
    return current_app.config['PRICE_SERVICE']


@prices_bp.route('/prices/mean', methods=['GET'])
def get_mean_price():
    state = request.args.get('state')

    if state is None:
        return jsonify({
            'error': 'Missing required parameter: state',
            'hint': 'Provide state as query parameter, e.g., ?state=NSW'
        }), HTTPStatus.BAD_REQUEST

    state = state.strip()
    if not state:
        return jsonify({
            'error': 'State parameter cannot be empty',
            'hint': 'Valid states: NSW, QLD, SA, TAS, VIC'
        }), HTTPStatus.BAD_REQUEST

    if not state.isalpha() or len(state) > 10:
        return jsonify({
            'error': f"Invalid state format: '{state}'",
            'hint': 'State should be a short alphabetic code like NSW or VIC'
        }), HTTPStatus.BAD_REQUEST

    try:
        service = get_price_service()
        stats = service.get_mean_price(state)

        return jsonify({
            'state': stats.state,
            'mean_price': float(stats.mean),
            'record_count': stats.count
        }), HTTPStatus.OK

    except StateNotFoundError as e:
        logger.info(f"State not found: {state}")
        return jsonify({
            'error': str(e)
        }), HTTPStatus.NOT_FOUND


@prices_bp.route('/states', methods=['GET'])
def list_states():
    service = get_price_service()
    states = service.get_available_states()

    return jsonify({
        'states': states
    }), HTTPStatus.OK


@prices_bp.route('/health', methods=['GET'])
def health_check():
    service = get_price_service()
    return jsonify({
        'status': 'healthy',
        'record_count': service._data_loader.record_count
    }), HTTPStatus.OK
