from flask import Blueprint, jsonify, abort
from app.services import GymService

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    """Base endpoint displaying gym summary metadata metrics."""
    return jsonify(GymService.get_welcome_message())

@main_bp.route('/api/programs', methods=['GET'])
def list_programs():
    """Lists all operational fitness keys available in the ecosystem."""
    return jsonify({"programs": GymService.get_all_programs()})

@main_bp.route('/api/programs/<string:name>', methods=['GET'])
def get_program(name):
    """Retrieves workout charts and target diet profiles for a specific track."""
    program_data = GymService.get_program_details(name)
    if not program_data:
        return jsonify({"status": "error", "message": "Fitness program profile not found"}), 404
    return jsonify({"program": name, "details": program_data})
