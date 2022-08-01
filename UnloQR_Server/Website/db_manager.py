from flask_sqlalchemy import SQLAlchemy
from os import path
import time


class DBManager:
    def __init__(self, name):
        self.data_base = SQLAlchemy()
        self.name = name

    def create_database(self, app):
        if not path.exists('Website/' + self.name):
            self.data_base.create_all(app=app)
            print("Created Database!")

    def add_user(self, new_user):
        self.data_base.session.add(new_user)
        self.data_base.session.commit()

    def add_log(self, log_entry):
        self.data_base.session.add(log_entry)
        self.data_base.session.commit()

    def update_email_confirmed_status(self, user):
        user.email_confirmed = True
        self.data_base.session.commit()
