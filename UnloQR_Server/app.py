try:
    from .Website import create_app
    __local__ = False
except ModuleNotFoundError:
    from Website import create_app
    __local__ = True
except ImportError:
    from Website import create_app
    __local__ = True

app, socketio, db = create_app(__local__)


if __name__ == "__main__":

    if __local__:
        print("_______RUNNNING APP LOCALLY_________")
        socketio.run(app, debug=True)

    else:
        print("_______RUNNNING APP ON HEROKU_________")
        socketio.run(app, debug=False, use_reloader=False)
