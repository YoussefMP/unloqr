import base64
from pathlib import Path
from flask import Blueprint, request
from .models import Device, User, Log
from . import db_man, socketio, app
import random
import os.path

dev_comms = Blueprint("dev_com", __name__)


def generate_dev_name(names):
    """
    Method that generates an ID for Raspberry devices that connect to server
    :param names: List of existing IDs in the database
    :return: new_id (1 Letter and 3 Numbers)
    """
    new_id = ""

    while new_id == "" or new_id in names:
        id_char = chr(random.randint(ord('A'), ord('Z')))
        id_nb = ''.join(str(random.randint(0, 9)) for i in range(3))
        new_id = id_char + id_nb

    return new_id


@socketio.on("connect")
def handle_connect():
    pass


@socketio.on('get_ID')
def message_handler(data):
    """
    Handles new incoming devices messages into the server
    :param data: Data sent with the message
    """
    print("Wait a sec, I am ", end="")
    if data["id"] == "XXXX":
        print("Welcoming new comer... ")
        devices_list = db_man.data_base.session.query(Device.dev_name).all()
        new_id = generate_dev_name(devices_list)

        # TODO: Uncomment when testing with Raspberry pi
        # new_dev = Device(dev_id=new_dev_name)
        # db_man.add_device(new_dev)

        return new_id

    else:
        print(f"Welcome back {data['id']}")
        # TODO: update session Id for device
        return "XXXX"


@socketio.on("file_upload")
def handle_file_upload(data):

    from . import __DEBUG__
    print("Handling File")

    if __DEBUG__:
        path = "./Website/static/uploads/amv.mp4"
    else:
        path = str(Path(os.path.abspath(__file__)).parent) + "\\static\\uploads\\" + data["filename"]

    file = open(path, "wb")
    file.write(base64.decodebytes(data["file"]))
    file.close()

    with app.app_context():
        user = User.query.filter_by(id=1).first()
        log_entry = Log(activity=f"Added to Device (Video Entry Test)",
                        user_id=User.query.filter_by(email=user.email).first().id,
                        video=path
                        )
        db_man.add_log(log_entry)

    print("File Got")


