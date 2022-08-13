from werkzeug.security import generate_password_hash
from flask_socketio import SocketIO
from flask_login import LoginManager
from .db_manager import DBManager
from flask import Flask
from datetime import timedelta

__DEBUG__ = False
db_man = DBManager("database.db")
db = db_man.data_base
socketio = None
app = None


def create_app():
    global app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "One Secret key to generate here"
    app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{db_man.name}'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["UPLOAD_FOLDER"] = "static/uploads"
    serv_socketio = SocketIO(app, max_http_buffer_size=(50 * 1000 * 1000))
    set_socketio(serv_socketio)

    db.init_app(app)

    from .views import views
    from .auth import auth
    from .DevicesCommunications import dev_comms
    from .ClientCommunication import client_comms

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(dev_comms, url_prefix="/")
    app.register_blueprint(client_comms, url_prefix="/")

    from .models import User, Log, Device
    with app.app_context():
        db_man.create_database(app)

    # TODO: Delete when insertion of devices
    with app.app_context():
        user = User.query.filter_by(email="admin@admin").first()

        if not user:
            dev = Device.query.filter_by(dev_name="Q101").first()
            if not dev:
                dev = Device(dev_name="Q101")
                db_man.add_device(dev)
            user = User(email="admin@admin", name="admin", password=generate_password_hash("admin", method="sha256"))
            db_man.add_user(user, device=dev)

            try:
                log_entry = Log(activity=f"Added to Device ({dev.dev_name})",
                                user_id=User.query.filter_by(email=user.email).first().id,
                                )
                db_man.add_log(log_entry)
            except Exception as e:
                print(e)

            print(f"user logs = {user.logs}")

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app, socketio


def set_socketio(socket):
    global socketio
    socketio = socket

