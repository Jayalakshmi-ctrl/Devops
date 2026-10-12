from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Initialize database tables on startup
    from app.services import GymService
    GymService.init_db()
    
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app
