from flask import Blueprint, jsonify, request
from app.services import GymService

main_bp = Blueprint('main', __name__)

@main_bp.route('/api/clients', methods=['POST'])
def save_profile():
    data = request.get_json() or {}
    profile = GymService.save_client_profile(data)
    if not profile:
        return jsonify({"status": "error", "message": "Invalid input metadata blocks"}), 400
    return jsonify({"status": "success", "profile": profile}), 201

@main_bp.route('/api/clients/<string:name>/summary', methods=['GET'])
def get_summary(name):
    summary = GymService.get_client_summary(name)
    if not summary:
        return jsonify({"status": "error", "message": "Client record not found"}), 404
    return jsonify({"status": "success", "summary": summary})

@main_bp.route('/api/clients/<string:name>/bmi', methods=['GET'])
def get_bmi(name):
    bmi_data = GymService.calculate_bmi_metrics(name)
    if not bmi_data:
        return jsonify({"status": "error", "message": "Insufficient biometric indices"}), 400
    return jsonify({"status": "success", "analytics": bmi_data})

@main_bp.route('/api/clients/<string:name>/workouts', methods=['POST'])
def log_workout(name):
    data = request.get_json() or {}
    w_data = data.get('workout', {})
    e_data = data.get('exercise', {})
    
    if not w_data.get('date') or not w_data.get('type'):
        return jsonify({"status": "error", "message": "Missing structural session definitions"}), 400
        
    w_id = GymService.log_workout_session(name, w_data, e_data)
    return jsonify({"status": "success", "workout_id": w_id}), 201

@main_bp.route('/api/clients/<string:name>/charts/weight', methods=['GET'])
def get_weight_chart(name):
    chart_b64 = GymService.generate_weight_trend_chart(name)
    if not chart_b64:
        return jsonify({"status": "error", "message": "No historical metrics available to render"}), 404
    return jsonify({"status": "success", "weight_trend_base64": chart_b64})
