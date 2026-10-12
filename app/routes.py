from flask import Blueprint, jsonify, request
from app.services import GymService

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    return jsonify({"status": "success", "message": "ACEest DB-Backed API Engine Live"})

@main_bp.route('/api/clients', methods=['POST'])
def save_client():
    """Maps to save_client logic to create or update core metric sets."""
    data = request.get_json() or {}
    name = data.get('name')
    program = data.get('program')

    if not name or not program:
        return jsonify({"status": "error", "message": "Name and Program parameter fields required"}), 400

    profile = GymService.save_client_profile(name, data.get('age'), data.get('weight'), program)
    return jsonify({"status": "success", "profile": profile}), 201

@main_bp.route('/api/clients/<string:name>', methods=['GET'])
def load_client(name):
    """Maps to load_client logic to query historical entity fields."""
    profile = GymService.load_client_profile(name)
    if not profile:
        return jsonify({"status": "error", "message": "Requested client entity profile not found"}), 404
    return jsonify({"status": "success", "client_profile": profile})

@main_bp.route('/api/clients/progress', methods=['POST'])
def save_progress():
    """Maps to save_progress logic to record adherence benchmarks against schedules."""
    data = request.get_json() or {}
    name = data.get('name')
    adherence = data.get('adherence')

    if not name or adherence is None:
        return jsonify({"status": "error", "message": "Client name and adherence metrics are required"}), 400

    log = GymService.save_weekly_progress(name, adherence)
    return jsonify({"status": "success", "progress_log": log}), 201
