from flask import Blueprint, jsonify, request
from app.services import GymService

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "success",
        "message": "Welcome to ACEest Functional Fitness & Performance Engine"
    })

@main_bp.route('/api/programs/<string:name>', methods=['GET'])
def get_program_profile(name):
    """Fetches details for a specific fitness domain tracking path."""
    weight_param = request.args.get('weight', type=float, default=0.0)
    program_data = GymService.get_program_details(name)
    
    if not program_data:
        return jsonify({"status": "error", "message": "Program profile not found"}), 404
        
    response_data = {
        "program": name,
        "workout_chart": program_data["workout"],
        "diet_plan": program_data["diet"],
        "display_color": program_data["color"]
    }
    
    # Dynamically inject metabolic evaluations if weight is available
    if weight_param > 0:
        response_data["estimated_calories"] = GymService.calculate_estimated_calories(name, weight_param)
        
    return jsonify(response_data)

@main_bp.route('/api/clients', methods=['POST'])
def create_client():
    """Handles POST payloads to securely save incoming user states."""
    data = request.get_json() or {}
    
    name = data.get('name')
    age = data.get('age', 0)
    weight = data.get('weight', 0.0)
    program = data.get('program')
    adherence = data.get('adherence', 0)
    
    if not name or not program:
        return jsonify({"status": "error", "message": "Missing required details: name and program"}), 400
        
    saved_profile = GymService.save_client_profile(name, age, weight, program, adherence)
    if not saved_profile:
        return jsonify({"status": "error", "message": "Failed to persist validation model parameters"}), 400
        
    return jsonify({
        "status": "success",
        "message": f"Client {name} saved successfully.",
        "client_profile": saved_profile
    }), 201

