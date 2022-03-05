from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Log in to access this page'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    from main.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from main.orders import bp as orders_bp
    app.register_blueprint(orders_bp, url_prefix='/orders')

    from main.profiles import bp as profiles_bp
    app.register_blueprint(profiles_bp, url_prefix='/profiles')

    return app

