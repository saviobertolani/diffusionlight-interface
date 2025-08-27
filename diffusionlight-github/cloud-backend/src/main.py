import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
            """Application factory"""
            app = Flask(__name__)

    # Configuration
            app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
            app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB max file size

    # Enable CORS
            CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))

    # Initialize database FIRST
            from src.config.database import init_database
            db = init_database(app)

    # Register blueprints AFTER database initialization
            from src.routes.api import api_bp
            from src.routes.webhooks import webhooks_bp

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(webhooks_bp, url_prefix='/webhooks')

    # Error handlers
    @app.errorhandler(413)
    def file_too_large(error):
                    return jsonify({'error': 'File too large. Maximum size: 200MB'}), 413

    @app.errorhandler(404)
    def not_found(error):
                    return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
                    return jsonify({'error': 'Internal server error'}), 500

    # Health check endpoint
    @app.route('/health')
    def health():
                    return jsonify({
                                        'status': 'healthy',
                                        'service': 'diffusionlight-backend',
                                        'version': '1.0.0'
                    })

    # Root endpoint
    @app.route('/')
    def root():
                    return jsonify({
                                        'service': 'DiffusionLight API',
                                        'version': '1.0.0',
                                        'endpoints': {
                                                                'api': '/api',
                                                                'docs': '/api/docs'
                                        },
                                        'health': '/health'
                    })

    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
            port = int(os.getenv('PORT', 5000))
            debug = os.getenv('FLASK_ENV') == 'development'
            app.run(
                host='0.0.0.0',
                port=port,
                debug=debug
            )
