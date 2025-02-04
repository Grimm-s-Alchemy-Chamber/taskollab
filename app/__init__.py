from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_migrate import Migrate, migrate
from app.db import db

from app.routes.board_routes import boards_bp

socketio = SocketIO(cors_allowed_origins="*")
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)
    CORS(app)
    with app.app_context():
        db.create_all()  # Automatically create tables (optional for prod)

    # Register routes
    from app.routes.auth_routes import auth_bp
    from app.routes.task_routes import task_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(boards_bp, url_prefix='/api')
    app.register_blueprint(task_bp, url_prefix='/api')

    return app