from werkzeug.security import check_password_hash
from .client_msg_gen import send_confirmation_email
from flask import Blueprint, request, jsonify
from .models import User, Log, Device
from . import messages as msg
from . import socketio
from .client_msg_gen import compile_grant_access_msg


client_comms = Blueprint("client_comms", __name__)


@client_comms.route("/lgn_req", methods=["POST"])
def login_request():

    data = request.get_json()
    email = data["email"]
    password = data["password"]

    user = User.query.filer_by(email=email).first()
    if user:
        if check_password_hash(user.password, password):
            response = msg.LOGIN_GRANTED
        else:
            response = msg.LOGIN_DENIED
    else:
        response = msg.USER_DOESNT_EXIST

    return jsonify(response)


@client_comms.route("/frgtpswrd", methods=["GET", "POST"])
def forgot_pw_req(user):
    send_confirmation_email(user.email, "auth.reroute_to_confirmation")
    response = msg.PW_RESET_REQUEST_ACCEPTED
    return jsonify(response)


# TODO: Handle access request
@client_comms.route("/access_request", methods=["POST"])
def access_req():
    print(request)
    try:
        data = request.get_json()
        email = data["email"]
        password = data["password"]
        dev_name = data["dev_name"]
    except:
        email = "Zshooterboy@gmail.com"
        password = "1234567"
        dev_name = "Z658"

    user = User.query.filter_by(email=email).first()
    if user:
        if check_password_hash(user.password, password):

            # TODO: Check if user is allowed on device
            device = Device.query.filter_by(dev_name=dev_name).first()


            if user.allowed_devices[0].dev_name == device.dev_name:
                sid = device.sid
                if sid:
                    response = compile_grant_access_msg(user.id, dev_name)
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


# TODO: Switch communication to socket io as opposed to POST requests (Optional)

# TODO: handle admin requests



