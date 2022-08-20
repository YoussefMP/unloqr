from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user
from .client_msg_gen import send_confirmation_email
from .models import User, Device, Log
from . import db_man

views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    # TODO: Check if user is already allowed on device
    if request.method == "POST":
        email = request.form.get("email")
        dev_name = request.form.get("dev_name")

        device = Device.query.filter_by(dev_name=dev_name).first()
        user = User.query.filter_by(email=email).first()

        if device:
            if not user:
                new_user = User(email=email)
                db_man.add_user(new_user, device)
                send_confirmation_email(email, "auth.reroute_to_confirmation")
                flash("Konto wurde erfolgreich erstellt, bitte bestätigen Sie Ihre E-Mail-Adresse.", category="success")
            else:
                already_in = False
                for dev in user.allowed_devices:
                    if dev_name == dev.dev_name:
                        flash("Nutzer steht schon in der Liste der erlaubten Nutzern.", category="success")
                        already_in = True
                        break
                if not already_in:
                    db_man.add_user_to_device(device, user)
                    log_entry = Log(activity=f"Added to Device ({dev_name})",
                                    user_id=User.query.filter_by(email=email).first().id
                                    )
                    db_man.add_log(log_entry)
                    flash("Nutzer wurde zu der Liste der erlaubten Nutzern hinzugefügt.", category="success")
        else:
            flash("Device ID könnte nicht in der Database gefunden werden", category="error")

        return redirect(url_for("views.home"))

    return render_template("home.html", user=current_user, db=User)



