from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .client_comms import send_confirmation_email, get_token_seed
from itsdangerous import SignatureExpired
from .models import User, Log
from . import db_man
import datetime

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                # TODO: Open Lock and Camera
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


@auth.route("/confirm_email/<token>")
def reroute_to_confirmation(token):
    try:
        email = get_token_seed(token)
    except SignatureExpired:
        return "<h1> Der Token ist abgelaufen, bitte fordern Sie eine neue Identifikationsmail an </h1> "
        pass

    db_man.update_email_confirmed_status(User.query.filter_by(email=email).first())

    log_entry = Log(video="Hello", activity="Email-confirm", user_id=User.query.filter_by(email=email).first().id)
    db_man.add_log(log_entry)


    # TODO: Reroute after some time

    return "<h1> Confirmed </h1>"


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("firstName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Die email-adresse ist schon verwendet", category="error")
        elif len(email) < 6:
            flash("Email muss mehr als 6 Buchstaben enthalten", category="error")
        elif len(first_name) < 2:
            flash("Vorname muss mehr als 2 Buchstaben enthalten", category="error")
        elif password2 != password1:
            print(password1, password2)
            print(password1 == password2)
            flash("Passwörter stimmen nicht überein", category="error")
        elif len(password1) < 7:
            flash("Passwort ist zu kurz", category="error")
        else:
            new_user = User(email=email, first_name=first_name,
                            password=generate_password_hash(password1, method="sha256"))

            db_man.add_user(new_user)

            log_entry = Log(video="Hello", activity="Sign-Up", user_id=new_user.id)
            db_man.add_log(log_entry)

            flash("Konto wurde erfolgreich erstellt, bitte bestätigen Sie Ihre E-Mail-Adresse.", category="success")

            send_confirmation_email(email)

            return redirect(url_for("views.home"))

    return render_template("sign_up.html", user=current_user)


@auth.route("/logs/<uid>")
@login_required
def logs_view(uid):
    user = User.query.filter_by(id=uid).first()


    return render_template("Logs.html", user=user)
