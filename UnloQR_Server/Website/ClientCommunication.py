from werkzeug.security import check_password_hash
from .client_msg_gen import send_confirmation_email
from flask import Blueprint, request
from .models import User, Log
from . import messages as msg

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

    return response


@client_comms.route("/frgtpswrd", methods=["GET", "POST"])
def forgot_pw_req(user):
    send_confirmation_email(user.email, "auth.reroute_to_confirmation")
    response = msg.PW_RESET_REQUEST_ACCEPTED
    return response


@client_comms.route("/access_request", methods=["POST"])
def access_req():
    data = request.get_json()

    email = data["email"]
    password = data["password"]
    dev_name = data["dev_name"]

    user = User.query.filer_by(email=email).first()
    if user:
        if check_password_hash(user.password, password):
            if dev_name in user.allowed_devices:
                # TODO: Start thread for unlocking and recording
                response = msg.LOGIN_GRANTED
            else:
                response = msg.DENIED_ON_DEVICE
        else:
            response = msg.LOGIN_DENIED
    else:
        response = msg.USER_DOESNT_EXIST

    return response
