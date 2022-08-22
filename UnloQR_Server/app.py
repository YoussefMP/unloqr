try:
    from .Website import create_app
    __local__ = False
except ModuleNotFoundError:
    from Website import create_app
    __local__ = True
except ImportError:
    from Website import create_app
    __local__ = True

import click
from flask.cli import with_appcontext

app, socketio, db = create_app(__local__)


@click.command(name="create_tables")
@with_appcontext
def create_all():
    db.create_all()


if __name__ == "__main__":

    if __local__:
        print("_______RUNNNING APP LOCALLY_________")
        socketio.run(app, debug=True)

    else:
        print("_______RUNNNING APP ON HEROKU_________")
        socketio.run(app, debug=False, use_reloader=False)
