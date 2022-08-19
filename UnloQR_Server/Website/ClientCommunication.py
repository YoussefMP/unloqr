from flask_cors import cross_origin
from werkzeug.security import check_password_hash
from .client_msg_gen import send_confirmation_email
from flask import Blueprint, request, jsonify
from .models import User, Log, Device
from . import messages as msg
from . import socketio

client_comms = Blueprint("client_comms", __name__)


@client_comms.route("/login_request", methods=["POST"])
@cross_origin()
def login_request():

    # TODO: Logging

    data = request.get_json()
    email = data["email"]
    password = data["password"]

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
def hio():
    devices = Device.query.all()
    print(devices)
    for user in User.query.all():
        for device in devices:
            if user in [d for d in device.allowed_users]:
                print(f"{user.name}is allowed on {device.dev_name}")

    return "<h1> Devices </h1>"


# TODO: handle admin requests



