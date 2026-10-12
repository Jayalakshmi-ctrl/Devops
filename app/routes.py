from flask import Blueprint, jsonify, request
from app.services import GymService

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    return jsonify({"status": "success", "message": "ACEest Progressive Tracking Engine Live"})

@main_bp.route('/api/clients', methods=['POST'])
def save_client():
    data = request.get_json() or {}
    name = data.get('name')
    program = data.get('program')
    if not name or not program:
        return jsonify({"status": "error", "message": "Name and Program parameters required"}), 400
    profile = GymService.save_client_profile(name, data.get('age'), data.get('weight'), program)
    return jsonify({"status": "success", "profile": profile}), 201

@main_bp.route('/api/clients/<string:name>', methods=['GET'])
def load_client(name):
    profile = GymService.load_client_profile(name)
    if not profile:
        return jsonify({"status": "error", "message": "Client profile not found"}), 404
    return jsonify({"status": "success", "client_profile": profile})

@main_bp.route('/api/clients/progress', methods=['POST'])
def save_progress():
    data = request.get_json() or {}
    name = data.get('name')
    adherence = data.get('adherence')
    if not name or adherence is None:
        return jsonify({"status": "error", "message": "Client name and adherence metrics are required"}), 400
    log = GymService.save_weekly_progress(name, adherence)
    return jsonify({"status": "success", "progress_log": log}), 201

@main_bp.route('/api/clients/<string:name>/chart', methods=['GET'])
def get_client_chart(name):
    """Returns the custom timeline chart for the requested client as a Base64 string."""
    chart_data = GymService.generate_progress_chart(name)
    if not chart_data:
        return jsonify({"status": "error", "message": "No historical progress data recorded for this client"}), 404
    return jsonify({"client": name, "chart_base64": chart_data})
