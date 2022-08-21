import os

from flask import Blueprint, render_template, request, flash, redirect, url_for, Response
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .client_msg_gen import send_confirmation_email, get_token_seed
from itsdangerous import SignatureExpired
from .models import User, Log, Device
from time import sleep
from . import db_man
import cv2

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Erfolgreich eingeloggt!", category="success")
                login_user(user, remember=False)
                return redirect(url_for("views.home"))
            else:
                flash("Falsches Passwort, versuchen Sie es erneut.", category="error")
        else:
            flash(f"Es existiert kein Konto für die email-adresse: {email}.", category="error")

    return render_template("login.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/confirm_email/<token>", methods=["GET", "POST"])
def reroute_to_confirmation(token):

    if request.method == "POST":
        name = request.form.get("name")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        try:
            email = get_token_seed(token)
        except SignatureExpired:
            return "<h1> Der Token ist abgelaufen, bitte fordern Sie eine neue Identifikationsmail an </h1> "

        user = User.query.filter_by(email=email).first()

        if password2 == password1:
            db_man.update_email_confirmed_status(user)
            db_man.set_name(user, name)
            db_man.set_password(user, password1)

            log_entry = Log(activity="Email-bestätigt", user_id=User.query.filter_by(email=email).first().id)
            db_man.add_log(log_entry)

            flash("Passwort gespeichert!", category="success")

            return redirect(url_for("auth.login"))
        else:
            flash("Passwörter stimmen nicht überein", category="error")

    return render_template("set_password.html")


@auth.route("/forgot_password/<token>", methods=["GET", "POST"])
def forgot_my_password(token):
    if request.method == "POST":

        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        try:
            email = get_token_seed(token)
        except SignatureExpired:
            return "<h1> Der Token ist abgelaufen, bitte fordern Sie eine neue Identifikationsmail an </h1> "

        user = User.query.filter_by(email=email).first()

        if password2 == password1:
            db_man.set_password(user, password1)

            log_entry = Log(activity="Recovered password", user_id=User.query.filter_by(email=email).first().id)
            db_man.add_log(log_entry)

            flash("Passwort gespeichert!", category="success")

            return "<h1> Your Password has been Updated </h1>"
        else:
            flash("Passwörter stimmen nicht überein", category="error")

    return render_template("Forgot_password.html")


@auth.route("/logs/<uid>")
@login_required
def logs_view(uid):
    user = User.query.filter_by(id=uid).first()
    return render_template("Logs.html", user=user)


@auth.route("/devices")
@login_required
def devices_view():
    return render_template("Devices.html", user=current_user, db=Device)


@auth.route("/del_device/<did>")
@login_required
def delete_device_with_id(did):
    db_man.delete_device_by_id(Device.query.filter_by(id=did))
    flash("Gerät wurde erfolgreich gelöscht", category="success")
    return redirect(url_for("auth.devices_view"))


# background process happening without any refreshing
@auth.route("/del_user/<uid>")
@login_required
def delete_user_with_id(uid):
    db_man.delete_user_by_id(User.query.filter_by(id=uid))
    flash("Benutzer wurde erfolgreich gelöscht", category="success")
    return redirect(url_for("views.home"))


# _________________ Video Handling _________________
def generate_frames(path):
    print(path)
    print(f"Video existence => {os.path.exists(path)}")
    cap = cv2.VideoCapture(path)

    while cap.isOpened():
        success, frame = cap.read()
        if success:
            ret, frame = cv2.imencode(".jpeg", frame)
            frame = frame.tobytes()

            yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
            sleep(0.02)
        else:
            break

    cap.release()
    cv2.destroyAllWindows()


vid_path = ""


@auth.route("/video/<log_id>", methods=["GET"])
def video_viewer(log_id):
    import re
    global vid_path

    dev_name_regex = re.compile(r"""(?P<uid>.*?)_(?P<dev>....)_(?P<date>.*?)\.(?:avi|mp4)""")

    log_entry = Log.query.filter_by(id=log_id).first()
    vid_path = log_entry.video

    dev_name = dev_name_regex.match(vid_path).group("dev")
    date = dev_name_regex.match(vid_path).group("date")
    date = f"{date[:2]}-{date[2:4]}-{date[4:8]}.{date[8:10]}:{date[10:12]}:{date[12:14]}"

    request_sender = User.query.filter_by(id=log_entry.user_id).first()

    return render_template("VideoViewer.html", user=current_user, vid_path=vid_path,
                           request_sender=request_sender, dev_id=dev_name, date=date)


@auth.route("/Vid_log")
def open_vid_modal():

    global vid_path
    from pathlib import Path

    # vid_path = str(Path(os.path.abspath(__file__)).parent) + vid_path[1:].replace("/", "\\")
    print("IN OPENM MODALS")
    print(vid_path)

    return Response(generate_frames(vid_path), mimetype='multipart/x-mixed-replace; boundary=frame')


