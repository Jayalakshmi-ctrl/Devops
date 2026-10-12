from flask import Blueprint, jsonify, request
from app.services import GymService

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    return jsonify({"status": "success", "message": "ACEest Dynamic Database API Engine Operational"})

@main_bp.route('/api/clients', methods=['POST'])
def save_profile():
    """Saves or updates core client profile variables."""
    data = request.get_json() or {}
    profile = GymService.save_client_profile(data)
    if not profile:
        return jsonify({"status": "error", "message": "Invalid input variables or missing fields"}), 400
    return jsonify({"status": "success", "profile": profile}), 201

@main_bp.route('/api/clients/<string:name>', methods=['GET'])
def load_profile(name):
    """Loads matching master client configuration sets."""
    profile = GymService.load_client_profile(name)
    if not profile:
        return jsonify({"status": "error", "message": "Client profile record not found"}), 404
    return jsonify({"status": "success", "client_profile": profile})

@main_bp.route('/api/clients/progress', methods=['POST'])
def save_progress():
    """Applies incoming client adherence metrics directly to persistence models."""
    data = request.get_json() or {}
    name = data.get('name')
    adherence = data.get('adherence')

    if not name or adherence is None:
        return jsonify({"status": "error", "message": "Client name and adherence metrics are required"}), 400

    log = GymService.save_weekly_progress(name, adherence)
    return jsonify({"status": "success", "progress_log": log}), 201

@main_bp.route('/api/clients/<string:name>/bmi', methods=['GET'])
def get_bmi(name):
    """Evaluates dynamic clinical tracking parameters to diagnose metric risks."""
    bmi_data = GymService.calculate_bmi_metrics(name)
    if not bmi_data:
        return jsonify({"status": "error", "message": "Insufficient biometric data indices recorded"}), 400
    return jsonify({"status": "success", "analytics": bmi_data})

@main_bp.route('/api/clients/<string:name>/workouts', methods=['POST'])
def log_workout(name):
    """Handles deep relational session logs for a specific tracking user profile."""
    data = request.get_json() or {}
    w_data = data.get('workout', {})
    e_data = data.get('exercise', {})
    
    if not w_data.get('date') or not w_data.get('type'):
        return jsonify({"status": "error", "message": "Missing required workout definitions"}), 400
        
    w_id = GymService.log_workout_session(name, w_data, e_data)
    return jsonify({"status": "success", "workout_id": w_id}), 201
