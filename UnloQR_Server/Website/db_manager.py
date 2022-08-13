import os

from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from os import path


class DBManager:
    def __init__(self, name):
        self.data_base = SQLAlchemy()
        self.name = name

    def create_database(self, app):

        try:
            print(f" Listing '/' content {os.listdir('/')}")
        except:
            pass

        try:
            print(f"Listing 'Website' content {os.listdir('Website')}")
        except:
            pass

        try:
            print(f"Does database exist ? => {path.exists('.Website/' + self.name)}")
        except:
            pass

        try:
            print(f"Does database exist ? => {path.exists('.Website/' + self.name)}")
        except:
            print()

        if not path.exists('.Website/' + self.name):
            self.data_base.drop_all()
            self.data_base.create_all(app=app)
            print("Created Database!")
            # TODO add admin account

    ########################
    # User table functions #
    ########################
    def add_user(self, new_user, device):
        self.data_base.session.add(new_user)
        device.allowed_users.append(new_user)
        self.data_base.session.commit()

    def set_name(self, user, name):
        user.name = name
        self.data_base.session.commit()

    def set_password(self, user, password):
        user.password = generate_password_hash(password, method="sha256")
        self.data_base.session.commit()

    def update_email_confirmed_status(self, user):
        user.email_confirmed = True
        self.data_base.session.commit()

    def delete_user_by_id(self, user):
        self.data_base.session.delete(user.first())
        self.data_base.session.commit()
    #####################################################

    #######################
    # Log table functions #
    #######################
    def add_log(self, log_entry):
        self.data_base.session.add(log_entry)
        self.data_base.session.commit()

    def update_video_path(self, entry, vid_path):
        entry.video = vid_path
        self.data_base.session.commit()
    #####################################################

    ##########################
    # Device table functions #
    ##########################
    def add_device(self, device):
        self.data_base.session.add(device)
        self.data_base.session.commit()
    #####################################################

