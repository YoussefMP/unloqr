from flask_cors import cross_origin
from validate_email import validate_email
from werkzeug.security import check_password_hash
from .client_msg_gen import send_confirmation_email
from flask import Blueprint, request, jsonify
from .models import User, Log, Device, DummyUser
from . import messages as msg
from . import socketio, db_man

client_comms = Blueprint("client_comms", __name__)


@client_comms.route("/login_request", methods=["POST"])
@cross_origin()
def login_request():

    # TODO: Logging

    data = request.get_json()
    email = data["email"]
    password = data["password"]

    is_valid = validate_email(email)

    user = User.query.filter_by(email=email).first()
    if user:
        uid = user.id
        if check_password_hash(user.password, password):
            msg.LOGIN_GRANTED.update({"UID": uid})
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
            # TODO: Change the token rerouting link to update password method
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
                # TODO: update database
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

    data = request.get_json()
    email = data["email"]
    password = data["password"]
    dev_name = data["dev_name"]

    user = User.query.filter_by(email=email).first()
    if user:
        if check_password_hash(user.password, password):

            # TODO: Check if user is allowed on device
            device = Device.query.filter_by(dev_name=dev_name).first()

            allowed_user = False
            for dev in user.allowed_devices:
                if dev_name == dev.dev_name:
                    allowed_user = True
                    break

            if allowed_user:
                sid = device.sid
                if sid:
                    response = msg.ACCESS_GRANTED
                    socketio.emit("access_granted", response, room=sid)
                else:
                    # TODO: Device is offline
                    pass

                response = msg.LOGIN_GRANTED
            else:
                response = msg.DENIED_ON_DEVICE
        else:
            response = msg.LOGIN_DENIED
    else:
        response = msg.USER_DOESNT_EXIST

    return jsonify(response)


@client_comms.route("/get_users_request", methods=["GET"])
@cross_origin()
def send_users_list():
    devices = User.query.all()

    u_list = []

    for user in devices:
        dummy_user = {"email": user.email,
                      "uid": user.id,
                      "name": user.name,
                      }
        u_list.append(dummy_user)

    response = msg.USERS_LIST.update({"users": u_list})

    return jsonify(response)


@client_comms.route("/add_user", methods=["POST"])
@cross_origin()
def add_user():
    response = msg.OK_MSG

    if request.method == "POST":
        email = request.form.get("email")
        dev_name = request.form.get("dev_name")

        device = Device.query.filter_by(dev_name=dev_name).first()
        user = User.query.filter_by(email=email).first()

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
        uid = request.form.get("uid")
        db_man.delete_user_by_id(User.query.filter_by(id=uid))
        response = msg.USER_DELETED
    except Exception as err:
        response = msg.SOMETHING_WENT_WRONG

    return jsonify(response)


