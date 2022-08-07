from flask import Blueprint, render_template, request, flash, redirect, url_for, Response
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .client_msg_gen import send_confirmation_email, get_token_seed
from validate_email import validate_email
from itsdangerous import SignatureExpired
from .models import User, Log, Device
from time import sleep
from . import db_man
import numpy as np
from io import BytesIO
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
                flash("Logged in Successfully!", category="success")
                login_user(user, remember=False)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect password, try again.", category="error")
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

            log_entry = Log(video="Hello", activity="Email-confirm", user_id=User.query.filter_by(email=email).first().id)
            db_man.add_log(log_entry)

            flash("Passwort gespeichert!", category="success")

            return redirect(url_for("auth.login"))
        else:
            flash("Passwörter stimmen nicht überein", category="error")

    return render_template("set_password.html")


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("firstName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user = User.query.filter_by(email=email).first()

        if user:
            flash("Die email-adresse ist schon verwendet", category="error")
        elif len(email) < 6:
            flash("Email muss mehr als 6 Buchstaben enthalten", category="error")
        elif len(name) < 2:
            flash("Vorname muss mehr als 2 Buchstaben enthalten", category="error")
        elif password2 != password1:
            print(password1, password2)
            print(password1 == password2)
            flash("Passwörter stimmen nicht überein", category="error")
        elif len(password1) < 7:
            flash("Passwort ist zu kurz", category="error")
        else:
            new_user = User(email=email, name=name,
                            password=generate_password_hash(password1, method="sha256"))

            db_man.add_user(new_user)

            # TODO: Remove this default entry
            # device = Device(dev_name="A101")
            # db_man.add_allowed_device(device)

            log_entry = Log(video="Hello", activity="Sign-Up", user_id=new_user.id)
            db_man.add_log(log_entry)

            flash("Konto wurde erfolgreich erstellt, bitte bestätigen Sie Ihre E-Mail-Adresse.", category="success")

            send_confirmation_email(email, "auth.reroute_to_confirmation")

            return redirect(url_for("views.home"))

    return render_template("sign_up.html", user=current_user)


@auth.route("/logs/<uid>")
@login_required
def logs_view(uid):
    user = User.query.filter_by(id=uid).first()
    return render_template("Logs.html", user=user)


# background process happening without any refreshing
@auth.route("/del_user/<uid>")
@login_required
def delete_user_with_id(uid):
    db_man.delete_user_by_id(User.query.filter_by(id=uid))
    flash("Logged in Successfully!", category="success")
    return redirect(url_for("views.home"))


@auth.route("/add_user", methods=["GET", "POST"])
@login_required
def add_user_view():

    if request.method == "POST":
        email = request.form.get("email")
        isvalid = validate_email(email)

        if isvalid:
            flash("User added to database!", category="success")

            user = User.query.filter_by(email=email).first()
            if user:
                flash("Die email-adresse ist schon verwendet", category="error")
            else:
                new_user = User(email=email)

                db_man.add_user(new_user)

                log_entry = Log(video="Hello", activity="User Added", user_id=new_user.id)
                db_man.add_log(log_entry)

                flash(f"Confirmation email sent to {email}.", category="success")

                send_confirmation_email(email, "auth.reroute_to_confirmation")

                return redirect(url_for("views.home"))
        else:
            flash("Invalid email", category="error")

    return render_template("VideoViewer.html", user=current_user)


# _________________ Video Handling _________________
def generate_frames(path):
    cap = cv2.VideoCapture(path)

    while cap.isOpened():
        success, frame = cap.read()
        if success:
            ret, frame = cv2.imencode(".jpg", frame)
            frame = frame.tobytes()

            yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
            sleep(0.01)

    cap.release()
    cv2.destroyAllWindows()


@auth.route("/Vid_log/<vid_path>", methods=["GET"])
def open_vid_modal(vid_path):
    from . import app
    with app.app_context():
        vid_path = Log.query.filter_by(id=vid_path).first().video

    print(vid_path)
    return Response(generate_frames(vid_path), mimetype='multipart/x-mixed-replace; boundary=frame')


