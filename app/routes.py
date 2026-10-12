from flask import Blueprint, jsonify, request, Response
from app.services import GymService

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    return jsonify({"status": "success", "message": "ACEest System Environment v3 Live"})

@main_bp.route('/api/programs/<string:name>', methods=['GET'])
def get_program(name):
    weight = request.args.get('weight', type=float, default=0.0)
    data = GymService.get_program_details(name)
    if not data:
        return jsonify({"status": "error", "message": "Program not found"}), 404
        
    res = {"program": name, "workout": data["workout"], "diet": data["diet"]}
    if weight > 0:
        res["estimated_calories"] = GymService.calculate_calories(name, weight)
    return jsonify(res)

@main_bp.route('/api/clients', methods=['POST', 'GET'])
def manage_clients():
    """Handles POST payloads to save client data records and GET lookups to list registry pools."""
    if request.method == 'POST':
        data = request.get_json() or {}
        profile = GymService.save_client(
            data.get('name'), data.get('age'), data.get('weight'),
            data.get('program'), data.get('adherence'), data.get('notes')
        )
        if not profile:
            return jsonify({"status": "error", "message": "Invalid registration input variables"}), 400
        return jsonify({"status": "success", "client": profile}), 201
        
    # GET Logic: List current registry pool metrics
    return jsonify({"clients": GymService.get_all_clients()})

@main_bp.route('/api/clients/chart', methods=['GET'])
def get_chart():
    """Returns analytics data along with a Base64 graphical image string representation."""
    chart_b64 = GymService.generate_progress_chart()
    if not chart_b64:
        return jsonify({"status": "error", "message": "No active client metrics to chart"}), 404
    return jsonify({"chart_base64": chart_b64})

@main_bp.route('/api/clients/export', methods=['GET'])
def export_clients():
    """Streams a dynamically generated CSV spreadsheet attachment back to the user."""
    csv_data = GymService.generate_csv_data()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=clients_export.csv"}
    )
