import click
from . import db
from .models import User, Device, Log, user_device
from flask.cli import with_appcontext


def create_db():
    """Creates database"""
    db.create_all()


def drop_db():
    """Cleans database"""
    db.drop_all()


def create_models_tables():
    """ Create table model in the database """
    User.__table__.create(db.engine)
    Device.__table__.create(db.engine)
    Log.__table__.create(db.engine)
    user_device.__table__.create(db.engine)

@with_appcontext
def add_admin():

    user = User.query.filter_by(email="admin@admin").first()

    print(f"Searching for the admin returned {user} ==> if not user = {not user}")

    if not user:
        user = User(email="admin@admin", name="admin", password=generate_password_hash("admin", method="sha256"))
        db.session.add(user)
        db.session.commit()


def init_app(app):
    # add multiple commands in a bulk
    for command in [create_db, drop_db, create_models_tables, add_admin]:
        app.cli.add_command(app.cli.command()(command))
