import os

import dotenv
import firebase_admin
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

dotenv.load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
firebase_app = firebase_admin.initialize_app()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="dev", SQLALCHEMY_DATABASE_URI="sqlite:////tmp/test.db")

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    db.init_app(app)
    login_manager.init_app(app)

    from api import api

    app.register_blueprint(api)

    return app
