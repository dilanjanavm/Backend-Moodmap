from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta

db = SQLAlchemy()

def create_app(config_name=None):
    app = Flask(__name__)
    print('call create app')
    CORS(app)
    # app.config.from_object('instance.config.Config')
    app.config['DEBUG'] = True
    if config_name:
        app.config.from_object(f'instance.config.{config_name}')  # Dynamically load config based on config_name
    else:
        app.config.from_object('instance.config.Config')

    db.init_app(app)
    jwt = JWTManager(app)
    print(app)

    migrate = Migrate(app, db)
    # In your Flask app config
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

    @jwt.unauthorized_loader
    def custom_unauthorized_response(callback):
        return jsonify({
            "status": 401,
            "message": "Unauthorized"
        }), 401

    @jwt.invalid_token_loader
    def custom_invalid_token_response(callback):
        return jsonify({
            "status": 422,
            "message": "The token is invalid or expired"
        }), 422

    from .routes import main
    from .auth import auth_blueprint

    app.register_blueprint(main)
    app.register_blueprint(auth_blueprint)

    return app
