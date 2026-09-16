"""
NearShop — Main Flask Application
AI-powered hyperlocal shop inventory discovery system for Ballari, Karnataka.
"""
import os
from flask import Flask, render_template
from config import Config
from database.db import init_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY

    # Ensure upload directory exists
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    # Initialize DB
    with app.app_context():
        init_db()

    # Register blueprints
    from routes.auth import auth_bp
    from routes.product import product_bp
    from routes.search import search_bp
    from routes.dashboard import dashboard_bp, main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(dashboard_bp)

    # ── Jinja2 Globals ──────────────────────────────────────────────────
    from flask import session

    @app.context_processor
    def inject_globals():
        return {
            'app_name': Config.APP_NAME,
            'app_tagline': Config.APP_TAGLINE,
            'city': Config.CITY,
            'state': Config.STATE,
            'current_user': {
                'id':    session.get('user_id'),
                'name':  session.get('name'),
                'email': session.get('email'),
                'role':  session.get('role'),
            } if 'user_id' in session else None,
        }

    # ── Error Handlers ──────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    return app


app = create_app()

if __name__ == '__main__':
    print('=' * 60)
    print('  NearShop — AI Hyperlocal Inventory Discovery')
    print('  Running at http://localhost:5000')
    print('  City: Ballari, Karnataka, India')
    print('=' * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
