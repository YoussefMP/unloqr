import os
import sqlite3
import click
import sqlalchemy.exc
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from os import path


class DBManager:
    def __init__(self, name):
        self.data_base = SQLAlchemy()
        self.name = name

    def create_database(self, app, force=False):
        local_path = "./Website"
        heroku_path = "./UnloQR_Server/Website/"

        # print(f"listdir of the path {heroku_path} ====> {os.listdir(heroku_path)}")

        print(not (path.exists(f'{local_path}/{self.name}') or path.exists(heroku_path + self.name)) or force)

        if not (path.exists(f'{local_path}/{self.name}') or path.exists(heroku_path + self.name)) or force:
            try:
                self.data_base.drop_all()
                self.data_base.create_all(app=app)
            except sqlite3.OperationalError as err:
                print(f"Catched {err} ===========")
        else:
            print("DATABASE ALREADY EXISTENT")

        # print(f"listdir of the path {heroku_path} ====> {os.listdir(heroku_path)}")

    def add_admin(self):
        heroku_path = "./UnloQR_Server/Website/"
        # print(f"listdir of the path {heroku_path} ====> {os.listdir(heroku_path)}")
        from .models import User
        admin = User(email="admin@admin", name="admin", password=generate_password_hash("admin", method="sha256"))
        try:
            self.data_base.session.add(admin)
            self.data_base.session.commit()
        except sqlite3.IntegrityError as err:
            print(f"Could not add admin")

    ########################
    # User table functions #
    ########################
    def add_user(self, new_user, device):
        try:
            self.data_base.session.add(new_user)
            device.allowed_users.append(new_user)
            self.data_base.session.commit()
        except sqlite3.IntegrityError or sqlalchemy.exc.IntegrityError as err:
            print(f"Error Message: {err}")

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
        try:
            self.data_base.session.delete(user.first())
            self.data_base.session.commit()
        except sqlite3.DataError or sqlalchemy.exc.IntegrityError as d_err:
            print(f"Data error while deleting: {d_err}")
    #####################################################

    #######################
    # Log table functions #
    #######################
    def add_log(self, log_entry):
        try:
            self.data_base.session.add(log_entry)
            self.data_base.session.commit()
        except sqlite3.IntegrityError or sqlalchemy.exc.IntegrityError as i_err:
            print(f"Integrity error: {i_err}")

    def update_video_path(self, entry, vid_path):
        entry.video = vid_path
        self.data_base.session.commit()
    #####################################################

    ##########################
    # Device table functions #
    ##########################
    def add_device(self, device):
        try:
            self.data_base.session.add(device)
            self.data_base.session.commit()
        except sqlite3.IntegrityError or sqlalchemy.exc.IntegrityError as i_err:
            print(f"Integrity error: {i_err}")

    def set_session_id(self, device, sid):
        print(sid)
        device.sid = sid
        self.data_base.session.commit()
        print("Should be Set")

    def add_user_to_device(self, device, user):
        device.allowed_users.append(user)
        self.data_base.session.commit()
    #####################################################