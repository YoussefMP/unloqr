from werkzeug.security import check_password_hash
from flask import Blueprint, request
from .models import Device, User, Log
from . import db_man, socketio, app
from .dev_msg_gen import *
from pathlib import Path
import os.path
import random
import base64

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
    print("Connected")


@socketio.on("man_open_request")
def handle_manual_access_request(data):

    password = data["password"]
    sid = request.sid

    admin = User.query.filter_by(id=1).first()
    print(f"Admin {admin} wants in")
    if check_password_hash(admin.password, password):
        print("OK")
        response = {"ID": 140, "text": "Access granted", "uid": -1, "did": "did", "date": "date"}
        socketio.emit("access_granted", response, room=sid)
    else:
        print("NOT OK")


@socketio.on('get_ID')
def handle_id_request(data):
    """
    Handles new incoming devices messages into the server
    :param data: Data sent with the message
    """
    device = Device.query.filter_by(dev_name=data['id']).first()
    if not device:
        if data['id'] != "XXXX":
            new_id = data['id']
        else:
            print("Welcoming new comer... ")
            devices_list = db_man.data_base.session.query(Device.dev_name).all()
            new_id = generate_dev_name(devices_list)

        new_dev = Device(dev_name=new_id)
        db_man.set_session_id(new_dev, request.sid)
        db_man.add_device(new_dev)

        response = compose_new_id_msg(new_id)
        socketio.emit("set_ID", response, room=request.sid)

    else:
        db_man.set_session_id(device, request.sid)
        response = compose_hello_msg()
        socketio.emit("hello", response, room=request.sid)


@socketio.on("file_upload")
def handle_file_upload(data):
    import re
    from . import __DEBUG__

    dev_name_regex = re.compile(r"""(?P<uid>.*?)_(?P<dev>....)_(?P<date>.*?)\.(?:avi|mp4)""")
    dev_name = dev_name_regex.match(data["filename"]).group("dev")
    uid = int(dev_name_regex.match(data["filename"]).group("uid"))
    date = dev_name_regex.match(data["filename"]).group("date")

    print(f"File name === >{data['filename']}")

    if __DEBUG__:
        path = "./Website/static/uploads/amv.mp4"
    else:
        path = str(Path(os.path.abspath(__file__)).parent) + "/static/uploads/" + data["filename"]
        print(path)
        print(f" Listing Path(os.path.abspath(__file__)).parent => {os.listdir(Path(os.path.abspath(__file__)).parent)}")
        print(f"Video path give = {path}")

        # for testing
        # path = f"./Website/static/uploads/{data['filename']}"
        # filename = f"static/uploads/{data['filename']}"

    print(os.listdir("./UnloQR_Server/Website/static/uploads"))
    file = open(path, "wb")
    file.write(base64.decodebytes(data["file"]))
    file.close()
    print("Should be done with file writing")

    user = User.query.filter_by(id=uid).first()
    log_entry = Log(activity=f"Benutzer {user.name} hat Zugang zu {dev_name}"
                             f"angefordert => (Gewaehrt)",
                    user_id=uid,
                    video=path)
    db_man.add_log(log_entry)

    print("File Got")


@socketio.on("exit")
def handle_disconnect(data):
    print(f"Device with ID {data['id']} was disconnected")

    did = data["id"]
    device = Device.query.filter_by(dev_name=did).first()
    if device:
        db_man.set_session_id(device, "Null")
    else:
        print("device already deleted from the database")
    print("session Id was nullified")


@socketio.on("received")
def client_ack():
    print(f" ________________ Received ACK from device _______________________ ")
    from . import ack
    ack = True



