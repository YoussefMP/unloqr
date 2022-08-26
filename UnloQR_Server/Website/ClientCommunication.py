from flask_cors import cross_origin
from validate_email import validate_email
from werkzeug.security import check_password_hash
from .client_msg_gen import send_confirmation_email
from flask import Blueprint, request, jsonify
from .models import User, Log, Device
from . import messages as msg
from . import socketio, db_man
from datetime import datetime

client_comms = Blueprint("client_comms", __name__)


@client_comms.route("/login_request", methods=["POST"])
@cross_origin()
def login_request():

    data = request.get_json()
    email = data["email"]
    password = data["password"]

    print(f"login request from {email}")
    user = User.query.filter_by(email=email).first()
    print(f"db query return {user}")

    if user:
        uid = user.id
        if check_password_hash(user.password, password):
            msg.LOGIN_GRANTED.update({"UID": uid})
            msg.LOGIN_GRANTED.update({"name": user.name})
            response = msg.LOGIN_GRANTED
        else:
            response = msg.LOGIN_DENIED
    else:
        response = msg.USER_DOESNT_EXIST

    return jsonify(response)


@client_comms.route("/forgot_password", methods=["POST"])
@cross_origin()
def forgot_pw_req():

    # TODO: Logging
    response = msg.OK_MSG

    if request.method == "POST":
        data = request.get_json()
        email = data["email"]

        user = User.query.filter_by(email=email).first()
        if user and user.email_confirmed:
            send_confirmation_email(user.email, "auth.forgot_my_password")
            response = msg.PW_RESET_REQUEST_ACCEPTED
        elif not user.email_confirmed:
            response = msg.EMAIL_NOT_CONFIRMED
        else:
            response = msg.PW_RESET_REQUEST_DENIED

    return jsonify(response)


@client_comms.route("/change_password", methods=["POST"])
@cross_origin()
def change_pw_req():

    # TODO: Logging
    response = msg.OK_MSG

    if request.method == "POST":

        data = request.get_json()
        email = data["email"]
        old_password = data["old_password"]
        new_password = data["new_password"]

        user = User.query.filter_by(email=email).first()
        if user and user.email_confirmed:
            if check_password_hash(user.password, old_password):
                db_man.set_password(user, new_password)
                response = msg.PW_UPDATE_SUCCESSFUL
            else:
                response = msg.PW_OLD_PASSWORD_WRONG
        elif not user.email_confirmed:
            response = msg.EMAIL_NOT_CONFIRMED

    return jsonify(response)


# TODO: Handle access request
@client_comms.route("/access_request", methods=["POST"])
@cross_origin()
def access_req():
    # TODO: Loggin

    now = datetime.now()
    date_str = "%02d%02d%04d%02d%02d%02d" % (now.day, now.month, now.year, now.hour, now.minute, now.second)

    data = request.get_json()
    email = data["email"]
    password = data["password"]
    dev_name = data["dev_name"]

    print(email, dev_name, password)

    user = User.query.filter_by(email=email).first()
    if user:
        if check_password_hash(user.password, password):
            device = Device.query.filter_by(dev_name=dev_name).first()

            if user.id != 1:
                allowed_user = False
                for dev in user.allowed_devices:
                    if dev_name == dev.dev_name:
                        allowed_user = True
                        break
            else:
                allowed_user = True

            if allowed_user:
                sid = device.sid
                print(f"Got device {device.dev_name} with sid ={sid}")
                if sid:
                    msg.ACCESS_GRANTED.update({"uid": user.id})
                    msg.ACCESS_GRANTED.update({"did": dev_name})
                    msg.ACCESS_GRANTED.update({"date": date_str})
                    response = msg.ACCESS_GRANTED
                    print(f"Emitting access granted to Device")
                    socketio.emit("access_granted", response, room=sid)

                else:
                    response = msg.DEVICE_OFFLINE
            else:
                response = msg.DENIED_ON_DEVICE
        else:
            response = msg.LOGIN_DENIED
    else:
        response = msg.USER_DOESNT_EXIST

    print(f"Respose to access request ===> {response}")
    return jsonify(response)


@client_comms.route("/users_list", methods=["GET"])
@cross_origin()
def get_users_list():
    all_users = User.query.all()
    u_list = []

    for user in all_users:
        if user.id == 1:
            continue
        dummy_user = {"email": user.email,
                      "uid": user.id,
                      "name": user.name,
                      "email_confirmed": user.email_confirmed
                      }
        u_list.append(dummy_user)

        print(f"for user {user} with email {user.email} do search")
        user = User.query.filter_by(email=user.email).first()
        print(f"{user} was retrieved with id {user.id}")

    msg.USERS_LIST["users"] = u_list
    response = msg.USERS_LIST

    return jsonify(response)


@client_comms.route("/add_user", methods=["POST"])
@cross_origin()
def add_user():
    response = msg.OK_MSG

    data = request.get_json()

    if request.method == "POST":

        email = data["email"]
        dev_name = data["dev_name"]
        print(f"addings user request user = {email} to device = {dev_name}")

        device = Device.query.filter_by(dev_name=dev_name).first()
        user = User.query.filter_by(email=email).first()

        print("checkking email validity")
        if not validate_email(email):
            response = msg.NOT_VALID_EMAIL
            return jsonify(response)

        if device:
            if not user:
                new_user = User(email=email)
                db_man.add_user(new_user, device)
                send_confirmation_email(email, "auth.reroute_to_confirmation")
                response = msg.USER_ADDED
            else:
                db_man.add_user_to_device(device, user)

            log_entry = Log(activity=f"Added to Device ({dev_name})",
                            user_id=User.query.filter_by(email=email).first().id
                            )
            db_man.add_log(log_entry)
            response = msg.USER_ADDED_TO_DEVICE
        else:
            response = msg.DEVICE_NOT_FOUND

    return jsonify(response)


@client_comms.route("/delete_user", methods=["POST"])
@cross_origin()
def delete_user():
    try:
        data = request.get_json()

        uid = data["uid"]
        if uid != 1:
            db_man.delete_user_by_id(User.query.filter_by(id=uid))
            response = msg.USER_DELETED
        else:
            response = {"ID": 999, "text": "You sneaky bastard !!! "}

    except Exception as err:
        response = msg.SOMETHING_WENT_WRONG

    return jsonify(response)


