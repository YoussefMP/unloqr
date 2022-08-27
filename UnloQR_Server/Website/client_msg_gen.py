import smtplib
from flask import url_for
from datetime import datetime
from itsdangerous import URLSafeSerializer


s = URLSafeSerializer("Secret key goes here")


def gen_token(seed):
    return s.dumps(seed, salt="email-confirm")


def get_token_seed(token):
    return s.loads(token, salt="email-confirm", max_age=300)


def compose_mail(sender, receiver, token, route):
    sent_from = sender
    sent_to = [receiver]
    sent_subject = "Confirmation mail"

    link = url_for(route, token=token, _external=True)
    sent_body = f"Hello, This is your confirmation link:\n {link}"

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(sent_to), sent_subject, sent_body)

    return email_text


def send_confirmation_email(email, route):
    gmail_user = "unloqr.bot@gmail.com"
    gmail_app_password = "iwlvtidzuynpllwc"

    token = gen_token(email)

    email_text = compose_mail(gmail_user, email, token, route)

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        server.sendmail(gmail_user, email, email_text)
        server.close()

        print('Email sent!')

    except Exception as exception:
        print("Error: %s!\n\n" % exception)
