import sqlite3

import click
from flask.cli import with_appcontext

from . import db, db_man
from .models import Log, Device, User, user_device


@click.command(name="create_tables")
@with_appcontext
def create_all():
    db.create_all()


@click.command(name="add_admin")
@with_appcontext
def add_admin():
    admin = User(email="admin@admin", name="admin", password=generate_password_hash("admin", method="sha256"))
    try:
        db_man.add_user(admin)
    except sqlite3.IntegrityError as err:
        print(f"_______Adding Admin err \n{err}\n __________")