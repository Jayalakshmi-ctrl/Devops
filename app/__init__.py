from flask import Flask

def create_app():
    """Application factory pattern to initialize the Flask app modules."""
    app = Flask(__name__)
    # Register blueprints/routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    return app
