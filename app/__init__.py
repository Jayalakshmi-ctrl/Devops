from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Fire up DB schema layers upon server booting sequences
    from app.services import GymService
    GymService.init_db()
    
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

