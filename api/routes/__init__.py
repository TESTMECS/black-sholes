from api.routes.auth import auth_bp
from api.routes.calculations import calc_bp
from api.routes.heatmaps import heatmap_bp

def register_blueprints(app):
    """Register all API route blueprints with the Flask app"""
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(calc_bp, url_prefix='/api/calculations')
    app.register_blueprint(heatmap_bp, url_prefix='/api')
