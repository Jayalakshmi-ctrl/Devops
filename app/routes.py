from flask import Blueprint, jsonify, request
from app.services import GymService

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    return jsonify({"status": "success", "message": "ACEest Dynamic Database API Engine Operational"})

@main_bp.route('/api/clients', methods=['POST'])
def save_profile():
    """Saves or updates full profile configuration parameters."""
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

@main_bp.route('/api/clients/<string:name>/summary', methods=['GET'])
def get_summary(name):
    """Retrieves composite records including adherence milestones and latest stats."""
    summary = GymService.get_client_summary(name)
    if not summary:
        return jsonify({"status": "error", "message": "Client summary record not found"}), 404
    return jsonify({"status": "success", "summary": summary})

@main_bp.route('/api/clients/<string:name>/bmi', methods=['GET'])
def get_bmi(name):
    """Evaluates dynamic clinical tracking parameters to diagnose metric risks."""
    bmi_data = GymService.calculate_bmi_info(name)
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

@main_bp.route('/api/clients/<string:name>/metrics', methods=['POST'])
def log_metrics(name):
    """Logs raw data tracking elements like body fat and waistlines into rows."""
    data = request.get_json() or {}
    if not data.get('date') or not data.get('weight'):
        return jsonify({"status": "error", "message": "Date and weight attributes required"}), 400
    GymService.log_body_metrics(name, data)
    return jsonify({"status": "success", "message": "Biometric variables logged successfully"}), 201

@main_bp.route('/api/clients/<string:name>/charts/<string:chart_type>', methods=['GET'])
def get_analytics_chart(name, chart_type):
    """Streams transient Base64 telemetry images matching requested parameters (adherence or weight)."""
    if chart_type not in ["adherence", "weight"]:
        return jsonify({"status": "error", "message": "Invalid analytical graph request parameter"}), 400
        
    table_target = "progress" if chart_type == "adherence" else "metrics"
    chart_str = GymService.generate_trend_chart(name, table_target)
    
    if not chart_str:
        return jsonify({"status": "error", "message": f"Insufficient records to map {chart_type} trends"}), 444
    return jsonify({"status": "success", "chart_base64": chart_str})
