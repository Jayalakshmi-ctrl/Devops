from flask import Blueprint, jsonify, request
from app.services import GymService

main_bp = Blueprint('main', __name__)

@main_bp.route('/api/clients', methods=['POST'])
def save_profile():
    data = request.get_json() or {}
    profile = GymService.save_client_profile(data)
    if not profile:
        return jsonify({"status": "error", "message": "Invalid input variables"}), 400
    return jsonify({"status": "success", "profile": profile}), 201

@main_bp.route('/api/clients/<string:name>', methods=['GET'])
def load_profile(name):
    profile = GymService.load_client_profile(name)
    if not profile:
        return jsonify({"status": "error", "message": "Client profile not found"}), 404
    return jsonify({"status": "success", "client_profile": profile})

@main_bp.route('/api/clients/progress', methods=['POST'])
def save_progress():
    """Maps directly to the route your automated Pytest framework expects."""
    data = request.get_json() or {}
    name = data.get('name')
    adherence = data.get('adherence')

    if not name or adherence is None:
        return jsonify({"status": "error", "message": "Client name and adherence required"}), 400

    log = GymService.save_weekly_progress(name, adherence)
    return jsonify({"status": "success", "progress_log": log}), 201
