from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user
from .client_msg_gen import send_confirmation_email
from .models import User, Device, Log
from . import db_man

views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        email = request.form.get("email")
        dev_name = request.form.get("dev_name")

        device = Device.query.filter_by(dev_name=dev_name).first()

        if device:
            new_user = User(email=email)
            db_man.add_user(new_user, device)

            log_entry = Log(activity=f"Added to Device ({dev_name})",
                            user_id=User.query.filter_by(email=email).first().id
                            )
            db_man.add_log(log_entry)

            flash("Konto wurde erfolgreich erstellt, bitte bestätigen Sie Ihre E-Mail-Adresse.", category="success")
            send_confirmation_email(email, "auth.reroute_to_confirmation")
        else:
            flash("Device ID könnte nicht in der Database gefunden werden", category="error")

        return redirect(url_for("views.home"))

    return render_template("home.html", user=current_user, db=User)



