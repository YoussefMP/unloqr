from flask_login import LoginManager
from .db_manager import DBManager
from flask import Flask

db_man = DBManager("database.db")
db = db_man.data_base


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "One Secret key to generate here"
    app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{db_man.name}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User, Log
    db_man.create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

